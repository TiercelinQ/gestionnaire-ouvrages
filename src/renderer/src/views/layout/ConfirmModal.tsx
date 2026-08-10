import { t } from "../../i18n";
import { Modal } from "./Modal";

export interface ConfirmModalProps {
  ouvert: boolean;
  titre: string;
  message: string;
  /** Label of the confirmation button. The style is that of a destructive action. */
  libelleConfirmer: string;
  occupe?: boolean;
  onConfirmer(): void;
  onAnnuler(): void;
}

/** Confirmation of a destructive action. Never `confirm()`. */
export function ConfirmModal({
  ouvert,
  titre,
  message,
  libelleConfirmer,
  occupe = false,
  onConfirmer,
  onAnnuler,
}: ConfirmModalProps): React.JSX.Element {
  return (
    <Modal
      ouvert={ouvert}
      titre={titre}
      onFermer={onAnnuler}
      pied={
        <div className="btn-group">
          <button type="button" className="btn btn-secondary" onClick={onAnnuler} disabled={occupe}>
            {t("action.annuler")}
          </button>
          <button type="button" className="btn btn-danger" onClick={onConfirmer} disabled={occupe}>
            {libelleConfirmer}
          </button>
        </div>
      }
    >
      <p className="texte-corps">{message}</p>
    </Modal>
  );
}
