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
 * Ouvrages : consultation, écriture, corbeille et historique.
 * La corbeille et l'historique sont des états et un journal de la même entité,
 * ils ne justifient pas de modèle distinct.
 */
export const ouvrageModel = {
  /**
   * Liste complète des ouvrages actifs. Le serveur ne pagine pas, ne filtre pas
   * et ne lit aucun paramètre de requête : tri, recherche et filtrage sont côté client.
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
   * Remplace la fiche entière malgré le verbe `PATCH` : tout champ modifiable omis
   * est écrit à `null`. L'appelant envoie donc toujours l'intégralité des champs,
   * accompagnés de la `version` lue au chargement.
   */
  async update(id: number, input: OuvrageUpdateInput): Promise<IpcResult<OuvrageFiche>> {
    return apiClient.patch<OuvrageFiche>(`/ouvrages/${id}`, input);
  },

  /** Suppression logique. Le corps portant la `version` est obligatoire sur ce `DELETE`. */
  async remove(id: number, version: number): Promise<IpcResult<void>> {
    return apiClient.delete<void>(`/ouvrages/${id}`, { version });
  },

  /** Sort un ouvrage de la corbeille. Aucun contrôle de version, aucun délai opposable. */
  async restore(id: number): Promise<IpcResult<OuvrageFiche>> {
    return apiClient.post<OuvrageFiche>(`/ouvrages/${id}/restaurer`);
  },

  async trash(): Promise<IpcResult<OuvrageCorbeille[]>> {
    const resultat = await apiClient.get<EnveloppeOuvrages<OuvrageCorbeille>>("/corbeille");
    return resultat.ok ? { ok: true, data: resultat.data.ouvrages ?? [] } : resultat;
  },

  /**
   * Historique champ par champ. Le serveur ne borne pas le volume renvoyé
   * et ne vérifie pas l'existence de l'objet : un identifiant inconnu donne une liste vide.
   */
  async history(id: number): Promise<IpcResult<EntreeHistorique[]>> {
    const resultat = await apiClient.get<EnveloppeHistorique>(`/ouvrages/${id}/historique`);
    return resultat.ok ? { ok: true, data: resultat.data.historique ?? [] } : resultat;
  },
};
