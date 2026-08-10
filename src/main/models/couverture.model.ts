import { existsSync, readFileSync, statSync } from "node:fs";
import { extname, isAbsolute, resolve, sep } from "node:path";
import log from "electron-log/main";
import * as config from "../../shared/config";
import type { CouvertureResolue, IpcResult } from "../../shared/types";
import { coversRoot } from "./preferences.model";

const MIMES: Record<string, string> = {
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
};

function extensionAcceptee(chemin: string): boolean {
  return (config.IMAGE_EXTENSIONS as readonly string[]).includes(extname(chemin).toLowerCase());
}

/** Checks the resolved path stays confined under the root, against any `..` traversal. */
function confineSous(racine: string, cible: string): boolean {
  const base = resolve(racine);
  return cible === base || cible.startsWith(base.endsWith(sep) ? base : base + sep);
}

/**
 * Covers: path resolution and image reading.
 *
 * The API stores no binary, only path strings inherited from the previous application.
 * Four cases coexist and must be tolerated without error: a path relative to a root the
 * user configures, an absolute path, a malformed path, no path at all.
 */
export const couvertureModel = {
  /**
   * Resolves a cover path and returns the image as a data URL.
   * An unresolved path is not an error: the view shows a reasoned empty state.
   */
  read(chemin: string | null): IpcResult<CouvertureResolue> {
    if (!chemin || chemin.trim().length === 0) {
      return { ok: true, data: { dataUrl: null, raison: "vide" } };
    }

    const brut = chemin.trim();
    if (!extensionAcceptee(brut)) {
      return { ok: true, data: { dataUrl: null, raison: "invalide" } };
    }

    let absolu: string;
    if (isAbsolute(brut)) {
      absolu = resolve(brut);
    } else {
      const racine = coversRoot();
      if (!racine) return { ok: true, data: { dataUrl: null, raison: "racine-absente" } };
      absolu = resolve(racine, brut);
      if (!confineSous(racine, absolu)) {
        log.warn("Chemin de couverture sortant du dossier racine, lecture refusée");
        return { ok: true, data: { dataUrl: null, raison: "invalide" } };
      }
    }

    try {
      if (!existsSync(absolu) || !statSync(absolu).isFile()) {
        return { ok: true, data: { dataUrl: null, raison: "introuvable" } };
      }
      const mime = MIMES[extname(absolu).toLowerCase()];
      const donnees = readFileSync(absolu).toString("base64");
      return { ok: true, data: { dataUrl: `data:${mime};base64,${donnees}`, raison: "ok" } };
    } catch (err) {
      log.error("Lecture d'une couverture impossible", err);
      return { ok: true, data: { dataUrl: null, raison: "introuvable" } };
    }
  },
};
