import { writeFileSync } from "node:fs";
import type { IpcResult, OuvrageListe } from "../../shared/types";

const SEPARATEUR = ";";
const ENTETES = ["Auteur", "Titre", "Édition", "Catégorie"];
/** Without a byte order mark, Excel opens the file as ANSI and breaks the accents. */
const BOM = "﻿";

/** Escapes a value in CSV format: doubled quotes, wrapped when needed. */
function echapper(valeur: string | null): string {
  const texte = valeur ?? "";
  return /[";\r\n]/.test(texte) ? `"${texte.replace(/"/g, '""')}"` : texte;
}

/**
 * CSV export of the collection.
 *
 * The columns are the ones the list returns: the API only provides the thirty-eight fields
 * of a book record by record, and exporting the full collection would cost one request
 * per book.
 */
export const exportModel = {
  /** Writes the file in UTF-8 with BOM, semicolon separator, in the order received. */
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
