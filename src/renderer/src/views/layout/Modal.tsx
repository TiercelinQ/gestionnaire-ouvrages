import { useEffect, type ReactNode } from "react";
import { X } from "lucide-react";
import { t } from "../../i18n";

export interface ModalProps {
  ouvert: boolean;
  titre: string;
  /** `large` sert la fiche d'ouvrage : trois colonnes, 1200 px sur 85 % de la hauteur. */
  taille?: "standard" | "large" | "image";
  onFermer(): void;
  pied?: ReactNode;
  children: ReactNode;
}

/**
 * Modale contrôlée. Remplace toute boîte native : aucun `alert`, `confirm`
 * ni `dialog.showMessageBox` dans l'application.
 */
export function Modal({
  ouvert,
  titre,
  taille = "standard",
  onFermer,
  pied,
  children,
}: ModalProps): React.JSX.Element | null {
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
    <div className="modal-overlay" onMouseDown={onFermer} role="presentation">
      <div
        className={`modal modal-${taille}`}
        role="dialog"
        aria-modal="true"
        aria-label={titre}
        onMouseDown={(evenement) => evenement.stopPropagation()}
      >
        <header className="modal-header">
          <h2 className="modal-title">{titre}</h2>
          <button type="button" className="btn-ghost btn-icon" onClick={onFermer} title={t("action.fermer")}>
            <X className="icon icon-md" strokeWidth={1.75} aria-hidden="true" />
          </button>
        </header>
        <div className="modal-body">{children}</div>
        {pied ? <footer className="modal-footer">{pied}</footer> : null}
      </div>
    </div>
  );
}
