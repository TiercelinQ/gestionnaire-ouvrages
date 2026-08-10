import { useEffect, useRef } from "react";
import { Info, LibraryBig, LogOut, Moon, Sun } from "lucide-react";
import * as config from "../../../../shared/config";
import type { Theme, Utilisateur } from "../../../../shared/types";
import { t } from "../../i18n";

export type Onglet = "dashboard" | "ouvrages" | "corbeille" | "parametres";

export const ONGLETS: { cle: Onglet; libelle: string }[] = [
  { cle: "dashboard", libelle: t("onglet.dashboard") },
  { cle: "ouvrages", libelle: t("onglet.ouvrages") },
  { cle: "corbeille", libelle: t("onglet.corbeille") },
  { cle: "parametres", libelle: t("onglet.parametres") },
];

export interface TopbarProps {
  onglet: Onglet;
  onOnglet(onglet: Onglet): void;
  utilisateur: Utilisateur | null;
  theme: Theme;
  onTheme(): void;
  onAPropos(): void;
  onDeconnexion(): void;
}

export function Topbar({
  onglet,
  onOnglet,
  utilisateur,
  theme,
  onTheme,
  onAPropos,
  onDeconnexion,
}: TopbarProps): React.JSX.Element {
  const onglets = useRef<HTMLElement>(null);

  // Signature gesture: the underline slides to the active tab. The only visual positioned
  // in JavaScript, limited to two CSS variables (design-system.md section 8).
  useEffect(() => {
    const conteneur = onglets.current;
    if (!conteneur) return;
    const placer = (): void => {
      const actif = conteneur.querySelector<HTMLElement>(".tab.is-active");
      if (!actif) return;
      conteneur.style.setProperty("--underline-x", `${actif.offsetLeft}px`);
      conteneur.style.setProperty("--underline-w", `${actif.offsetWidth}px`);
    };
    placer();
    window.addEventListener("resize", placer);
    return () => window.removeEventListener("resize", placer);
  }, [onglet]);

  return (
    <header id="topbar">
      <div className="topbar-marque">
        <LibraryBig className="icon icon-lg icon-active" strokeWidth={1.75} aria-hidden="true" />
        <span className="topbar-nom">{config.APP_DISPLAY_NAME}</span>
      </div>

      <nav id="topbar-tabs" className="tabs" ref={onglets} aria-label={t("nav.principale")}>
        {ONGLETS.map((element) => (
          <button
            key={element.cle}
            type="button"
            className={`tab${element.cle === onglet ? " is-active" : ""}`}
            onClick={() => onOnglet(element.cle)}
            aria-current={element.cle === onglet ? "page" : undefined}
          >
            {element.libelle}
          </button>
        ))}
      </nav>

      <div className="topbar-actions">
        {utilisateur ? <span className="topbar-compte">{utilisateur.nom_affichage}</span> : null}
        <button
          type="button"
          className="btn-ghost btn-icon"
          onClick={onAPropos}
          title={t("action.apropos")}
        >
          <Info className="icon icon-lg" strokeWidth={1.75} aria-hidden="true" />
        </button>
        <button
          type="button"
          className="btn-ghost btn-icon"
          onClick={onTheme}
          title={theme === "dark" ? t("theme.clair") : t("theme.sombre")}
        >
          {theme === "dark" ? (
            <Sun className="icon icon-lg" strokeWidth={1.75} aria-hidden="true" />
          ) : (
            <Moon className="icon icon-lg" strokeWidth={1.75} aria-hidden="true" />
          )}
        </button>
        <button
          type="button"
          className="btn-ghost btn-icon"
          onClick={onDeconnexion}
          title={t("action.deconnexion")}
        >
          <LogOut className="icon icon-lg" strokeWidth={1.75} aria-hidden="true" />
        </button>
      </div>
    </header>
  );
}
