import { useEffect, useState } from "react";
import { TriangleAlert } from "lucide-react";
import type { AppInfo } from "../../../shared/types";
import { t, tp } from "../i18n";

export interface UpdateRequiredViewProps {
  /** Message serveur, affiché tel quel. */
  message: string;
}

/**
 * Écran bloquant sur refus de version.
 *
 * Le contrôle de version s'exécute avant la résolution de route : toutes les routes sont
 * refusées d'un coup. La situation ne se résout que par l'installation d'une nouvelle
 * version, aucun bouton de réessai n'est donc proposé - réessayer consommerait un quota
 * partagé sans jamais aboutir.
 */
export function UpdateRequiredView({ message }: UpdateRequiredViewProps): React.JSX.Element {
  const [info, setInfo] = useState<AppInfo | null>(null);

  useEffect(() => {
    let annule = false;
    void (async () => {
      // Seule route dispensée d'en-têtes : elle répond même à un client refusé.
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
