import { BrowserWindow, dialog, ipcMain } from "electron";
import { IPC } from "../../shared/ipc-channels";
import { CODE_TECHNIQUE, type IpcResult, type Preferences } from "../../shared/types";
import * as preferencesModel from "../models/preferences.model";

const CLES: (keyof Preferences)[] = ["theme", "coversRoot", "windowBounds"];

function estCle(valeur: unknown): valeur is keyof Preferences {
  return typeof valeur === "string" && (CLES as string[]).includes(valeur);
}

export function registerPreferencesController(): void {
  ipcMain.handle(IPC.PREF_GET, (): IpcResult<Preferences> => ({
    ok: true,
    data: preferencesModel.getAll(),
  }));

  ipcMain.handle(IPC.PREF_SET, (_evenement, cle: unknown, valeur: unknown): IpcResult<void> => {
    if (!estCle(cle)) {
      return {
        ok: false,
        error: {
          type: "danger",
          message: "Préférence inconnue.",
          code: CODE_TECHNIQUE,
          champ: null,
        },
      };
    }
    preferencesModel.set(cle, valeur as Preferences[typeof cle]);
    return { ok: true, data: undefined };
  });

  /** Picking the cover root folder: a system dialog, hence controller side. */
  ipcMain.handle(IPC.PREF_PICK_FOLDER, async (evenement): Promise<IpcResult<string | null>> => {
    const fenetre = BrowserWindow.fromWebContents(evenement.sender);
    const options = { properties: ["openDirectory" as const] };
    const resultat = fenetre
      ? await dialog.showOpenDialog(fenetre, options)
      : await dialog.showOpenDialog(options);
    if (resultat.canceled || resultat.filePaths.length === 0) return { ok: true, data: null };

    const dossier = resultat.filePaths[0];
    preferencesModel.set("coversRoot", dossier);
    return { ok: true, data: dossier };
  });
}
