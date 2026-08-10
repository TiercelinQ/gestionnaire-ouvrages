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
 * Same table mechanics as the book list: the header sits outside the scrolling container so
 * the scroll track starts below it, column widths are fixed and overflowing text is
 * truncated. A sticky header inside the table would not do - Chromium drops the sticky
 * painting of cells under `border-collapse: collapse`, and rows show through the header.
 *
 * The server translates the labels and resolves the nomenclature identifiers: rows are
 * displayed as they come, with no client-side lookup table.
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

  function valeur(entree: EntreeHistorique, cle: "ancienne_valeur" | "nouvelle_valeur"): string {
    if (entree.action !== "modification") return ABSENT;
    return entree[cle] ?? ABSENT;
  }

  return (
    <Modal ouvert={ouvert} titre={t("historique.titre")} taille="moyenne" onFermer={onFermer}>
      {chargement ? <p className="etat-vide">{t("etat.chargement")}</p> : null}

      {!chargement && entrees.length === 0 ? (
        <p className="etat-vide">{t("historique.aucune")}</p>
      ) : null}

      {entrees.length > 0 ? (
        <div className="table-cadre">
          {/* Header outside the scrolling container: the scroll track starts below it. */}
          <div className="table-entete">
            <table className="data-table">
              <thead>
                <tr>
                  <th className="colonne-horodatage">{t("historique.colonneDate")}</th>
                  <th className="colonne-etroite">{t("historique.colonneAuteur")}</th>
                  <th className="colonne-etroite">{t("historique.colonneAction")}</th>
                  <th className="colonne-moyenne">{t("historique.colonneChamp")}</th>
                  <th>{t("historique.colonneAvant")}</th>
                  <th>{t("historique.colonneApres")}</th>
                </tr>
              </thead>
            </table>
          </div>

          <div className="table-defilante">
            <table className="data-table">
              <colgroup>
                <col className="colonne-horodatage" />
                <col className="colonne-etroite" />
                <col className="colonne-etroite" />
                <col className="colonne-moyenne" />
                <col />
                <col />
              </colgroup>
              <tbody>
                {entrees.map((entree) => {
                  const avant = valeur(entree, "ancienne_valeur");
                  const apres = valeur(entree, "nouvelle_valeur");
                  return (
                    <tr key={entree.id}>
                      <td>{formaterDateHeure(entree.date_action)}</td>
                      <td title={entree.auteur}>{entree.auteur}</td>
                      <td>{t(ACTIONS[entree.action])}</td>
                      <td title={entree.champ_libelle ?? ABSENT}>
                        {entree.champ_libelle ?? ABSENT}
                      </td>
                      <td title={avant}>
                        {avant === ABSENT ? (
                          ABSENT
                        ) : (
                          <span className="historique-avant">{avant}</span>
                        )}
                      </td>
                      <td title={apres}>
                        {apres === ABSENT ? (
                          ABSENT
                        ) : (
                          <span className="historique-apres">{apres}</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </Modal>
  );
}
