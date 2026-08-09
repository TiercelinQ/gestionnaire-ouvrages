import { useEffect, useState } from "react";
import type { EntreeHistorique } from "../../../../shared/types";
import { t } from "../../i18n";
import { formaterDateHeure } from "../../utils/helpers";
import { useSession } from "../../hooks/useSession";
import { Drawer } from "../layout/Drawer";

export interface HistoriqueDrawerProps {
  ouvert: boolean;
  ouvrageId: number | null;
  onFermer(): void;
}

/** Seule valeur non traduite par le serveur : la traduction est à la charge du client. */
const ACTIONS = {
  creation: "historique.creation",
  modification: "historique.modification",
  suppression: "historique.suppression",
  restauration: "historique.restauration",
} as const;

/**
 * Historique d'un ouvrage, champ par champ.
 *
 * Le serveur traduit les libellés et résout les identifiants de nomenclature : les lignes
 * sont affichées telles quelles, sans table de correspondance côté client. Le volume
 * renvoyé n'est pas borné, d'où le défilement interne du panneau.
 */
export function HistoriqueDrawer({
  ouvert,
  ouvrageId,
  onFermer,
}: HistoriqueDrawerProps): React.JSX.Element {
  const { echouer } = useSession();
  const [entrees, setEntrees] = useState<EntreeHistorique[]>([]);
  // Le composant est remonté à chaque ouverture (clé côté appelant) : l'état repart donc
  // en chargement sans qu'un setState synchrone soit nécessaire dans l'effet.
  const [chargement, setChargement] = useState(true);

  useEffect(() => {
    if (!ouvert || ouvrageId === null) return;
    let annule = false;
    void (async () => {
      const resultat = await window.api.ouvrageHistory(ouvrageId);
      if (annule) return;
      setChargement(false);
      if (!resultat.ok) {
        echouer(resultat.error);
        return;
      }
      setEntrees(resultat.data);
    })();
    return () => {
      annule = true;
    };
  }, [ouvert, ouvrageId, echouer]);

  return (
    <Drawer ouvert={ouvert} titre={t("historique.titre")} onFermer={onFermer}>
      {chargement ? <p className="etat-vide">{t("etat.chargement")}</p> : null}

      {!chargement && entrees.length === 0 ? (
        <p className="etat-vide">{t("historique.aucune")}</p>
      ) : null}

      <ul className="historique">
        {entrees.map((entree) => (
          <li key={entree.id} className="historique-entree">
            <div className="historique-entete">
              <span className="historique-action">{t(ACTIONS[entree.action])}</span>
              <span className="historique-date">{formaterDateHeure(entree.date_action)}</span>
            </div>
            <p className="historique-auteur">{entree.auteur}</p>
            {entree.champ_libelle ? (
              <p className="historique-champ">{entree.champ_libelle}</p>
            ) : null}
            {entree.action === "modification" ? (
              <p className="historique-valeurs">
                <span className="historique-avant">{entree.ancienne_valeur ?? "-"}</span>
                <span className="historique-fleche" aria-hidden="true">
                  →
                </span>
                <span className="historique-apres">{entree.nouvelle_valeur ?? "-"}</span>
              </p>
            ) : null}
          </li>
        ))}
      </ul>
    </Drawer>
  );
}
