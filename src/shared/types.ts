/**
 * Shared types: API DTOs, IPC result contract, surface exposed to the renderer.
 * DTO field names mirror the ones used by the API (French, underscores).
 */

// ---------------------------------------------------------------------------
// IPC result contract
// ---------------------------------------------------------------------------

export type ToastType = "success" | "info" | "warning" | "danger";

/**
 * Error surfaced to the renderer.
 * `code` and `champ` come from the API error envelope: the renderer branches its logic
 * on `code` and places `message` under the field designated by `champ`.
 */
export interface IpcError {
  type: ToastType;
  message: string;
  description?: string;
  code?: string;
  champ?: string | null;
}

export type IpcResult<T> = { ok: true; data: T } | { ok: false; error: IpcError };

/** API error codes the renderer branches a behaviour on. */
export const CODE_SESSION_EXPIREE = "session_expiree";
export const CODE_CONFLIT_VERSION = "conflit_version";
export const CODE_VERSION_INVALIDE = "entete_version_invalide";
export const CODE_VERSION_ANCIENNE = "version_trop_ancienne";
export const CODE_COMPTE_BLOQUE = "compte_bloque";
export const CODE_TROP_DE_TENTATIVES = "trop_de_tentatives";
export const CODE_RESEAU = "reseau_indisponible";
export const CODE_TECHNIQUE = "erreur_technique";

// ---------------------------------------------------------------------------
// API availability
// ---------------------------------------------------------------------------

/**
 * Availability state, derived from the last call actually made.
 * No periodic polling: the API quota is shared and unprotected.
 */
export interface ApiStatus {
  /** `connecte`: last call succeeded - `serveur`: unreadable response or 500 - `hors-ligne`: network failure. */
  etat: "connecte" | "serveur" | "hors-ligne";
  /** ISO timestamp of the last successful exchange, `null` if none since startup. */
  dernierEchange: string | null;
}

// ---------------------------------------------------------------------------
// Session
// ---------------------------------------------------------------------------

export interface Utilisateur {
  id: number;
  email: string;
  nom_affichage: string;
}

export interface Identifiants {
  email: string;
  mot_de_passe: string;
}

export interface SessionStatut {
  authentifie: boolean;
  utilisateur?: Utilisateur;
  /** True when the server answered 426: the application must show the update screen. */
  miseAJourRequise?: boolean;
  /** Matching server message, displayed as it comes. */
  message?: string;
}

export interface AppInfo {
  nom: string;
  version: string;
  /** Thresholds read from `GET /v1/version`, absent if the route did not answer. */
  versionsMinimales?: { electron: string; flutter: string };
}

// ---------------------------------------------------------------------------
// Books
// ---------------------------------------------------------------------------

/**
 * Row of `GET /v1/ouvrages`.
 *
 * The first six fields are the ones the Worker returns today. The following ones are
 * expected from the evolution described in `docs/api/evolution-liste-ouvrages.md`: they stay
 * optional so the application works before and after the deployment, the screens depending
 * on them hiding themselves while they are absent.
 */
export interface OuvrageListe {
  id: number;
  titre: string;
  auteur: string;
  edition: string | null;
  recherche_normalisee: string;
  categorie_nom: string | null;

  id_localisation?: number | null;
  localisation_nom?: string | null;
  id_periode?: number | null;
  periode_nom?: string | null;
  date_creation?: string;
  a_couverture_premiere?: boolean;
  a_couverture_quatrieme?: boolean;
}

/** Enriched fields actually present in the response, inferred from a sample of rows. */
export interface ChampsDisponibles {
  localisation: boolean;
  periode: boolean;
  dateCreation: boolean;
  couvertures: boolean;
}

/** Row of `GET /v1/corbeille`: the six list fields plus four. */
export interface OuvrageCorbeille extends OuvrageListe {
  version: number;
  supprime_le: string;
  supprime_par_nom: string | null;
  /** Computed by the server on every call. Never recomputed client-side. */
  jours_restants: number;
}

