import { useEffect, type ReactNode } from "react";
import { X } from "lucide-react";
import { t } from "../../i18n";

export interface DrawerProps {
  ouvert: boolean;
  titre: string;
  onFermer(): void;
  children: ReactNode;
}

/**
 * Panneau latéral droit. Ouvert par action explicite uniquement.
 * Largeur portée à 420 px : une ligne d'historique porte cinq colonnes de texte.
 */
export function Drawer({ ouvert, titre, onFermer, children }: DrawerProps): React.JSX.Element | null {
  useEffect(() => {
    if (!ouvert) return;
    const surTouche = (evenement: KeyboardEvent): void => {
      if (evenement.key === "Escape") onFermer();
    };
    window.addEventListener("keydown", surTouche);
    return () => window.removeEventListener("keydown", surTouche);
  }, [ouvert, onFermer]);

  if (!ouvert) return null;

  return (
    <>
      <div className="drawer-overlay" onMouseDown={onFermer} role="presentation" />
      <aside id="drawer" role="dialog" aria-modal="false" aria-label={titre}>
        <header className="drawer-header">
          <h2 className="drawer-title">{titre}</h2>
          <button type="button" className="btn-ghost btn-icon" onClick={onFermer} title={t("action.fermer")}>
            <X className="icon icon-md" strokeWidth={1.75} aria-hidden="true" />
          </button>
        </header>
        <div className="drawer-body">{children}</div>
      </aside>
    </>
  );
}
