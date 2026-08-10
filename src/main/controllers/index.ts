import { registerCouvertureController } from "./couverture.controller";
import { registerExportController } from "./export.controller";
import { registerNomenclatureController } from "./nomenclature.controller";
import { registerOuvrageController } from "./ouvrage.controller";
import { registerPreferencesController } from "./preferences.controller";
import { registerSessionController } from "./session.controller";

/** Registers every IPC handler. Called once, from the composition root. */
export function registerAllControllers(): void {
  registerSessionController();
  registerOuvrageController();
  registerNomenclatureController();
  registerCouvertureController();
  registerExportController();
  registerPreferencesController();
}
