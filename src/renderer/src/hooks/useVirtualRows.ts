import { useEffect, useState } from "react";
import * as config from "../../../shared/config";

export interface FenetreVirtuelle {
  /** Index de la première ligne rendue. */
  debut: number;
  /** Index suivant la dernière ligne rendue. */
  fin: number;
  /** Hauteur du bloc d'espacement précédant les lignes rendues. */
  hauteurAvant: number;
  /** Hauteur du bloc d'espacement suivant les lignes rendues. */
  hauteurApres: number;
}

/**
 * Calcule la fenêtre de rendu. Fonction pure, isolée du DOM pour rester vérifiable.
 * La hauteur de ligne est fixe : c'est la condition d'une virtualisation par simple division.
 */
export function calculerFenetre(
  total: number,
  hauteurLigne: number,
  positionDefilement: number,
  hauteurVisible: number,
  marge: number,
): FenetreVirtuelle {
  if (total <= 0 || hauteurLigne <= 0) {
    return { debut: 0, fin: 0, hauteurAvant: 0, hauteurApres: 0 };
  }
  const premiereVisible = Math.floor(Math.max(0, positionDefilement) / hauteurLigne);
  const nombreVisible = Math.ceil(Math.max(0, hauteurVisible) / hauteurLigne);
  const debut = Math.max(0, premiereVisible - marge);
  const fin = Math.min(total, premiereVisible + nombreVisible + marge);
  return {
    debut,
    fin,
    hauteurAvant: debut * hauteurLigne,
    hauteurApres: Math.max(0, total - fin) * hauteurLigne,
  };
}

/**
 * Virtualisation d'une liste plate à hauteur de ligne constante.
 * Aucune bibliothèque : la collection tient en mémoire, seule la fenêtre visible est rendue.
 */
export function useVirtualRows(
  total: number,
  conteneur: React.RefObject<HTMLElement | null>,
): FenetreVirtuelle {
  const [fenetre, setFenetre] = useState<FenetreVirtuelle>(() =>
    calculerFenetre(total, config.ROW_HEIGHT, 0, 0, config.ROW_OVERSCAN),
  );

  useEffect(() => {
    const element = conteneur.current;
    if (!element) return;

    const recalculer = (): void => {
      setFenetre(
        calculerFenetre(
          total,
          config.ROW_HEIGHT,
          element.scrollTop,
          element.clientHeight,
          config.ROW_OVERSCAN,
        ),
      );
    };

    element.addEventListener("scroll", recalculer, { passive: true });
    // L'observateur appelle son rappel dès la mise en observation : c'est le premier calcul,
    // ce qui évite un setState synchrone dans le corps de l'effet.
    const observateur = new ResizeObserver(recalculer);
    observateur.observe(element);

    return () => {
      element.removeEventListener("scroll", recalculer);
      observateur.disconnect();
    };
  }, [conteneur, total]);

  return fenetre;
}
