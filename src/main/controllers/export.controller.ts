import { BrowserWindow, dialog, ipcMain } from "electron";
import log from "electron-log/main";
import * as config from "../../shared/config";
import { IPC } from "../../shared/ipc-channels";
import { CODE_TECHNIQUE, type IpcResult, type OuvrageListe } from "../../shared/types";
import { exportModel } from "../models/export.model";

function estListe(charge: unknown): charge is OuvrageListe[] {
  return (
    Array.isArray(charge) && charge.every((ligne) => typeof ligne === "object" && ligne !== null)
  );
}

export function registerExportController(): void {
  ipcMain.handle(
    IPC.EXPORT_CSV,
    async (evenement, charge: unknown): Promise<IpcResult<string | null>> => {
      if (!estListe(charge)) {
        return {
          ok: false,
          error: {
            type: "danger",
            message: "Données d'export invalides.",
            code: CODE_TECHNIQUE,
            champ: null,
          },
        };
      }

      const fenetre = BrowserWindow.fromWebContents(evenement.sender);
      const options = {
        defaultPath: `${config.APP_NAME}.csv`,
        filters: [{ name: "CSV", extensions: ["csv"] }],
      };
      const cible = fenetre
        ? await dialog.showSaveDialog(fenetre, options)
        : await dialog.showSaveDialog(options);
      if (cible.canceled || !cible.filePath) return { ok: true, data: null };

      try {
        return exportModel.toCsv(charge, cible.filePath);
      } catch (err) {
        log.error("Écriture du fichier CSV impossible", err);
        return {
          ok: false,
          error: {
            type: "danger",
            message: "Le fichier n'a pas pu être écrit.",
            description: "Vérifiez que le dossier est accessible en écriture.",
            code: CODE_TECHNIQUE,
            champ: null,
          },
        };
      }
    },
  );
}
