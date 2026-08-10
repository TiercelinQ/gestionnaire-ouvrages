import { useEffect, useState } from "react";
import type { ApiStatus } from "../../../shared/types";

/**
 * API availability state, pushed by the main process after every call.
 * No polling: the value reflects the last exchange actually made.
 */
export function useApiStatus(): ApiStatus {
  const [statut, setStatut] = useState<ApiStatus>({ etat: "connecte", dernierEchange: null });

  useEffect(() => window.api.onApiStatus(setStatut), []);

  return statut;
}
