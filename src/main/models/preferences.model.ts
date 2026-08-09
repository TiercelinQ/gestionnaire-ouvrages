import { app } from "electron";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import log from "electron-log/main";
import * as config from "../../shared/config";
import type { Preferences } from "../../shared/types";

const DEFAUTS: Preferences = {
  theme: null,
  coversRoot: null,
  windowBounds: null,
};

let cache: Preferences | null = null;

function fichier(): string {
  return join(app.getPath("userData"), config.PREFERENCES_FILENAME);
}

/** Préférences courantes, fusionnées avec les valeurs par défaut. */
export function getAll(): Preferences {
  if (cache) return cache;

  const chemin = fichier();
  if (!existsSync(chemin)) {
    cache = { ...DEFAUTS };
    return cache;
  }

  try {
    const contenu = JSON.parse(readFileSync(chemin, "utf8")) as Partial<Preferences>;
    cache = { ...DEFAUTS, ...contenu };
  } catch (err) {
    // Fichier corrompu : on repart des valeurs par défaut plutôt que de bloquer le démarrage.
    log.error("Lecture des préférences impossible", err);
    cache = { ...DEFAUTS };
  }
  return cache;
}

/** Écrit une préférence et persiste l'ensemble. */
export function set<K extends keyof Preferences>(cle: K, valeur: Preferences[K]): void {
  const preferences = { ...getAll(), [cle]: valeur };
  cache = preferences;
  try {
    writeFileSync(fichier(), JSON.stringify(preferences, null, 2), "utf8");
  } catch (err) {
    log.error("Écriture des préférences impossible", err);
  }
}

/** Dossier racine servant à résoudre les chemins de couverture relatifs. */
export function coversRoot(): string | null {
  return getAll().coversRoot;
}
