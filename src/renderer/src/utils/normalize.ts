/**
 * Normalisation de recherche, identique à celle appliquée par le serveur pour construire
 * `recherche_normalisee` : décomposition Unicode, retrait des diacritiques, minuscules.
 * Sans elle, « Herbert » ne trouverait pas « Hérbert » et la comparaison serait fausse.
 */
export function normaliser(valeur: string): string {
  return valeur
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase()
    .trim();
}
