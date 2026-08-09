import { useEffect, useState } from "react";
import type { ApiStatus } from "../../../shared/types";

/**
 * État de disponibilité de l'API, poussé par le processus principal après chaque appel.
 * Aucun sondage : la valeur reflète le dernier échange réellement effectué.
 */
export function useApiStatus(): ApiStatus {
  const [statut, setStatut] = useState<ApiStatus>({ etat: "connecte", dernierEchange: null });

  useEffect(() => window.api.onApiStatus(setStatut), []);

  return statut;
}
