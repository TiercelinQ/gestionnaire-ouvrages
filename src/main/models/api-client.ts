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

/** Portée des en-têtes selon la route appelée. */
export type ModeEntetes =
  /** Aucun en-tête : `GET /v1/version`, seule route dispensée. */
  | "public"
  /** Identification de l'application seule : `POST /v1/connexion`. */
  | "version"
  /** Identification plus jeton : toutes les autres routes. */
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

/** Les deux mécanismes d'attente de l'API se présentent comme des avertissements, pas des échecs durs. */
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
 * Seul point d'accès réseau de l'application.
 *
 * Pose systématiquement les en-têtes d'identification : le contrôle de version du serveur
 * s'exécute avant la résolution de route, un en-tête manquant produirait donc un `426`
 * trompeur sur une simple faute de chemin.
 *
 * Toutes les requêtes partent du processus principal : le Worker ne pose aucun en-tête CORS
 * et répondrait `426` à un contrôle préalable de navigateur.
 */
export class ApiClient {
  private statusListener: ((statut: ApiStatus) => void) | null = null;
  private dernierEchange: string | null = null;

  /**
   * Branche l'émission de l'état de disponibilité.
   * Le modèle n'accède pas à `BrowserWindow` : la composition racine y raccorde l'envoi au rendu.
   */
  setStatusListener(callback: (statut: ApiStatus) => void): void {
    this.statusListener = callback;
  }

  /** Dernier état publié, utile au démarrage du rendu. */
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
   * Exécute une requête et convertit toute issue en `IpcResult`.
   * Aucune exception ne traverse cette méthode.
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

    // 204 : aucun octet renvoyé. Tenter d'analyser ce corps comme du JSON échouerait.
    if (reponse.status === 204) {
      this.publierStatut("connecte");
      return { ok: true, data: undefined as T };
    }

    const texte = await reponse.text();
    let donnees: unknown;
    try {
      donnees = JSON.parse(texte);
    } catch {
      // Réponse en texte brut : elle ne vient pas du code applicatif mais de Cloudflare,
      // sur exception non interceptée.
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

    // Une session périmée n'est plus utilisable : le jeton stocké est effacé immédiatement.
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
    // Version réelle publiée, jamais une constante figée : le seuil serveur la compare numériquement.
    entetes["X-App-Version"] = app.getVersion();

    if (mode === "complet") {
      const jeton = lireJeton();
      if (jeton) entetes.Authorization = `Bearer ${jeton}`;
    }
    return entetes;
  }

  private versIpcError(statut: number, enveloppe: EnveloppeErreur): IpcError {
    const type: ToastType = STATUTS_AVERTISSEMENT.has(statut) ? "warning" : "danger";
    // Le message serveur est rédigé pour l'utilisateur final et s'affiche tel quel.
    return { type, message: enveloppe.message, code: enveloppe.code, champ: enveloppe.champ };
  }

  private publierStatut(etat: ApiStatus["etat"]): void {
    if (etat === "connecte") this.dernierEchange = new Date().toISOString();
    this.statusListener?.({ etat, dernierEchange: this.dernierEchange });
  }
}

export const apiClient = new ApiClient();
