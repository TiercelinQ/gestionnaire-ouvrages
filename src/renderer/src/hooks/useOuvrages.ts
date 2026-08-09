import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ChampsDisponibles, OuvrageListe } from "../../../shared/types";
import { normaliser } from "../utils/normalize";
import { useSession } from "./useSession";

export type ColonneTri = "auteur" | "titre" | "edition" | "categorie";
export type SensTri = "asc" | "desc";

/** Valeurs spéciales du filtre par localisation, en regard d'un identifiant. */
export const LOCALISATION_TOUTES = "toutes";
export const LOCALISATION_ABSENTE = "non-renseignee";

export interface OuvragesApi {
  /** Collection complète telle que reçue, pour les agrégations du tableau de bord. */
  toutes: OuvrageListe[];
  /** Collection filtrée puis triée, telle qu'affichée par la table. */
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
  /** Champs enrichis effectivement fournis par l'API, voir docs/api/evolution-liste-ouvrages.md. */
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

/** Un champ est disponible dès qu'il est présent dans la réponse, même valué à `null`. */
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
 * Collection d'ouvrages : chargement, recherche, filtrage et tri.
 *
 * Le serveur ne pagine pas, ne trie pas selon la demande et ne lit aucun paramètre de requête.
 * Tout se fait ici, sur la collection tenue en mémoire. Aucun rechargement automatique :
 * le quota de l'API est partagé et non protégé.
 */
export function useOuvragesState(actif: boolean): OuvragesApi {
  const { echouer } = useSession();
  const [toutes, setToutes] = useState<OuvrageListe[]>([]);
  // Vrai dès le montage : le premier chargement part immédiatement, et signaler l'occupation
  // ici plutôt qu'au début de `recharger` évite un setState synchrone dans l'effet.
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

  // Chargement initial écrit dans l'effet, avec drapeau d'annulation : appeler `recharger`
  // ici exposerait un setState hors du corps asynchrone de l'effet.
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
    // La chaîne saisie est normalisée comme l'est `recherche_normalisee` côté serveur.
    const terme = normaliser(recherche);
    const filtrees = toutes.filter((ligne) => {
      if (terme && !ligne.recherche_normalisee.includes(terme)) {
        // La catégorie n'entre pas dans `recherche_normalisee` : on la compare séparément.
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
