import type {
  IpcResult,
  Nomenclature,
  NomenclatureInput,
  Nomenclatures,
  RessourceNomenclature,
} from "../../shared/types";
import { apiClient } from "./api-client";

/**
 * URL segments use a hyphen where the JSON keys and the tables use an underscore.
 * The mapping is explicit to prevent any drift.
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
 * Nomenclatures: the seven reference lists.
 * Reading is grouped into a single call, there is no per-resource route.
 */
export const nomenclatureModel = {
  /** Grouped read of the seven lists, each sorted by ascending name server side. */
  async list(): Promise<IpcResult<Nomenclatures>> {
    const resultat = await apiClient.get<Partial<Nomenclatures>>("/nomenclatures");
    if (!resultat.ok) return resultat;
    // Defensive read: a missing list means an empty list, never `undefined` in the renderer.
    return { ok: true, data: { ...LISTES_VIDES, ...resultat.data } };
  },

  async create(
    ressource: RessourceNomenclature,
    input: NomenclatureInput,
  ): Promise<IpcResult<Nomenclature>> {
    return apiClient.post<Nomenclature>(`/${ressource}`, { corps: input });
  },

  /**
   * Renames, and moves for the two hierarchical resources.
   * Moving is refused if at least one book references the value, trash included.
   */
  async update(
    ressource: RessourceNomenclature,
    id: number,
    input: NomenclatureInput,
  ): Promise<IpcResult<Nomenclature>> {
    return apiClient.patch<Nomenclature>(`/${ressource}/${id}`, input);
  },

  /** Permanent deletion, no trash. Refused if the value is in use or has children. */
  async remove(ressource: RessourceNomenclature, id: number): Promise<IpcResult<void>> {
    return apiClient.delete<void>(`/${ressource}/${id}`);
  },
};
