/** Pure presentation functions. No business logic, no data access. */

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
 * Converts an ISO date in universal time to Paris time.
 * The server never returns a local time, the conversion is the client's job, daylight
 * saving included - handled here by the named time zone.
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

/** Returns `null` for an empty string: the API treats absence, `null` and empty string alike. */
export function videVersNull(valeur: string): string | null {
  const propre = valeur.trim();
  return propre.length === 0 ? null : propre;
}

/** Converts a dropdown value into a nomenclature identifier. */
export function versIdentifiant(valeur: string): number | null {
  const nombre = Number.parseInt(valeur, 10);
  return Number.isInteger(nombre) && nombre > 0 ? nombre : null;
}
