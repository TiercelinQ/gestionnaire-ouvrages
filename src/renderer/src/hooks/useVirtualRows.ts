import { useEffect, useState } from "react";
import * as config from "../../../shared/config";

export interface FenetreVirtuelle {
  /** Index of the first rendered row. */
  debut: number;
  /** Index following the last rendered row. */
  fin: number;
  /** Height of the spacer block preceding the rendered rows. */
  hauteurAvant: number;
  /** Height of the spacer block following the rendered rows. */
  hauteurApres: number;
}

/**
 * Computes the render window. Pure function, isolated from the DOM to stay testable.
 * The row height is fixed: that is what makes virtualisation a plain division.
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
 * Virtualisation of a flat list with a constant row height.
 * No library: the collection fits in memory, only the visible window is rendered.
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
    // The observer calls its callback as soon as it starts observing: that is the first
    // computation, which avoids a synchronous setState in the effect body.
    const observateur = new ResizeObserver(recalculer);
    observateur.observe(element);

    return () => {
      element.removeEventListener("scroll", recalculer);
      observateur.disconnect();
    };
  }, [conteneur, total]);

  return fenetre;
}
