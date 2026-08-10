import { useEffect, useState } from "react";
import { TriangleAlert } from "lucide-react";
import type { AppInfo } from "../../../shared/types";
import { t, tp } from "../i18n";

export interface UpdateRequiredViewProps {
  /** Server message, displayed as it comes. */
  message: string;
}

/**
 * Blocking screen on a version refusal.
 *
 * The version check runs before route resolution: every route is refused at once. The
 * situation only resolves by installing a new version, so no retry button is offered -
 * retrying would consume a shared quota without ever succeeding.
 */
export function UpdateRequiredView({ message }: UpdateRequiredViewProps): React.JSX.Element {
  const [info, setInfo] = useState<AppInfo | null>(null);

  useEffect(() => {
    let annule = false;
    void (async () => {
      // The only route exempt from headers: it answers even a rejected client.
      const resultat = await window.api.appInfo();
      if (!annule && resultat.ok) setInfo(resultat.data);
    })();
    return () => {
      annule = true;
    };
  }, []);

  return (
    <main className="ecran-plein">
      <section className="carte carte-message">
        <TriangleAlert
          className="icon icon-lg icon-warning"
          strokeWidth={1.75}
          aria-hidden="true"
        />
        <h1 className="carte-titre">{t("maj.titre")}</h1>
        <p className="texte-corps">{message || t("maj.messageDefaut")}</p>
        <dl className="liste-definition">
          <dt>{t("maj.versionInstallee")}</dt>
          <dd>{info?.version ?? "-"}</dd>
          <dt>{t("maj.versionMinimale")}</dt>
          <dd>{info?.versionsMinimales?.electron ?? t("apropos.inconnue")}</dd>
        </dl>
        <p className="texte-secondaire">
          {tp("maj.consigne", { application: info?.nom ?? t("apropos.application") })}
        </p>
      </section>
    </main>
  );
}
