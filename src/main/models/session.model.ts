import { app } from "electron";
import { hostname } from "node:os";
import log from "electron-log/main";
import * as config from "../../shared/config";
import {
  CODE_SESSION_EXPIREE,
  CODE_VERSION_ANCIENNE,
  CODE_VERSION_INVALIDE,
  type AppInfo,
  type Identifiants,
  type IpcResult,
  type SessionStatut,
  type Utilisateur,
} from "../../shared/types";
import { apiClient } from "./api-client";
import { ecrireSession, effacerSession, lireSession } from "./token-store";

interface ReponseConnexion {
  jeton: string;
  expire_le: string;
  utilisateur: Utilisateur;
}

interface ReponseVersion {
  versions_minimales: { electron: string; flutter: string };
}

function estRefusDeVersion(code: string | undefined): boolean {
  return code === CODE_VERSION_INVALIDE || code === CODE_VERSION_ANCIENNE;
}

/**
 * Application session: sign-in, startup check, sign-out.
 * The token stays in the main process, it is never returned to the renderer.
 */
export const sessionModel = {
  /**
   * Session state at startup. Checks a stored token is still accepted: the lifetime is
   * fixed and using it does not extend it.
   */
  async status(): Promise<IpcResult<SessionStatut>> {
    if (!lireSession()) return { ok: true, data: { authentifie: false } };

    const resultat = await apiClient.get<Utilisateur>("/moi");
    if (resultat.ok) return { ok: true, data: { authentifie: true, utilisateur: resultat.data } };

    if (estRefusDeVersion(resultat.error.code)) {
      return {
        ok: true,
        data: { authentifie: false, miseAJourRequise: true, message: resultat.error.message },
      };
    }

    if (resultat.error.code === CODE_SESSION_EXPIREE) {
      // The token has already been cleared by the HTTP client.
      return { ok: true, data: { authentifie: false } };
    }

    // Server unreachable: the local session is kept, the user retries later.
    return { ok: false, error: resultat.error };
  },

  /**
   * Opens a session. The password is not kept beyond this call and the request body is
   * never logged.
   */
  async login(identifiants: Identifiants): Promise<IpcResult<Utilisateur>> {
    const resultat = await apiClient.post<ReponseConnexion>("/connexion", {
      mode: "version",
      corps: {
        email: identifiants.email,
        mot_de_passe: identifiants.mot_de_passe,
        appareil: hostname(),
      },
    });
    if (!resultat.ok) return resultat;

    ecrireSession({
      jeton: resultat.data.jeton,
      expire_le: resultat.data.expire_le,
      utilisateur: resultat.data.utilisateur,
    });
    log.info(`Session ouverte pour ${resultat.data.utilisateur.nom_affichage}`);
    return { ok: true, data: resultat.data.utilisateur };
  },

  /** Deletes the session server side, then clears the local token in every case. */
  async logout(): Promise<IpcResult<void>> {
    const resultat = await apiClient.post<void>("/deconnexion");
    effacerSession();
    log.info("Session fermée");
    // An already invalid token gets a 401 before reaching the route: signing out locally is enough.
    return resultat.ok || resultat.error.code === CODE_SESSION_EXPIREE
      ? { ok: true, data: undefined }
      : resultat;
  },

  /**
   * Application identity and server version thresholds.
   * `GET /v1/version` is public: it is the machine source of the thresholds, including for
   * a rejected client that has to learn why it was rejected.
   */
  async appInfo(): Promise<IpcResult<AppInfo>> {
    const info: AppInfo = { nom: config.APP_DISPLAY_NAME, version: app.getVersion() };
    const resultat = await apiClient.get<ReponseVersion>("/version", "public");
    if (resultat.ok) info.versionsMinimales = resultat.data.versions_minimales;
    return { ok: true, data: info };
  },
};
