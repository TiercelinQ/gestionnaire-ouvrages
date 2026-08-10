import { useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";
import type { Nomenclature, RessourceNomenclature } from "../../../../shared/types";
import { t, tp } from "../../i18n";
import { useNomenclatures } from "../../hooks/useNomenclatures";
import { useSession } from "../../hooks/useSession";
import { useToast } from "../../hooks/useToast";
import { ConfirmModal } from "../layout/ConfirmModal";
import { Modal } from "../layout/Modal";

export interface ListePanelProps {
  ressource: RessourceNomenclature;
  titre: string;
  elements: Nomenclature[];
}

/**
 * Generic panel for a simple list. The seven nomenclatures share an identical API
 * contract: one parameterised panel avoids four copies of the same screen.
 *
 * Server refusal messages are displayed as they come: they are already correctly worded
 * for the end user, and no machine-readable structure is provided to extract the counts.
 */
export function ListePanel({ ressource, titre, elements }: ListePanelProps): React.JSX.Element {
  const { recharger } = useNomenclatures();
  const { echouer } = useSession();
  const { toast } = useToast();

  const [nouveau, setNouveau] = useState("");
  const [renommage, setRenommage] = useState<Nomenclature | null>(null);
  const [nomRenomme, setNomRenomme] = useState("");
  const [suppression, setSuppression] = useState<Nomenclature | null>(null);
  const [occupe, setOccupe] = useState(false);

  async function ajouter(): Promise<void> {
    setOccupe(true);
    const resultat = await window.api.nomenclatureCreate(ressource, { nom: nouveau.trim() });
    setOccupe(false);
    if (!resultat.ok) {
      echouer(resultat.error);
      return;
    }
    setNouveau("");
    toast("success", tp("nomenclature.ajoutee", { nom: resultat.data.nom }));
    await recharger();
  }

  async function renommer(): Promise<void> {
    if (!renommage) return;
    setOccupe(true);
    const resultat = await window.api.nomenclatureUpdate(ressource, renommage.id, {
      nom: nomRenomme.trim(),
    });
    setOccupe(false);
    if (!resultat.ok) {
      echouer(resultat.error);
      return;
    }
    setRenommage(null);
    toast("success", t("nomenclature.renommee"));
    await recharger();
  }

  async function supprimer(): Promise<void> {
    if (!suppression) return;
    setOccupe(true);
    const resultat = await window.api.nomenclatureDelete(ressource, suppression.id);
    setOccupe(false);
    setSuppression(null);
    if (!resultat.ok) {
      echouer(resultat.error);
      return;
    }
    toast("success", t("nomenclature.supprimee"));
    await recharger();
  }

  return (
    <div className="panneau">
      <h2 className="panneau-titre">{titre}</h2>

      <div className="ligne-ajout">
        <input
          type="text"
          value={nouveau}
          onChange={(evenement) => setNouveau(evenement.target.value)}
          placeholder={t("nomenclature.nouveau")}
          aria-label={t("nomenclature.nouveau")}
        />
        <button
          type="button"
          className="btn btn-primary btn-sm"
          onClick={() => void ajouter()}
          disabled={occupe || nouveau.trim().length === 0}
        >
          <Plus className="icon icon-sm" strokeWidth={1.75} aria-hidden="true" />
          {t("action.ajouter")}
        </button>
      </div>

      <ul className="liste-simple">
        {elements.map((element) => (
          <li key={element.id} className="liste-item">
            <span className="liste-item-nom">{element.nom}</span>
            <span className="liste-item-actions">
              <button
                type="button"
                className="btn-ghost btn-icon"
                title={t("action.renommer")}
                onClick={() => {
                  setRenommage(element);
                  setNomRenomme(element.nom);
                }}
              >
                <Pencil className="icon icon-sm" strokeWidth={1.75} aria-hidden="true" />
              </button>
              <button
                type="button"
                className="btn-ghost btn-icon"
                title={t("action.supprimer")}
                onClick={() => setSuppression(element)}
              >
                <Trash2
                  className="icon icon-sm icon-danger"
                  strokeWidth={1.75}
                  aria-hidden="true"
                />
              </button>
            </span>
          </li>
        ))}
      </ul>

      {elements.length === 0 ? <p className="etat-vide">{t("nomenclature.aucune")}</p> : null}

      <Modal
        ouvert={renommage !== null}
        titre={t("nomenclature.renommer")}
        onFermer={() => setRenommage(null)}
        pied={
          <div className="btn-group">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setRenommage(null)}
              disabled={occupe}
            >
              {t("action.annuler")}
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => void renommer()}
              disabled={occupe || nomRenomme.trim().length === 0}
            >
              {t("action.enregistrer")}
            </button>
          </div>
        }
      >
        <div className="champ">
          <label htmlFor="renommage">{t("nomenclature.nom")}</label>
          <input
            id="renommage"
            type="text"
            value={nomRenomme}
            onChange={(evenement) => setNomRenomme(evenement.target.value)}
          />
        </div>
      </Modal>

      <ConfirmModal
        ouvert={suppression !== null}
        titre={t("nomenclature.supprimer")}
        message={tp("nomenclature.supprimerMessage", { nom: suppression?.nom ?? "" })}
        libelleConfirmer={t("action.supprimer")}
        occupe={occupe}
        onConfirmer={() => void supprimer()}
        onAnnuler={() => setSuppression(null)}
      />
    </div>
  );
}
