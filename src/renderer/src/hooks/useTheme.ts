import { useCallback, useEffect, useState } from "react";
import type { Theme } from "../../../shared/types";

function themeSysteme(): Theme {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

/**
 * Current theme. Applies `data-theme` on `<html>` - every token is redefined in the
 * `[data-theme="dark"]` block of tokens.css, with no override anywhere else.
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
