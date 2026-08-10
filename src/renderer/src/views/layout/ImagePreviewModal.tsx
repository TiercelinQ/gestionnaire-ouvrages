import { t } from "../../i18n";
import { Modal } from "./Modal";

export interface ImagePreviewModalProps {
  ouvert: boolean;
  titre: string;
  /** Image already resolved to a data URL by the main process. */
  dataUrl: string | null;
  onFermer(): void;
}

/** Full-screen preview of a cover. */
export function ImagePreviewModal({
  ouvert,
  titre,
  dataUrl,
  onFermer,
}: ImagePreviewModalProps): React.JSX.Element {
  return (
    <Modal ouvert={ouvert} titre={titre} taille="image" onFermer={onFermer}>
      {dataUrl ? (
        <img className="image-apercu" src={dataUrl} alt={titre} />
      ) : (
        <p className="etat-vide">{t("couverture.indisponible")}</p>
      )}
    </Modal>
  );
}
