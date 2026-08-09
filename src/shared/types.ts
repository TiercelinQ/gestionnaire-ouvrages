/**
 * Types partagés : DTO de l'API, contrat de résultat IPC, surface exposée au rendu.
 * Les noms de champs des DTO reprennent ceux de l'API (français, tirets bas).
 */

// ---------------------------------------------------------------------------
// Contrat de résultat IPC
// ---------------------------------------------------------------------------

export type ToastType = "success" | "info" | "warning" | "danger";

/**
 * Erreur remontée au rendu.
 * `code` et `champ` sont repris de l'enveloppe d'erreur de l'API : le rendu branche
 * sa logique sur `code` et positionne `message` sous le champ désigné par `champ`.
 */
export interface IpcError {
  type: ToastType;
  message: string;
  description?: string;
  code?: string;
  champ?: string | null;
}

export type IpcResult<T> = { ok: true; data: T } | { ok: false; error: IpcError };

/** Codes d'erreur de l'API sur lesquels le rendu branche un comportement. */
export const CODE_SESSION_EXPIREE = "session_expiree";
export const CODE_CONFLIT_VERSION = "conflit_version";
export const CODE_VERSION_INVALIDE = "entete_version_invalide";
export const CODE_VERSION_ANCIENNE = "version_trop_ancienne";
export const CODE_COMPTE_BLOQUE = "compte_bloque";
export const CODE_TROP_DE_TENTATIVES = "trop_de_tentatives";
export const CODE_RESEAU = "reseau_indisponible";
export const CODE_TECHNIQUE = "erreur_technique";

// ---------------------------------------------------------------------------
// Disponibilité de l'API
// ---------------------------------------------------------------------------

/**
 * État de disponibilité, dérivé du dernier appel réellement effectué.
 * Aucun sondage périodique : le quota de l'API est partagé et non protégé.
 */
export interface ApiStatus {
  /** `connecte` : dernier appel abouti · `serveur` : réponse illisible ou 500 · `hors-ligne` : échec réseau. */
  etat: "connecte" | "serveur" | "hors-ligne";
  /** Horodatage ISO du dernier échange abouti, `null` si aucun depuis le démarrage. */
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
  /** Vrai quand le serveur a répondu 426 : l'application doit afficher l'écran de mise à jour. */
  miseAJourRequise?: boolean;
  /** Message serveur associé, affiché tel quel. */
  message?: string;
}

export interface AppInfo {
  nom: string;
  version: string;
  /** Seuils lus sur `GET /v1/version`, absents si la route n'a pas répondu. */
  versionsMinimales?: { electron: string; flutter: string };
}

// ---------------------------------------------------------------------------
// Ouvrages
// ---------------------------------------------------------------------------

/**
 * Ligne de `GET /v1/ouvrages`.
 *
 * Les six premiers champs sont ceux que le Worker renvoie aujourd'hui. Les suivants sont
 * attendus de l'évolution décrite dans `docs/api/evolution-liste-ouvrages.md` : ils restent
 * optionnels pour que l'application fonctionne avant comme après le déploiement, les écrans
 * qui en dépendent se masquant tant qu'ils sont absents.
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

/** Champs enrichis effectivement présents dans la réponse, déduits d'un échantillon de lignes. */
export interface ChampsDisponibles {
  localisation: boolean;
  periode: boolean;
  dateCreation: boolean;
  couvertures: boolean;
}

/** Ligne de `GET /v1/corbeille` : les six champs de la liste plus quatre. */
export interface OuvrageCorbeille extends OuvrageListe {
  version: number;
  supprime_le: string;
  supprime_par_nom: string | null;
  /** Calculé par le serveur à chaque appel. Jamais recalculé côté client. */
  jours_restants: number;
}

/** Les vingt-neuf champs modifiables par le client. */
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

/** Fiche complète : les 38 colonnes plus les sept libellés de nomenclature résolus. */
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

/** Corps d'une modification : la fiche entière plus la version lue au chargement. */
export interface OuvrageUpdateInput extends OuvrageInput {
  version: number;
}

export interface EntreeHistorique {
  id: number;
  date_action: string;
  auteur: string;
  /** Seule valeur non traduite par le serveur. */
  action: "creation" | "modification" | "suppression" | "restauration";
  champ: string | null;
  /** Chaîne d'affichage, jamais une valeur énumérée. */
  champ_libelle: string | null;
  ancienne_valeur: string | null;
  nouvelle_valeur: string | null;
}

// ---------------------------------------------------------------------------
// Nomenclatures
// ---------------------------------------------------------------------------

/** Segments d'URL des sept ressources. Le segment emploie le trait d'union, la clé JSON le tiret bas. */
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

/** Corps de création ou de renommage. La clé de rattachement ne concerne que genres et sous-genres. */
export interface NomenclatureInput {
  nom: string;
  id_categorie?: number;
  id_genre?: number;
}

// ---------------------------------------------------------------------------
// Couvertures
// ---------------------------------------------------------------------------

/**
 * Résultat de résolution d'un chemin de couverture.
 * Les quatre cas du parc existant sont tolérés sans erreur : relatif, absolu, malformé, absent.
 */
export interface CouvertureResolue {
  dataUrl: string | null;
  raison: "ok" | "vide" | "racine-absente" | "introuvable" | "invalide";
}

// ---------------------------------------------------------------------------
// Préférences
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
  /** Dossier racine servant à résoudre les chemins de couverture relatifs. */
  coversRoot: string | null;
  windowBounds: WindowBounds | null;
}

// ---------------------------------------------------------------------------
// Surface exposée au rendu par le preload
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

  /** Abonnement à l'état de disponibilité de l'API. Renvoie la fonction de désabonnement. */
  onApiStatus(callback: (statut: ApiStatus) => void): () => void;
}

declare global {
  interface Window {
    api: WindowApi;
  }
}

// ---------------------------------------------------------------------------
// Gardes de type — utilisées par les contrôleurs pour valider les entrées IPC
// ---------------------------------------------------------------------------

export function estChaineNonVide(valeur: unknown): valeur is string {
  return typeof valeur === "string" && valeur.trim().length > 0;
}

export function estEntierPositif(valeur: unknown): valeur is number {
  return typeof valeur === "number" && Number.isInteger(valeur) && valeur > 0;
}

export function estRessourceNomenclature(valeur: unknown): valeur is RessourceNomenclature {
  return (
    typeof valeur === "string" &&
    (RESSOURCES_NOMENCLATURE as readonly string[]).includes(valeur)
  );
}

/** Vérifie la présence des deux seuls champs obligatoires d'un ouvrage. */
export function estOuvrageInput(valeur: unknown): valeur is OuvrageInput {
  if (typeof valeur !== "object" || valeur === null) return false;
  const candidat = valeur as Record<string, unknown>;
  return estChaineNonVide(candidat.titre) && estChaineNonVide(candidat.auteur);
}

export function estNomenclatureInput(valeur: unknown): valeur is NomenclatureInput {
  if (typeof valeur !== "object" || valeur === null) return false;
  return estChaineNonVide((valeur as Record<string, unknown>).nom);
}
