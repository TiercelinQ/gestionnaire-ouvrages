import type {
  EntreeHistorique,
  IpcResult,
  OuvrageCorbeille,
  OuvrageFiche,
  OuvrageInput,
  OuvrageListe,
  OuvrageUpdateInput,
} from "../../shared/types";
import { apiClient } from "./api-client";

interface EnveloppeOuvrages<T> {
  ouvrages: T[];
}

interface EnveloppeHistorique {
  historique: EntreeHistorique[];
}

/**
 * Books: reading, writing, trash and history.
 * The trash and the history are a state and a journal of the same entity,
 * they do not warrant a separate model.
 */
export const ouvrageModel = {
  /**
   * Full list of active books. The server does not paginate, does not filter and reads no
   * query parameter: sorting, searching and filtering all happen client side.
   */
  async list(): Promise<IpcResult<OuvrageListe[]>> {
    const resultat = await apiClient.get<EnveloppeOuvrages<OuvrageListe>>("/ouvrages");
    return resultat.ok ? { ok: true, data: resultat.data.ouvrages ?? [] } : resultat;
  },

  async get(id: number): Promise<IpcResult<OuvrageFiche>> {
    return apiClient.get<OuvrageFiche>(`/ouvrages/${id}`);
  },

  async create(input: OuvrageInput): Promise<IpcResult<OuvrageFiche>> {
    return apiClient.post<OuvrageFiche>("/ouvrages", { corps: input });
  },

  /**
   * Replaces the whole record despite the `PATCH` verb: any editable field omitted is
   * written as `null`. The caller therefore always sends every field, along with the
   * `version` read when loading.
   */
  async update(id: number, input: OuvrageUpdateInput): Promise<IpcResult<OuvrageFiche>> {
    return apiClient.patch<OuvrageFiche>(`/ouvrages/${id}`, input);
  },

  /** Soft deletion. The body carrying the `version` is mandatory on this `DELETE`. */
  async remove(id: number, version: number): Promise<IpcResult<void>> {
    return apiClient.delete<void>(`/ouvrages/${id}`, { version });
  },

  /** Takes a book out of the trash. No version check, no enforceable deadline. */
  async restore(id: number): Promise<IpcResult<OuvrageFiche>> {
    return apiClient.post<OuvrageFiche>(`/ouvrages/${id}/restaurer`);
  },

  async trash(): Promise<IpcResult<OuvrageCorbeille[]>> {
    const resultat = await apiClient.get<EnveloppeOuvrages<OuvrageCorbeille>>("/corbeille");
    return resultat.ok ? { ok: true, data: resultat.data.ouvrages ?? [] } : resultat;
  },

  /**
   * History field by field. The server does not bound the returned volume and does not
   * check the object exists: an unknown identifier yields an empty list.
   */
  async history(id: number): Promise<IpcResult<EntreeHistorique[]>> {
    const resultat = await apiClient.get<EnveloppeHistorique>(`/ouvrages/${id}/historique`);
    return resultat.ok ? { ok: true, data: resultat.data.historique ?? [] } : resultat;
  },
};
