import fr from "./fr.json";

/**
 * Libellés de l'interface, centralisés en français.
 *
 * L'internationalisation n'est pas activée (Phase 1) : pas de dépendance i18next, pas de
 * bascule de langue. Les libellés restent néanmoins hors des composants, ce qui rend
 * l'activation ultérieure possible sans reprendre les vues.
 *
 * Le typage de `Cle` sur les clés réelles du fichier fait échouer la compilation
 * sur toute clé absente : c'est la vérification d'intégrité des libellés.
 */
export type Cle = keyof typeof fr;

export function t(cle: Cle): string {
  return fr[cle];
}

/** Variante à substitution : `{n}` et `{valeur}` sont remplacés par les paramètres fournis. */
export function tp(cle: Cle, params: Record<string, string | number>): string {
  return Object.entries(params).reduce<string>(
    (texte, [nom, valeur]) => texte.replace(`{${nom}}`, String(valeur)),
    fr[cle],
  );
}
