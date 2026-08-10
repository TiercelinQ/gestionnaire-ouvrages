import { app } from "electron";
import log from "electron-log/main";
import * as config from "../../shared/config";
import {
  CODE_RESEAU,
  CODE_SESSION_EXPIREE,
  CODE_TECHNIQUE,
  type ApiStatus,
  type IpcError,
  type IpcResult,
  type ToastType,
} from "../../shared/types";
import { effacerSession, lireJeton } from "./token-store";

/** Header scope, depending on the route being called. */
export type ModeEntetes =
  /** No header: `GET /v1/version`, the only exempt route. */
  | "public"
  /** Application identification only: `POST /v1/connexion`. */
  | "version"
  /** Identification plus token: every other route. */
  | "complet";

export interface OptionsRequete {
  corps?: unknown;
  mode?: ModeEntetes;
}

interface EnveloppeErreur {
  code: string;
  champ: string | null;
  message: string;
}

/** Both API waiting mechanisms surface as warnings, not as hard failures. */
const STATUTS_AVERTISSEMENT = new Set([423, 429]);

function lireEnveloppeErreur(donnees: unknown): EnveloppeErreur | null {
  if (typeof donnees !== "object" || donnees === null) return null;
  const erreur = (donnees as Record<string, unknown>).erreur;
  if (typeof erreur !== "object" || erreur === null) return null;
  const champs = erreur as Record<string, unknown>;
  if (typeof champs.code !== "string" || typeof champs.message !== "string") return null;
  return {
    code: champs.code,
    champ: typeof champs.champ === "string" ? champs.champ : null,
    message: champs.message,
  };
}

/**
 * The only network access point of the application.
 *
 * Always sets the identification headers: the server version check runs before route
 * resolution, so a missing header would produce a misleading `426` on a plain path typo.
 *
 * Every request starts from the main process: the Worker sets no CORS header and would
 * answer `426` to a browser preflight.
 */
export class ApiClient {
  private statusListener: ((statut: ApiStatus) => void) | null = null;
  private dernierEchange: string | null = null;

  /**
   * Wires the emission of the availability state.
   * The model does not reach `BrowserWindow`: the composition root hooks the send to the renderer.
   */
  setStatusListener(callback: (statut: ApiStatus) => void): void {
    this.statusListener = callback;
  }

  /** Last published state, useful when the renderer starts. */
  statutCourant(): ApiStatus {
    return { etat: this.dernierEchange ? "connecte" : "hors-ligne", dernierEchange: this.dernierEchange };
  }

  async get<T>(chemin: string, mode?: ModeEntetes): Promise<IpcResult<T>> {
    return this.requete<T>("GET", chemin, { mode });
  }

  async post<T>(chemin: string, options: OptionsRequete = {}): Promise<IpcResult<T>> {
    return this.requete<T>("POST", chemin, options);
  }

  async patch<T>(chemin: string, corps: unknown): Promise<IpcResult<T>> {
    return this.requete<T>("PATCH", chemin, { corps });
  }

  async delete<T>(chemin: string, corps?: unknown): Promise<IpcResult<T>> {
    return this.requete<T>("DELETE", chemin, { corps });
  }

  /**
   * Runs a request and converts every outcome into an `IpcResult`.
   * No exception crosses this method.
   */
  async requete<T>(
    methode: string,
    chemin: string,
    options: OptionsRequete = {},
  ): Promise<IpcResult<T>> {
    const mode = options.mode ?? "complet";
    const url = `${config.API_BASE_URL}${config.API_PREFIX}${chemin}`;

    let reponse: Response;
    try {
      reponse = await fetch(url, {
        method: methode,
        headers: this.entetes(mode, options.corps !== undefined),
        body: options.corps === undefined ? undefined : JSON.stringify(options.corps),
        signal: AbortSignal.timeout(config.API_TIMEOUT_MS),
      });
    } catch (err) {
      log.error(`Appel ${methode} ${chemin} injoignable`, err);
      this.publierStatut("hors-ligne");
      return {
        ok: false,
        error: {
          type: "danger",
          message: "Impossible de joindre le serveur.",
          description: "Vérifiez votre connexion réseau, puis réessayez.",
          code: CODE_RESEAU,
          champ: null,
        },
      };
    }

    // 204: no byte returned. Parsing that body as JSON would fail.
    if (reponse.status === 204) {
      this.publierStatut("connecte");
      return { ok: true, data: undefined as T };
    }

    const texte = await reponse.text();
    let donnees: unknown;
    try {
      donnees = JSON.parse(texte);
    } catch {
      // Plain text response: it does not come from the application code but from Cloudflare,
      // on an uncaught exception.
      log.error(`Réponse illisible sur ${methode} ${chemin} (HTTP ${reponse.status})`);
      this.publierStatut("serveur");
      return {
        ok: false,
        error: {
          type: "danger",
          message: "Le serveur a renvoyé une réponse inattendue.",
          description: `Code HTTP ${reponse.status}. Réessayez dans quelques instants.`,
          code: CODE_TECHNIQUE,
          champ: null,
        },
      };
    }

    if (reponse.ok) {
      this.publierStatut("connecte");
      return { ok: true, data: donnees as T };
    }

    const enveloppe = lireEnveloppeErreur(donnees);
    if (!enveloppe) {
      log.error(`Enveloppe d'erreur inattendue sur ${methode} ${chemin} (HTTP ${reponse.status})`);
      this.publierStatut(reponse.status >= 500 ? "serveur" : "connecte");
      return {
        ok: false,
        error: {
          type: "danger",
          message: "Le serveur a refusé la requête.",
          description: `Code HTTP ${reponse.status}.`,
          code: CODE_TECHNIQUE,
          champ: null,
        },
      };
    }

    // An expired session is no longer usable: the stored token is cleared immediately.
    if (enveloppe.code === CODE_SESSION_EXPIREE) effacerSession();

    log.warn(`Refus ${enveloppe.code} sur ${methode} ${chemin} (HTTP ${reponse.status})`);
    this.publierStatut(reponse.status >= 500 ? "serveur" : "connecte");
    return { ok: false, error: this.versIpcError(reponse.status, enveloppe) };
  }

  private entetes(mode: ModeEntetes, avecCorps: boolean): Record<string, string> {
    const entetes: Record<string, string> = {};
    if (avecCorps) entetes["Content-Type"] = "application/json";
    if (mode === "public") return entetes;

    entetes["X-App-Id"] = config.API_APP_ID;
    // The real published version, never a frozen constant: the server threshold compares it numerically.
    entetes["X-App-Version"] = app.getVersion();

    if (mode === "complet") {
      const jeton = lireJeton();
      if (jeton) entetes.Authorization = `Bearer ${jeton}`;
    }
    return entetes;
  }

  private versIpcError(statut: number, enveloppe: EnveloppeErreur): IpcError {
    const type: ToastType = STATUTS_AVERTISSEMENT.has(statut) ? "warning" : "danger";
    // The server message is written for the end user and is displayed as it comes.
    return { type, message: enveloppe.message, code: enveloppe.code, champ: enveloppe.champ };
  }

  private publierStatut(etat: ApiStatus["etat"]): void {
    if (etat === "connecte") this.dernierEchange = new Date().toISOString();
    this.statusListener?.({ etat, dernierEchange: this.dernierEchange });
  }
}

export const apiClient = new ApiClient();
