import { useCallback, useEffect, useState } from "react";
import { RefreshCw, Undo2 } from "lucide-react";
import type { OuvrageCorbeille } from "../../../shared/types";
import { t, tp } from "../i18n";
import { formaterDateHeure, formaterNombre } from "../utils/helpers";
import { useOuvrages } from "../hooks/useOuvrages";
import { useSession } from "../hooks/useSession";
import { useToast } from "../hooks/useToast";

/**
 * Corbeille. La purge est une tâche serveur quotidienne : un ouvrage à zéro jour restant
 * peut rester visible jusqu'à vingt-quatre heures, il n'est donc ni masqué ni grisé.
 */
export function CorbeilleView(): React.JSX.Element {
  const { echouer } = useSession();
  const { toast } = useToast();
  const ouvrages = useOuvrages();
  const [lignes, setLignes] = useState<OuvrageCorbeille[]>([]);
  // Vrai dès le montage : le chargement part immédiatement. Le bouton Actualiser repasse
  // l'indicateur à vrai depuis son gestionnaire, hors du corps de l'effet.
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

  // Chargement initial écrit dans l'effet, avec drapeau d'annulation : appeler `charger`
  // ici exposerait un setState hors du corps asynchrone de l'effet.
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
        {/* En-tête hors du conteneur défilant : la piste de défilement commence sous lui. */}
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