/** The twenty-nine fields the client can modify. */
export interface OuvrageInput {
  titre: string;
  sous_titre: string | null;
  auteur: string;
  auteur_2: string | null;
  titre_original: string | null;
  cycle: string | null;
  tome: string | null;
  id_illustration: number | null;
  id_categorie: number | null;
  id_genre: number | null;
  id_sous_genre: number | null;
  id_periode: number | null;
  edition: string | null;
  collection: string | null;
  edition_annee: string | null;
  edition_numero: string | null;
  edition_premiere_annee: string | null;
  isbn: string | null;
  id_reliure: number | null;
  nombre_page: string | null;
  dimension: string | null;
  id_localisation: number | null;
  localisation_details: string | null;
  resume: string | null;
  remarques: string | null;
  couverture_premiere_chemin: string | null;
  couverture_premiere_emplacement: string | null;
  couverture_quatrieme_chemin: string | null;
  couverture_quatrieme_emplacement: string | null;
}

/** Full record: the 38 columns plus the seven resolved nomenclature labels. */
export interface OuvrageFiche extends OuvrageInput {
  id: number;
  recherche_normalisee: string;
  version: number;
  supprime_le: string | null;
  supprime_par: number | null;
  date_creation: string;
  date_modification: string;
  cree_par: number;
  modifie_par: number;
  categorie_nom: string | null;
  genre_nom: string | null;
  sous_genre_nom: string | null;
  illustration_nom: string | null;
  periode_nom: string | null;
  reliure_nom: string | null;
  localisation_nom: string | null;
}

/** Body of an update: the whole record plus the version read when loading it. */
export interface OuvrageUpdateInput extends OuvrageInput {
  version: number;
}

export interface EntreeHistorique {
  id: number;
  date_action: string;
  auteur: string;
  /** The only value the server does not translate. */
  action: "creation" | "modification" | "suppression" | "restauration";
  champ: string | null;
  /** Display string, never an enumerated value. */
  champ_libelle: string | null;
  ancienne_valeur: string | null;
  nouvelle_valeur: string | null;
}

// ---------------------------------------------------------------------------
// Nomenclatures
// ---------------------------------------------------------------------------

/** URL segments of the seven resources. The segment uses a hyphen, the JSON key an underscore. */
export const RESSOURCES_NOMENCLATURE = [
  "categories",
  "genres",
  "sous-genres",
  "illustrations",
  "localisations",
  "periodes",
  "reliures",
] as const;

export type RessourceNomenclature = (typeof RESSOURCES_NOMENCLATURE)[number];

export interface Nomenclature {
  id: number;
  nom: string;
}

export interface Genre extends Nomenclature {
  id_categorie: number;
}

export interface SousGenre extends Nomenclature {
  id_genre: number;
}

export interface Nomenclatures {
  categories: Nomenclature[];
  genres: Genre[];
  sous_genres: SousGenre[];
  illustrations: Nomenclature[];
  localisations: Nomenclature[];
  periodes: Nomenclature[];
  reliures: Nomenclature[];
}

/** Creation or rename body. The parent key only concerns genres and sub-genres. */
export interface NomenclatureInput {
  nom: string;
  id_categorie?: number;
  id_genre?: number;
}

// ---------------------------------------------------------------------------
// Covers
// ---------------------------------------------------------------------------

/**
 * Result of resolving a cover path.
 * The four cases of the existing set are tolerated without error: relative, absolute,
 * malformed, absent.
 */
export interface CouvertureResolue {
  dataUrl: string | null;
  raison: "ok" | "vide" | "racine-absente" | "introuvable" | "invalide";
}

// ---------------------------------------------------------------------------
// Preferences
// ---------------------------------------------------------------------------

export type Theme = "light" | "dark";

export interface WindowBounds {
  width: number;
  height: number;
  x?: number;
  y?: number;
}

