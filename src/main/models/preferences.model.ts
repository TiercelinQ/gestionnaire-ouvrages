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

/** Current preferences, merged with the default values. */
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
    // Corrupted file: fall back to the default values rather than block startup.
    log.error("Lecture des préférences impossible", err);
    cache = { ...DEFAUTS };
  }
  return cache;
}

/** Writes one preference and persists the whole set. */
export function set<K extends keyof Preferences>(cle: K, valeur: Preferences[K]): void {
  const preferences = { ...getAll(), [cle]: valeur };
  cache = preferences;
  try {
    writeFileSync(fichier(), JSON.stringify(preferences, null, 2), "utf8");
  } catch (err) {
    log.error("Écriture des préférences impossible", err);
  }
}

/** Root folder used to resolve relative cover paths. */
export function coversRoot(): string | null {
  return getAll().coversRoot;
}
