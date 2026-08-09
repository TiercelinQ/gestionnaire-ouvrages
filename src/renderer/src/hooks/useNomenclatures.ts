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
  /** Rechargement après toute écriture : le serveur est la seule référence. */
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
 * Les sept listes de référence, chargées en un seul appel et conservées pour la session.
 * Il n'existe pas de route de lecture par ressource.
 */
export function useNomenclaturesState(actif: boolean): NomenclaturesApi {
  const { echouer } = useSession();
  const [nomenclatures, setNomenclatures] = useState<Nomenclatures>(VIDES);
  // Vrai dès le montage : le premier chargement part immédiatement, et signaler l'occupation
  // ici plutôt qu'au début de `recharger` évite un setState synchrone dans l'effet.
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

  // Chargement initial écrit dans l'effet, avec drapeau d'annulation : appeler `recharger`
  // ici exposerait un setState hors du corps asynchrone de l'effet.
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
