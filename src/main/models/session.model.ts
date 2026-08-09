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
 * Session applicative : connexion, vérification au démarrage, déconnexion.
 * Le jeton reste dans le processus principal, il n'est jamais renvoyé au rendu.
 */
export const sessionModel = {
  /**
   * État de session au démarrage. Vérifie qu'un jeton stocké est toujours accepté :
   * la durée de vie est fixe et l'usage ne la prolonge pas.
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
      // Le jeton a déjà été effacé par le client HTTP.
      return { ok: true, data: { authentifie: false } };
    }

    // Serveur injoignable : la session locale est conservée, l'utilisateur retente plus tard.
    return { ok: false, error: resultat.error };
  },

  /**
   * Ouvre une session. Le mot de passe n'est pas conservé au-delà de cet appel
   * et le corps de la requête n'est jamais journalisé.
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

  /** Supprime la session côté serveur, puis efface le jeton local dans tous les cas. */
  async logout(): Promise<IpcResult<void>> {
    const resultat = await apiClient.post<void>("/deconnexion");
    effacerSession();
    log.info("Session fermée");
    // Un jeton déjà invalide reçoit 401 avant d'atteindre la route : la déconnexion locale suffit.
    return resultat.ok || resultat.error.code === CODE_SESSION_EXPIREE
      ? { ok: true, data: undefined }
      : resultat;
  },

  /**
   * Identité de l'application et seuils de version du serveur.
   * `GET /v1/version` est publique : c'est la source machine des seuils, y compris
   * pour un client refusé qui doit apprendre pourquoi il l'est.
   */
  async appInfo(): Promise<IpcResult<AppInfo>> {
    const info: AppInfo = { nom: config.APP_DISPLAY_NAME, version: app.getVersion() };
    const resultat = await apiClient.get<ReponseVersion>("/version", "public");
    if (resultat.ok) info.versionsMinimales = resultat.data.versions_minimales;
    return { ok: true, data: info };
  },
};
