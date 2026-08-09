import type { ApiStatus } from "../../../../shared/types";
import { t, tp } from "../../i18n";
import { formaterHeure, formaterNombre } from "../../utils/helpers";

export interface StatusbarProps {
  message: string;
  occupe: boolean;
  affiches: number;
  total: number;
  version: string;
  statut: ApiStatus;
}

const LIBELLE_STATUT = {
  connecte: "statut.connecte",
  serveur: "statut.serveur",
  "hors-ligne": "statut.horsLigne",
} as const;

/**
 * Barre d'état. L'indicateur d'API reflète le dernier appel réellement effectué :
 * aucun sondage périodique, le quota du serveur est partagé et non protégé.
 */
export function Statusbar({
  message,
  occupe,
  affiches,
  total,
  version,
  statut,
}: StatusbarProps): React.JSX.Element {
  const infobulle = statut.dernierEchange
    ? tp("statut.dernierEchange", { heure: formaterHeure(statut.dernierEchange) })
    : t("statut.aucunEchange");

  return (
    <footer id="statusbar">
      <span className="statusbar-message">{message}</span>
      <span className="statusbar-progression">
        {occupe ? <progress aria-label={t("etat.chargement")} /> : null}
      </span>
      <span className="statusbar-infos">
        <span className="statusbar-compteur">
          {tp("statut.compteur", {
            affiches: formaterNombre(affiches),
            total: formaterNombre(total),
          })}
        </span>
        <span className={`indicateur indicateur-${statut.etat}`} title={infobulle}>
          <span className="indicateur-point" aria-hidden="true" />
          {t(LIBELLE_STATUT[statut.etat])}
        </span>
        <span className="statusbar-version">{tp("statut.version", { version })}</span>
      </span>
    </footer>
  );
}
