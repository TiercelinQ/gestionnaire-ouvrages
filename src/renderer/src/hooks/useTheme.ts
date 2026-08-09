import { useCallback, useEffect, useState } from "react";
import type { Theme } from "../../../shared/types";

function themeSysteme(): Theme {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

/**
 * Thème courant. Applique `data-theme` sur `<html>` — tous les tokens sont redéfinis
 * dans le bloc `[data-theme="dark"]` de tokens.css, aucune surcharge ailleurs.
 */
export function useTheme(initial: Theme | null): {
  theme: Theme;
  basculer: () => void;
} {
  const [theme, setTheme] = useState<Theme>(initial ?? themeSysteme());

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  const basculer = useCallback(() => {
    setTheme((courant) => {
      const suivant: Theme = courant === "dark" ? "light" : "dark";
      void window.api.setPreference("theme", suivant);
      return suivant;
    });
  }, []);

  return { theme, basculer };
}
