import fr from "./fr.json";

/**
 * Interface labels, centralised in French.
 *
 * Internationalisation is not enabled (Phase 1): no i18next dependency, no language switch.
 * The labels still live outside the components, which keeps a later activation possible
 * without reworking the views.
 *
 * Typing `Cle` on the actual keys of the file makes the compilation fail on any missing
 * key: that is the integrity check of the labels.
 */
export type Cle = keyof typeof fr;

export function t(cle: Cle): string {
  return fr[cle];
}

/** Substitution variant: `{n}` and `{valeur}` are replaced by the supplied parameters. */
export function tp(cle: Cle, params: Record<string, string | number>): string {
  return Object.entries(params).reduce<string>(
    (texte, [nom, valeur]) => texte.replace(`{${nom}}`, String(valeur)),
    fr[cle],
  );
}
