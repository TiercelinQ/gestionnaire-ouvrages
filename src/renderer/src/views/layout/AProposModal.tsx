import { useEffect, useState } from "react";
import type { AppInfo } from "../../../../shared/types";
import { t } from "../../i18n";
import { Modal } from "./Modal";

export interface AProposModalProps {
  ouvert: boolean;
  onFermer(): void;
}

/** Application identity and version threshold accepted by the server. */
export function AProposModal({ ouvert, onFermer }: AProposModalProps): React.JSX.Element {
  const [info, setInfo] = useState<AppInfo | null>(null);

  useEffect(() => {
    if (!ouvert) return;
    let annule = false;
    void (async () => {
      const resultat = await window.api.appInfo();
      if (!annule && resultat.ok) setInfo(resultat.data);
    })();
    return () => {
      annule = true;
    };
  }, [ouvert]);

  return (
    <Modal ouvert={ouvert} titre={t("apropos.titre")} onFermer={onFermer}>
      <dl className="liste-definition">
        <dt>{t("apropos.application")}</dt>
        <dd>{info?.nom ?? "-"}</dd>
        <dt>{t("apropos.version")}</dt>
        <dd>{info?.version ?? "-"}</dd>
        <dt>{t("apropos.versionMinimale")}</dt>
        <dd>{info?.versionsMinimales?.electron ?? t("apropos.inconnue")}</dd>
        <dt>{t("apropos.auteur")}</dt>
        <dd>{t("apropos.auteurValeur")}</dd>
        <dt>{t("apropos.licence")}</dt>
        <dd>{t("apropos.licenceValeur")}</dd>
      </dl>
    </Modal>
  );
}
