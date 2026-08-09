import { registerCouvertureController } from "./couverture.controller";
import { registerExportController } from "./export.controller";
import { registerNomenclatureController } from "./nomenclature.controller";
import { registerOuvrageController } from "./ouvrage.controller";
import { registerPreferencesController } from "./preferences.controller";
import { registerSessionController } from "./session.controller";

/** Enregistre tous les gestionnaires IPC. Appelé une seule fois, depuis la composition racine. */
export function registerAllControllers(): void {
  registerSessionController();
  registerOuvrageController();
  registerNomenclatureController();
  registerCouvertureController();
  registerExportController();
  registerPreferencesController();
}
