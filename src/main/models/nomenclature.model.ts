import type {
  IpcResult,
  Nomenclature,
  NomenclatureInput,
  Nomenclatures,
  RessourceNomenclature,
} from "../../shared/types";
import { apiClient } from "./api-client";

/**
 * Les segments d'URL emploient le trait d'union là où les clés JSON et les tables
 * emploient le tiret bas. La correspondance est explicite pour éviter toute dérive.
 */
export const CLE_JSON: Record<RessourceNomenclature, keyof Nomenclatures> = {
  categories: "categories",
  genres: "genres",
  "sous-genres": "sous_genres",
  illustrations: "illustrations",
  localisations: "localisations",
  periodes: "periodes",
  reliures: "reliures",
};

const LISTES_VIDES: Nomenclatures = {
  categories: [],
  genres: [],
  sous_genres: [],
  illustrations: [],
  localisations: [],
  periodes: [],
  reliures: [],
};

/**
 * Nomenclatures : les sept listes de référence.
 * La lecture est groupée en un seul appel, il n'existe pas de route par ressource.
 */
export const nomenclatureModel = {
  /** Lecture groupée des sept listes, chacune triée par nom croissant côté serveur. */
  async list(): Promise<IpcResult<Nomenclatures>> {
    const resultat = await apiClient.get<Partial<Nomenclatures>>("/nomenclatures");
    if (!resultat.ok) return resultat;
    // Lecture défensive : une liste absente vaut liste vide, jamais `undefined` côté rendu.
    return { ok: true, data: { ...LISTES_VIDES, ...resultat.data } };
  },

  async create(
    ressource: RessourceNomenclature,
    input: NomenclatureInput,
  ): Promise<IpcResult<Nomenclature>> {
    return apiClient.post<Nomenclature>(`/${ressource}`, { corps: input });
  },

  /**
   * Renomme, et déplace pour les deux ressources hiérarchiques.
   * Le déplacement est refusé si au moins un ouvrage référence la valeur, corbeille comprise.
   */
  async update(
    ressource: RessourceNomenclature,
    id: number,
    input: NomenclatureInput,
  ): Promise<IpcResult<Nomenclature>> {
    return apiClient.patch<Nomenclature>(`/${ressource}/${id}`, input);
  },

  /** Suppression définitive, sans corbeille. Refusée si la valeur est utilisée ou a des enfants. */
  async remove(ressource: RessourceNomenclature, id: number): Promise<IpcResult<void>> {
    return apiClient.delete<void>(`/${ressource}/${id}`);
  },
};
