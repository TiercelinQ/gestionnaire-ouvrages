import { ipcMain } from "electron";
import { IPC } from "../../shared/ipc-channels";
import {
  CODE_TECHNIQUE,
  estEntierPositif,
  estOuvrageInput,
  type EntreeHistorique,
  type IpcResult,
  type OuvrageCorbeille,
  type OuvrageFiche,
  type OuvrageListe,
  type OuvrageUpdateInput,
} from "../../shared/types";
import { ouvrageModel } from "../models/ouvrage.model";

function refus(message: string, champ: string | null = null): IpcResult<never> {
  return { ok: false, error: { type: "danger", message, code: CODE_TECHNIQUE, champ } };
}

/** La version doit être numérique : le serveur refuse une chaîne, même bien formée. */
function versionValide(valeur: unknown): valeur is number {
  return typeof valeur === "number" && Number.isFinite(valeur);
}

export function registerOuvrageController(): void {
  ipcMain.handle(IPC.OUVRAGE_LIST, (): Promise<IpcResult<OuvrageListe[]>> => ouvrageModel.list());

  ipcMain.handle(IPC.CORBEILLE_LIST, (): Promise<IpcResult<OuvrageCorbeille[]>> => ouvrageModel.trash());

  ipcMain.handle(
    IPC.OUVRAGE_GET,
    (_evenement, id: unknown): Promise<IpcResult<OuvrageFiche>> | IpcResult<never> =>
      estEntierPositif(id) ? ouvrageModel.get(id) : refus("Identifiant d'ouvrage invalide."),
  );

  ipcMain.handle(
    IPC.OUVRAGE_CREATE,
    (_evenement, charge: unknown): Promise<IpcResult<OuvrageFiche>> | IpcResult<never> => {
      if (!estOuvrageInput(charge)) return refus("Le titre et l'auteur sont obligatoires.", "titre");
      return ouvrageModel.create(charge);
    },
  );

  ipcMain.handle(
    IPC.OUVRAGE_UPDATE,
    (
      _evenement,
      id: unknown,
      charge: unknown,
    ): Promise<IpcResult<OuvrageFiche>> | IpcResult<never> => {
      if (!estEntierPositif(id)) return refus("Identifiant d'ouvrage invalide.");
      if (!estOuvrageInput(charge)) return refus("Le titre et l'auteur sont obligatoires.", "titre");
      const version = (charge as unknown as OuvrageUpdateInput).version;
      if (!versionValide(version)) return refus("La version est obligatoire.", "version");
      return ouvrageModel.update(id, charge as OuvrageUpdateInput);
    },
  );

  ipcMain.handle(
    IPC.OUVRAGE_DELETE,
    (_evenement, id: unknown, version: unknown): Promise<IpcResult<void>> | IpcResult<never> => {
      if (!estEntierPositif(id)) return refus("Identifiant d'ouvrage invalide.");
      if (!versionValide(version)) return refus("La version est obligatoire.", "version");
      return ouvrageModel.remove(id, version);
    },
  );

  ipcMain.handle(
    IPC.OUVRAGE_RESTORE,
    (_evenement, id: unknown): Promise<IpcResult<OuvrageFiche>> | IpcResult<never> =>
      estEntierPositif(id) ? ouvrageModel.restore(id) : refus("Identifiant d'ouvrage invalide."),
  );

  ipcMain.handle(
    IPC.OUVRAGE_HISTORY,
    (_evenement, id: unknown): Promise<IpcResult<EntreeHistorique[]>> | IpcResult<never> =>
      estEntierPositif(id) ? ouvrageModel.history(id) : refus("Identifiant d'ouvrage invalide."),
  );
}
