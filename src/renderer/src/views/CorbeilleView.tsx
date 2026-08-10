import { useCallback, useEffect, useState } from "react";
import { RefreshCw, Undo2 } from "lucide-react";
import type { OuvrageCorbeille } from "../../../shared/types";
import { t, tp } from "../i18n";
import { formaterDateHeure, formaterNombre } from "../utils/helpers";
import { useOuvrages } from "../hooks/useOuvrages";
import { useSession } from "../hooks/useSession";
import { useToast } from "../hooks/useToast";

/**
 * Trash. Purging is a daily server task: a book with zero remaining days can stay visible
 * for up to twenty-four hours, so it is neither hidden nor greyed out.
 */
export function CorbeilleView(): React.JSX.Element {
  const { echouer } = useSession();
  const { toast } = useToast();
  const ouvrages = useOuvrages();
  const [lignes, setLignes] = useState<OuvrageCorbeille[]>([]);
  // True from mount: loading starts immediately. The Refresh button sets the flag back to
  // true from its own handler, outside the effect body.
  const [chargement, setChargement] = useState(true);

  const charger = useCallback(async () => {
    const resultat = await window.api.corbeilleList();
    setChargement(false);
    if (!resultat.ok) {
      echouer(resultat.error);
      return;
    }
    setLignes(resultat.data);
  }, [echouer]);

  // Initial load written inside the effect, with a cancellation flag: calling `charger`
  // here would expose a setState outside the asynchronous body of the effect.
  useEffect(() => {
    let annule = false;
    void (async () => {
      const resultat = await window.api.corbeilleList();
      if (annule) return;
      setChargement(false);
      if (!resultat.ok) {
        echouer(resultat.error);
        return;
      }
      setLignes(resultat.data);
    })();
    return () => {
      annule = true;
    };
  }, [echouer]);

  async function restaurer(ligne: OuvrageCorbeille): Promise<void> {
    const resultat = await window.api.ouvrageRestore(ligne.id);
    if (!resultat.ok) {
      echouer(resultat.error);
      return;
    }
    toast("success", tp("corbeille.restaure", { titre: ligne.titre }));
    await charger();
    await ouvrages.recharger();
  }

  return (
    <section className="vue">
      <header className="vue-entete">
        <h1 className="vue-titre">{t("onglet.corbeille")}</h1>
        <p className="vue-sous-titre">{t("corbeille.soustitre")}</p>
      </header>

      <div className="barre-outils">
        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => {
            setChargement(true);
            void charger();
          }}
          disabled={chargement}
        >
          <RefreshCw className="icon icon-sm" strokeWidth={1.75} aria-hidden="true" />
          {t("action.actualiser")}
        </button>
      </div>

      <div className="table-cadre">
        {/* Header outside the scrolling container: the scroll track starts below it. */}
        <div className="table-entete">
          <table className="data-table">
            <thead>
              <tr>
                <th className="colonne-large">{t("ouvrage.auteur")}</th>
                <th>{t("ouvrage.titre")}</th>
                <th className="colonne-moyenne">{t("corbeille.supprimeLe")}</th>
                <th className="colonne-moyenne">{t("corbeille.supprimePar")}</th>
                <th className="colonne-etroite">{t("corbeille.joursRestants")}</th>
                <th className="colonne-actions">{t("table.actions")}</th>
              </tr>
            </thead>
          </table>
        </div>

        <div className="table-defilante">
          <table className="data-table">
            <colgroup>
              <col className="colonne-large" />
              <col />
              <col className="colonne-moyenne" />
              <col className="colonne-moyenne" />
              <col className="colonne-etroite" />
              <col className="colonne-actions" />
            </colgroup>
            <tbody>
              {lignes.map((ligne) => (
                <tr key={ligne.id}>
                  <td title={ligne.auteur}>{ligne.auteur}</td>
                  <td title={ligne.titre}>{ligne.titre}</td>
                  <td>{formaterDateHeure(ligne.supprime_le)}</td>
                  <td>{ligne.supprime_par_nom ?? ""}</td>
                  <td className="cellule-nombre">{formaterNombre(ligne.jours_restants)}</td>
                  <td className="colonne-actions">
                    <button
                      type="button"
                      className="btn-ghost btn-icon"
                      onClick={() => void restaurer(ligne)}
                      title={t("action.restaurer")}
                    >
                      <Undo2 className="icon icon-sm" strokeWidth={1.75} aria-hidden="true" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {lignes.length === 0 && !chargement ? (
            <p className="etat-vide">{t("corbeille.vide")}</p>
          ) : null}
        </div>
      </div>
    </section>
  );
}
