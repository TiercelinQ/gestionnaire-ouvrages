/** Fonctions pures de présentation. Aucune logique métier, aucun accès aux données. */

const FUSEAU = "Europe/Paris";

const FORMAT_DATE = new Intl.DateTimeFormat("fr-FR", {
  timeZone: FUSEAU,
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
});

const FORMAT_DATE_HEURE = new Intl.DateTimeFormat("fr-FR", {
  timeZone: FUSEAU,
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

const FORMAT_HEURE = new Intl.DateTimeFormat("fr-FR", {
  timeZone: FUSEAU,
  hour: "2-digit",
  minute: "2-digit",
});

const FORMAT_NOMBRE = new Intl.NumberFormat("fr-FR");

/**
 * Convertit une date ISO en temps universel vers l'heure de Paris.
 * Le serveur ne renvoie jamais d'heure locale, la conversion est à la charge du client,
 * passage été/hiver compris - géré ici par le fuseau nommé.
 */
export function formaterDate(iso: string | null | undefined): string {
  if (!iso) return "";
  const date = new Date(iso);
  return Number.isNaN(date.getTime()) ? "" : FORMAT_DATE.format(date);
}

export function formaterDateHeure(iso: string | null | undefined): string {
  if (!iso) return "";
  const date = new Date(iso);
  return Number.isNaN(date.getTime()) ? "" : FORMAT_DATE_HEURE.format(date);
}

export function formaterHeure(iso: string | null | undefined): string {
  if (!iso) return "";
  const date = new Date(iso);
  return Number.isNaN(date.getTime()) ? "" : FORMAT_HEURE.format(date);
}

export function formaterNombre(valeur: number): string {
  return FORMAT_NOMBRE.format(valeur);
}

/** Renvoie `null` pour une chaîne vide : l'API traite absence, `null` et chaîne vide à l'identique. */
export function videVersNull(valeur: string): string | null {
  const propre = valeur.trim();
  return propre.length === 0 ? null : propre;
}

/** Convertit une valeur de liste déroulante en identifiant de nomenclature. */
export function versIdentifiant(valeur: string): number | null {
  const nombre = Number.parseInt(valeur, 10);
  return Number.isInteger(nombre) && nombre > 0 ? nombre : null;
}
