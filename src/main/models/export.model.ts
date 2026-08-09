import { writeFileSync } from "node:fs";
import type { IpcResult, OuvrageListe } from "../../shared/types";

const SEPARATEUR = ";";
const ENTETES = ["Auteur", "Titre", "Édition", "Catégorie"];
/** Sans marque d'ordre, Excel ouvre le fichier en ANSI et casse les accents. */
const BOM = "﻿";

/** Échappe une valeur au format CSV : guillemets doublés, encadrement si nécessaire. */
function echapper(valeur: string | null): string {
  const texte = valeur ?? "";
  return /[";\r\n]/.test(texte) ? `"${texte.replace(/"/g, '""')}"` : texte;
}

/**
 * Export CSV de la collection.
 *
 * Les colonnes sont celles que la liste renvoie : l'API ne fournit les trente-huit champs
 * d'un ouvrage que fiche par fiche, et exporter la collection complète coûterait
 * une requête par ouvrage.
 */
export const exportModel = {
  /** Écrit le fichier en UTF-8 avec BOM, séparateur point-virgule, ordre reçu. */
  toCsv(lignes: OuvrageListe[], chemin: string): IpcResult<string> {
    const contenu = [
      ENTETES.join(SEPARATEUR),
      ...lignes.map((ligne) =>
        [ligne.auteur, ligne.titre, ligne.edition, ligne.categorie_nom]
          .map(echapper)
          .join(SEPARATEUR),
      ),
    ].join("\r\n");

    writeFileSync(chemin, `${BOM}${contenu}`, "utf8");
    return { ok: true, data: chemin };
  },
};
