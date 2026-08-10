import { BrowserWindow, dialog, ipcMain } from "electron";
import log from "electron-log/main";
import * as config from "../../shared/config";
import { IPC } from "../../shared/ipc-channels";
import { CODE_TECHNIQUE, type CouvertureResolue, type IpcResult } from "../../shared/types";
import { couvertureModel } from "../models/couverture.model";

export function registerCouvertureController(): void {
  /** The file picker is an interface API: it lives in the controller, not in the model. */
  ipcMain.handle(IPC.COUVERTURE_PICK, async (evenement): Promise<IpcResult<string | null>> => {
    const fenetre = BrowserWindow.fromWebContents(evenement.sender);
    const options = {
      properties: ["openFile" as const],
      filters: [
        {
          name: "Images",
          extensions: config.IMAGE_EXTENSIONS.map((extension) => extension.replace(".", "")),
        },
      ],
    };
    const resultat = fenetre
      ? await dialog.showOpenDialog(fenetre, options)
      : await dialog.showOpenDialog(options);
    return { ok: true, data: resultat.canceled ? null : (resultat.filePaths[0] ?? null) };
  });

  ipcMain.handle(IPC.COUVERTURE_READ, (_evenement, chemin: unknown): IpcResult<CouvertureResolue> => {
    if (chemin !== null && typeof chemin !== "string") {
      log.warn("Chemin de couverture de type inattendu");
      return {
        ok: false,
        error: {
          type: "danger",
          message: "Chemin de couverture invalide.",
          code: CODE_TECHNIQUE,
          champ: null,
        },
      };
    }
    return couvertureModel.read(chemin);
  });
}
