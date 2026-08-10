import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ChampsDisponibles, OuvrageListe } from "../../../shared/types";
import { normaliser } from "../utils/normalize";
import { useSession } from "./useSession";

export type ColonneTri = "auteur" | "titre" | "edition" | "categorie";
export type SensTri = "asc" | "desc";

/** Special values of the location filter, as opposed to an identifier. */
export const LOCALISATION_TOUTES = "toutes";
export const LOCALISATION_ABSENTE = "non-renseignee";

export interface OuvragesApi {
  /** Full collection as received, for the dashboard aggregations. */
  toutes: OuvrageListe[];
  /** Collection filtered then sorted, as displayed by the table. */
  lignes: OuvrageListe[];
  chargement: boolean;
  recherche: string;
  setRecherche(valeur: string): void;
  localisation: string;
  setLocalisation(valeur: string): void;
  colonne: ColonneTri;
  sens: SensTri;
  basculerTri(colonne: ColonneTri): void;
  effacerFiltres(): void;
  recharger(): Promise<void>;
  /** Enriched fields actually provided by the API, see docs/api/evolution-liste-ouvrages.md. */
  champs: ChampsDisponibles;
}

export const OuvragesContext = createContext<OuvragesApi | null>(null);

export function useOuvrages(): OuvragesApi {
  const api = useContext(OuvragesContext);
  if (!api) throw new Error("useOuvrages doit être utilisé à l'intérieur de OuvragesContext.");
  return api;
}

function valeurTri(ligne: OuvrageListe, colonne: ColonneTri): string {
  switch (colonne) {
    case "auteur":
      return ligne.auteur;
    case "titre":
      return ligne.titre;
    case "edition":
      return ligne.edition ?? "";
    case "categorie":
      return ligne.categorie_nom ?? "";
  }
}

/** A field is available as soon as it is present in the response, even valued `null`. */
function detecterChamps(lignes: OuvrageListe[]): ChampsDisponibles {
  const echantillon = lignes[0];
  if (!echantillon) {
    return { localisation: false, periode: false, dateCreation: false, couvertures: false };
  }
  return {
    localisation: "id_localisation" in echantillon,
    periode: "id_periode" in echantillon,
    dateCreation: "date_creation" in echantillon,
    couvertures: "a_couverture_premiere" in echantillon,
  };
}

/**
 * Book collection: loading, searching, filtering and sorting.
 *
 * The server does not paginate, does not sort on request and reads no query parameter.
 * Everything happens here, on the collection held in memory. No automatic reload: the API
 * quota is shared and unprotected.
 */
export function useOuvragesState(actif: boolean): OuvragesApi {
  const { echouer } = useSession();
  const [toutes, setToutes] = useState<OuvrageListe[]>([]);
  // True from mount: the first load starts immediately, and flagging the busy state here
  // rather than at the start of `recharger` avoids a synchronous setState in the effect.
  const [chargement, setChargement] = useState(true);
  const [recherche, setRecherche] = useState("");
  const [localisation, setLocalisation] = useState<string>(LOCALISATION_TOUTES);
  const [colonne, setColonne] = useState<ColonneTri>("auteur");
  const [sens, setSens] = useState<SensTri>("asc");

  const recharger = useCallback(async () => {
    const resultat = await window.api.ouvrageList();
    setChargement(false);
    if (!resultat.ok) {
      echouer(resultat.error);
      return;
    }
    setToutes(resultat.data);
  }, [echouer]);

  // Initial load written inside the effect, with a cancellation flag: calling `recharger`
  // here would expose a setState outside the asynchronous body of the effect.
  useEffect(() => {
    if (!actif) return;
    let annule = false;
    void (async () => {
      const resultat = await window.api.ouvrageList();
      if (annule) return;
      setChargement(false);
      if (!resultat.ok) {
        echouer(resultat.error);
        return;
      }
      setToutes(resultat.data);
    })();
    return () => {
      annule = true;
    };
  }, [actif, echouer]);

  const basculerTri = useCallback((cible: ColonneTri) => {
    setColonne((courante) => {
      if (courante === cible) {
        setSens((precedent) => (precedent === "asc" ? "desc" : "asc"));
        return courante;
      }
      setSens("asc");
      return cible;
    });
  }, []);

  const effacerFiltres = useCallback(() => {
    setRecherche("");
    setLocalisation(LOCALISATION_TOUTES);
  }, []);

  const champs = useMemo(() => detecterChamps(toutes), [toutes]);

  const lignes = useMemo(() => {
    // The typed string is normalised the same way `recherche_normalisee` is server side.
    const terme = normaliser(recherche);
    const filtrees = toutes.filter((ligne) => {
      if (terme && !ligne.recherche_normalisee.includes(terme)) {
        // The category is not part of `recherche_normalisee`: it is compared separately.
        if (!normaliser(ligne.categorie_nom ?? "").includes(terme)) return false;
      }
      if (!champs.localisation || localisation === LOCALISATION_TOUTES) return true;
      if (localisation === LOCALISATION_ABSENTE) return !ligne.id_localisation;
      return String(ligne.id_localisation ?? "") === localisation;
    });

    const facteur = sens === "asc" ? 1 : -1;
    return [...filtrees].sort(
      (a, b) =>
        facteur *
        valeurTri(a, colonne).localeCompare(valeurTri(b, colonne), "fr", { sensitivity: "base" }),
    );
  }, [toutes, recherche, localisation, colonne, sens, champs.localisation]);

  return {
    toutes,
    lignes,
    chargement,
    recherche,
    setRecherche,
    localisation,
    setLocalisation,
    colonne,
    sens,
    basculerTri,
    effacerFiltres,
    recharger,
    champs,
  };
}
