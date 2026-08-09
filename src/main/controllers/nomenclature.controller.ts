import { ipcMain } from "electron";
import { IPC } from "../../shared/ipc-channels";
import {
  CODE_TECHNIQUE,
  estEntierPositif,
  estNomenclatureInput,
  estRessourceNomenclature,
  type IpcResult,
  type Nomenclature,
  type NomenclatureInput,
  type Nomenclatures,
} from "../../shared/types";
import { nomenclatureModel } from "../models/nomenclature.model";

function refus(message: string, champ: string | null = null): IpcResult<never> {
  return { ok: false, error: { type: "danger", message, code: CODE_TECHNIQUE, champ } };
}

/**
 * Vérifie la clé de rattachement des deux ressources hiérarchiques.
 * Le serveur exige un type numérique et n'accepte pas une chaîne.
 */
function rattachementValide(ressource: string, input: NomenclatureInput): boolean {
  if (ressource === "genres") return estEntierPositif(input.id_categorie);
  if (ressource === "sous-genres") return estEntierPositif(input.id_genre);
  return true;
}

export function registerNomenclatureController(): void {
  ipcMain.handle(IPC.NOMENCLATURE_LIST, (): Promise<IpcResult<Nomenclatures>> =>
    nomenclatureModel.list(),
  );

  ipcMain.handle(
    IPC.NOMENCLATURE_CREATE,
    (
      _evenement,
      ressource: unknown,
      charge: unknown,
    ): Promise<IpcResult<Nomenclature>> | IpcResult<never> => {
      if (!estRessourceNomenclature(ressource)) return refus("Ressource inconnue.");
      if (!estNomenclatureInput(charge)) return refus("Le nom est obligatoire.", "nom");
      if (!rattachementValide(ressource, charge)) {
        return refus(
          ressource === "genres" ? "La catégorie est obligatoire" : "Le genre est obligatoire",
          ressource === "genres" ? "id_categorie" : "id_genre",
        );
      }
      return nomenclatureModel.create(ressource, charge);
    },
  );

  ipcMain.handle(
    IPC.NOMENCLATURE_UPDATE,
    (
      _evenement,
      ressource: unknown,
      id: unknown,
      charge: unknown,
    ): Promise<IpcResult<Nomenclature>> | IpcResult<never> => {
      if (!estRessourceNomenclature(ressource)) return refus("Ressource inconnue.");
      if (!estEntierPositif(id)) return refus("Identifiant invalide.");
      if (!estNomenclatureInput(charge)) return refus("Le nom est obligatoire.", "nom");
      return nomenclatureModel.update(ressource, id, charge);
    },
  );

  ipcMain.handle(
    IPC.NOMENCLATURE_DELETE,
    (_evenement, ressource: unknown, id: unknown): Promise<IpcResult<void>> | IpcResult<never> => {
      if (!estRessourceNomenclature(ressource)) return refus("Ressource inconnue.");
      if (!estEntierPositif(id)) return refus("Identifiant invalide.");
      return nomenclatureModel.remove(ressource, id);
    },
  );
}
