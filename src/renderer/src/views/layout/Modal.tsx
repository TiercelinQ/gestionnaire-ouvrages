import { useEffect, type ReactNode } from "react";
import { X } from "lucide-react";
import { t } from "../../i18n";

export interface ModalProps {
  ouvert: boolean;
  titre: string;
  /** `large` serves the book record: three columns, 1200 px over 85 % of the height. */
  taille?: "standard" | "moyenne" | "large" | "image";
  /**
   * Escape closes the modal. Set to `false` on the modal underneath when another one is
   * stacked on top, so a single key press only closes the topmost one.
   */
  fermetureClavier?: boolean;
  onFermer(): void;
  pied?: ReactNode;
  children: ReactNode;
}

/**
 * Controlled modal. Replaces every native dialog: no `alert`, `confirm`
 * nor `dialog.showMessageBox` in the application.
 */
export function Modal({
  ouvert,
  titre,
  taille = "standard",
  fermetureClavier = true,
  onFermer,
  pied,
  children,
}: ModalProps): React.JSX.Element | null {
  useEffect(() => {
    if (!ouvert || !fermetureClavier) return;
    const surTouche = (evenement: KeyboardEvent): void => {
      if (evenement.key === "Escape") onFermer();
    };
    window.addEventListener("keydown", surTouche);
    return () => window.removeEventListener("keydown", surTouche);
  }, [ouvert, fermetureClavier, onFermer]);

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
          <button
            type="button"
            className="btn-ghost btn-icon"
            onClick={onFermer}
            title={t("action.fermer")}
          >
            <X className="icon icon-md" strokeWidth={1.75} aria-hidden="true" />
          </button>
        </header>
        <div className="modal-body">{children}</div>
        {pied ? <footer className="modal-footer">{pied}</footer> : null}
      </div>
    </div>
  );
}
