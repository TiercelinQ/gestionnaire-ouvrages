import { useEffect, useState } from "react";
import type { EntreeHistorique } from "../../../../shared/types";
import { t } from "../../i18n";
import { formaterDateHeure } from "../../utils/helpers";
import { useSession } from "../../hooks/useSession";
import { Modal } from "../layout/Modal";

export interface HistoriqueModalProps {
  ouvert: boolean;
  ouvrageId: number | null;
  onFermer(): void;
}

/** The only value the server does not translate: translating it is the client's job. */
const ACTIONS = {
  creation: "historique.creation",
  modification: "historique.modification",
  suppression: "historique.suppression",
  restauration: "historique.restauration",
} as const;

const ABSENT = "-";

/**
 * History of a book record, field by field, stacked over the record modal.
 *
 * The server translates the labels and resolves the nomenclature identifiers: rows are
 * displayed as they come, with no client-side lookup table. The returned volume is not
 * bounded, hence the scrolling modal body and the sticky table header.
 */
export function HistoriqueModal({
  ouvert,
  ouvrageId,
  onFermer,
}: HistoriqueModalProps): React.JSX.Element {
  const { echouer } = useSession();
  const [entrees, setEntrees] = useState<EntreeHistorique[]>([]);
  // The component is remounted on every opening (key on the caller side): the state therefore
  // starts in the loading position without a synchronous setState inside the effect.
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

  function valeur(brute: string | null, classe: string): React.JSX.Element | string {
    if (!brute) return ABSENT;
    return <span className={classe}>{brute}</span>;
  }

  return (
    <Modal ouvert={ouvert} titre={t("historique.titre")} taille="moyenne" onFermer={onFermer}>
      {chargement ? <p className="etat-vide">{t("etat.chargement")}</p> : null}

      {!chargement && entrees.length === 0 ? (
        <p className="etat-vide">{t("historique.aucune")}</p>
      ) : null}

      {entrees.length > 0 ? (
        <table className="data-table table-simple">
          <thead>
            <tr>
              <th className="colonne-moyenne">{t("historique.colonneDate")}</th>
              <th className="colonne-moyenne">{t("historique.colonneAuteur")}</th>
              <th className="colonne-moyenne">{t("historique.colonneAction")}</th>
              <th className="colonne-moyenne">{t("historique.colonneChamp")}</th>
              <th>{t("historique.colonneAvant")}</th>
              <th>{t("historique.colonneApres")}</th>
            </tr>
          </thead>
          <tbody>
            {entrees.map((entree) => (
              <tr key={entree.id}>
                <td className="cellule-date">{formaterDateHeure(entree.date_action)}</td>
                <td>{entree.auteur}</td>
                <td>{t(ACTIONS[entree.action])}</td>
                <td>{entree.champ_libelle ?? ABSENT}</td>
                <td>
                  {entree.action === "modification"
                    ? valeur(entree.ancienne_valeur, "historique-avant")
                    : ABSENT}
                </td>
                <td>
                  {entree.action === "modification"
                    ? valeur(entree.nouvelle_valeur, "historique-apres")
                    : ABSENT}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
    </Modal>
  );
}
