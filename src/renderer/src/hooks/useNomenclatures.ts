import { createContext, useCallback, useContext, useEffect, useState } from "react";
import type { Nomenclatures } from "../../../shared/types";
import { useSession } from "./useSession";

const VIDES: Nomenclatures = {
  categories: [],
  genres: [],
  sous_genres: [],
  illustrations: [],
  localisations: [],
  periodes: [],
  reliures: [],
};

export interface NomenclaturesApi {
  nomenclatures: Nomenclatures;
  chargement: boolean;
  /** Reload after any write: the server is the only reference. */
  recharger(): Promise<void>;
}

export const NomenclaturesContext = createContext<NomenclaturesApi | null>(null);

export function useNomenclatures(): NomenclaturesApi {
  const api = useContext(NomenclaturesContext);
  if (!api) {
    throw new Error("useNomenclatures doit être utilisé à l'intérieur de NomenclaturesContext.");
  }
  return api;
}

/**
 * The seven reference lists, loaded in a single call and kept for the session.
 * There is no per-resource read route.
 */
export function useNomenclaturesState(actif: boolean): NomenclaturesApi {
  const { echouer } = useSession();
  const [nomenclatures, setNomenclatures] = useState<Nomenclatures>(VIDES);
  // True from mount: the first load starts immediately, and flagging the busy state here
  // rather than at the start of `recharger` avoids a synchronous setState in the effect.
  const [chargement, setChargement] = useState(true);

  const recharger = useCallback(async () => {
    const resultat = await window.api.nomenclatureList();
    setChargement(false);
    if (!resultat.ok) {
      echouer(resultat.error);
      return;
    }
    setNomenclatures(resultat.data);
  }, [echouer]);

  // Initial load written inside the effect, with a cancellation flag: calling `recharger`
  // here would expose a setState outside the asynchronous body of the effect.
  useEffect(() => {
    if (!actif) return;
    let annule = false;
    void (async () => {
      const resultat = await window.api.nomenclatureList();
      if (annule) return;
      setChargement(false);
      if (!resultat.ok) {
        echouer(resultat.error);
        return;
      }
      setNomenclatures(resultat.data);
    })();
    return () => {
      annule = true;
    };
  }, [actif, echouer]);

  return { nomenclatures, chargement, recharger };
}
