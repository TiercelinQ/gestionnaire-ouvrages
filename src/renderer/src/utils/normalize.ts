/**
 * Search normalisation, identical to the one the server applies to build
 * `recherche_normalisee`: Unicode decomposition, diacritics removal, lower case.
 * Without it, "Herbert" would not find "Hérbert" and the comparison would be wrong.
 */
export function normaliser(valeur: string): string {
  return valeur
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase()
    .trim();
}