export interface Preferences {
  theme: Theme | null;
  /** Root folder used to resolve relative cover paths. */
  coversRoot: string | null;
  windowBounds: WindowBounds | null;
}

// ---------------------------------------------------------------------------
// Surface exposed to the renderer by the preload
// ---------------------------------------------------------------------------

export interface WindowApi {
  sessionStatus(): Promise<IpcResult<SessionStatut>>;
  sessionLogin(identifiants: Identifiants): Promise<IpcResult<Utilisateur>>;
  sessionLogout(): Promise<IpcResult<void>>;
  appInfo(): Promise<IpcResult<AppInfo>>;

  ouvrageList(): Promise<IpcResult<OuvrageListe[]>>;
  ouvrageGet(id: number): Promise<IpcResult<OuvrageFiche>>;
  ouvrageCreate(input: OuvrageInput): Promise<IpcResult<OuvrageFiche>>;
  ouvrageUpdate(id: number, input: OuvrageUpdateInput): Promise<IpcResult<OuvrageFiche>>;
  ouvrageDelete(id: number, version: number): Promise<IpcResult<void>>;
  ouvrageRestore(id: number): Promise<IpcResult<OuvrageFiche>>;
  ouvrageHistory(id: number): Promise<IpcResult<EntreeHistorique[]>>;
  corbeilleList(): Promise<IpcResult<OuvrageCorbeille[]>>;

  nomenclatureList(): Promise<IpcResult<Nomenclatures>>;
  nomenclatureCreate(
    ressource: RessourceNomenclature,
    input: NomenclatureInput,
  ): Promise<IpcResult<Nomenclature>>;
  nomenclatureUpdate(
    ressource: RessourceNomenclature,
    id: number,
    input: NomenclatureInput,
  ): Promise<IpcResult<Nomenclature>>;
  nomenclatureDelete(ressource: RessourceNomenclature, id: number): Promise<IpcResult<void>>;

  couverturePick(): Promise<IpcResult<string | null>>;
  couvertureRead(chemin: string | null): Promise<IpcResult<CouvertureResolue>>;

  exportCsv(lignes: OuvrageListe[]): Promise<IpcResult<string | null>>;

  getPreferences(): Promise<IpcResult<Preferences>>;
  setPreference<K extends keyof Preferences>(
    cle: K,
    valeur: Preferences[K],
  ): Promise<IpcResult<void>>;
  pickCoversFolder(): Promise<IpcResult<string | null>>;

  /** Subscribes to the API availability state. Returns the unsubscribe function. */
  onApiStatus(callback: (statut: ApiStatus) => void): () => void;
}

declare global {
  interface Window {
    api: WindowApi;
  }
}

// ---------------------------------------------------------------------------
// Type guards - used by the controllers to validate IPC inputs
// ---------------------------------------------------------------------------

export function estChaineNonVide(valeur: unknown): valeur is string {
  return typeof valeur === "string" && valeur.trim().length > 0;
}

export function estEntierPositif(valeur: unknown): valeur is number {
  return typeof valeur === "number" && Number.isInteger(valeur) && valeur > 0;
}

export function estRessourceNomenclature(valeur: unknown): valeur is RessourceNomenclature {
  return (
    typeof valeur === "string" && (RESSOURCES_NOMENCLATURE as readonly string[]).includes(valeur)
  );
}

/** Checks the presence of the only two mandatory fields of a book. */
export function estOuvrageInput(valeur: unknown): valeur is OuvrageInput {
  if (typeof valeur !== "object" || valeur === null) return false;
  const candidat = valeur as Record<string, unknown>;
  return estChaineNonVide(candidat.titre) && estChaineNonVide(candidat.auteur);
}

export function estNomenclatureInput(valeur: unknown): valeur is NomenclatureInput {
  if (typeof valeur !== "object" || valeur === null) return false;
  return estChaineNonVide((valeur as Record<string, unknown>).nom);
}
