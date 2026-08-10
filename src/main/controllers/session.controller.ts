import { ipcMain } from "electron";
import log from "electron-log/main";
import { IPC } from "../../shared/ipc-channels";
import {
  CODE_TECHNIQUE,
  estChaineNonVide,
  type AppInfo,
  type Identifiants,
  type IpcResult,
  type SessionStatut,
  type Utilisateur,
} from "../../shared/types";
import { ChiffrementIndisponibleError } from "../models/errors";
import { sessionModel } from "../models/session.model";

function validerIdentifiants(charge: unknown): Identifiants | null {
  if (typeof charge !== "object" || charge === null) return null;
  const candidat = charge as Record<string, unknown>;
  if (!estChaineNonVide(candidat.email) || !estChaineNonVide(candidat.mot_de_passe)) return null;
  return { email: candidat.email, mot_de_passe: candidat.mot_de_passe };
}

export function registerSessionController(): void {
  ipcMain.handle(IPC.SESSION_STATUS, (): Promise<IpcResult<SessionStatut>> =>
    sessionModel.status(),
  );

  ipcMain.handle(
    IPC.SESSION_LOGIN,
    async (_evenement, charge: unknown): Promise<IpcResult<Utilisateur>> => {
      const identifiants = validerIdentifiants(charge);
      if (!identifiants) {
        return {
          ok: false,
          error: {
            type: "danger",
            message: "Adresse e-mail et mot de passe sont requis.",
            code: CODE_TECHNIQUE,
            champ: "email",
          },
        };
      }
      try {
        return await sessionModel.login(identifiants);
      } catch (err) {
        // The only exception possible here: the system provides no encryption,
        // and the token must never be written in clear text.
        if (err instanceof ChiffrementIndisponibleError) {
          log.error("Session non conservée", err.message);
          return {
            ok: false,
            error: {
              type: "danger",
              message: err.message,
              description: "Vérifiez que votre session Windows autorise le stockage protégé.",
              code: CODE_TECHNIQUE,
              champ: null,
            },
          };
        }
        throw err;
      }
    },
  );

  ipcMain.handle(IPC.SESSION_LOGOUT, (): Promise<IpcResult<void>> => sessionModel.logout());

  ipcMain.handle(IPC.APP_INFO, (): Promise<IpcResult<AppInfo>> => sessionModel.appInfo());
}
