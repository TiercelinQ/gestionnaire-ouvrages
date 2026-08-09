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

/** Vérifie que le chemin résolu reste confiné sous la racine, contre toute remontée `..`. */
function confineSous(racine: string, cible: string): boolean {
  const base = resolve(racine);
  return cible === base || cible.startsWith(base.endsWith(sep) ? base : base + sep);
}

/**
 * Couvertures : résolution des chemins et lecture des images.
 *
 * L'API ne stocke aucun binaire, seulement des chaînes de chemin héritées de l'application
 * précédente. Quatre cas coexistent et doivent être tolérés sans erreur : chemin relatif à
 * une racine que l'utilisateur configure, chemin absolu, chemin malformé, absence de chemin.
 */
export const couvertureModel = {
  /**
   * Résout un chemin de couverture et renvoie l'image en data URL.
   * Un chemin non résolu n'est pas une erreur : la vue affiche un état vide motivé.
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
