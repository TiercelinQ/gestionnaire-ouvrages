import { useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";
import type {
  Nomenclature,
  NomenclatureInput,
  RessourceNomenclature,
} from "../../../../shared/types";
import { t, tp } from "../../i18n";
import { useNomenclatures } from "../../hooks/useNomenclatures";
import { useSession } from "../../hooks/useSession";
import { useToast } from "../../hooks/useToast";
import { ConfirmModal } from "../layout/ConfirmModal";
import { Modal } from "../layout/Modal";

interface Colonne {
  ressource: RessourceNomenclature;
  titre: string;
  elements: Nomenclature[];
  /** Identifiant du parent requis pour créer, `undefined` pour la racine. */
  parent?: number | null;
  selection: number | null;
  onSelection(id: number): void;
}

interface Edition {
  colonne: Colonne;
  element: Nomenclature;
}

/**
 * Classification hiérarchique en trois colonnes liées.
 *
 * Aucun verrouillage optimiste n'existe sur les nomenclatures : deux renommages simultanés
 * s'écrasent silencieusement. La liste est donc rechargée après chaque écriture.
 */
export function ClassificationPanel(): React.JSX.Element {
  const { nomenclatures, recharger } = useNomenclatures();
  const { echouer } = useSession();
  const { toast } = useToast();

  const [categorie, setCategorie] = useState<number | null>(null);
  const [genre, setGenre] = useState<number | null>(null);
  const [nouveaux, setNouveaux] = useState<Record<string, string>>({});
  const [edition, setEdition] = useState<Edition | null>(null);
  const [nomEdite, setNomEdite] = useState("");
  const [suppression, setSuppression] = useState<Edition | null>(null);
  const [occupe, setOccupe] = useState(false);

  const colonnes: Colonne[] = [
    {
      ressource: "categories",
      titre: t("classification.categories"),
      elements: nomenclatures.categories,
      selection: categorie,
      onSelection: (id) => {
        setCategorie(id);
        setGenre(null);
      },
    },
    {
      ressource: "genres",
      titre: t("classification.genres"),
      elements: nomenclatures.genres.filter((element) => element.id_categorie === categorie),
      parent: categorie,
      selection: genre,
      onSelection: setGenre,
    },
    {
      ressource: "sous-genres",
      titre: t("classification.sousGenres"),
      elements: nomenclatures.sous_genres.filter((element) => element.id_genre === genre),
      parent: genre,
      selection: null,
      onSelection: () => undefined,
    },
  ];

  function corpsAvecParent(colonne: Colonne, nom: string): NomenclatureInput {
    if (colonne.ressource === "genres") return { nom, id_categorie: colonne.parent ?? 0 };
    if (colonne.ressource === "sous-genres") return { nom, id_genre: colonne.parent ?? 0 };
    return { nom };
  }

  async function ajouter(colonne: Colonne): Promise<void> {
    const nom = (nouveaux[colonne.ressource] ?? "").trim();
    if (nom.length === 0) return;
    setOccupe(true);
    const resultat = await window.api.nomenclatureCreate(
      colonne.ressource,
      corpsAvecParent(colonne, nom),
    );
    setOccupe(false);
    if (!resultat.ok) {
      echouer(resultat.error);
      return;
    }
    setNouveaux((courant) => ({ ...courant, [colonne.ressource]: "" }));
    toast("success", tp("nomenclature.ajoutee", { nom: resultat.data.nom }));
    await recharger();
  }

  async function renommer(): Promise<void> {
    if (!edition) return;
    setOccupe(true);
    // Seul le nom est envoyé : la clé de rattachement omise conserve sa valeur actuelle.
    const resultat = await window.api.nomenclatureUpdate(edition.colonne.ressource, edition.element.id, {
      nom: nomEdite.trim(),
    });
    setOccupe(false);
    if (!resultat.ok) {
      echouer(resultat.error);
      return;
    }
    setEdition(null);
    toast("success", t("nomenclature.renommee"));
    await recharger();
  }

  async function supprimer(): Promise<void> {
    if (!suppression) return;
    setOccupe(true);
    const resultat = await window.api.nomenclatureDelete(
      suppression.colonne.ressource,
      suppression.element.id,
    );
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
      <h2 className="panneau-titre">{t("classification.titre")}</h2>
      <p className="texte-secondaire">{t("classification.aide")}</p>

      <div className="classification">
        {colonnes.map((colonne) => {
          const desactive = colonne.parent === null;
          return (
            <section key={colonne.ressource} className="classification-colonne">
              <h3 className="section-titre">{colonne.titre}</h3>

              <div className="ligne-ajout">
                <input
                  type="text"
                  value={nouveaux[colonne.ressource] ?? ""}
                  onChange={(evenement) =>
                    setNouveaux((courant) => ({
                      ...courant,
                      [colonne.ressource]: evenement.target.value,
                    }))
                  }
                  placeholder={t("nomenclature.nouveau")}
                  aria-label={colonne.titre}
                  disabled={desactive}
                />
                <button
                  type="button"
                  className="btn btn-primary btn-sm"
                  onClick={() => void ajouter(colonne)}
                  disabled={desactive || occupe || (nouveaux[colonne.ressource] ?? "").trim() === ""}
                >
                  <Plus className="icon icon-sm" strokeWidth={1.75} aria-hidden="true" />
                </button>
              </div>

              {desactive ? (
                <p className="etat-vide">{t("classification.selectionnerParent")}</p>
              ) : (
                <ul className="liste-simple">
                  {colonne.elements.map((element) => (
                    <li
                      key={element.id}
                      className={`liste-item${colonne.selection === element.id ? " is-selected" : ""}`}
                    >
                      <button
                        type="button"
                        className="liste-item-nom liste-item-bouton"
                        onClick={() => colonne.onSelection(element.id)}
                      >
                        {element.nom}
                      </button>
                      <span className="liste-item-actions">
                        <button
                          type="button"
                          className="btn-ghost btn-icon"
                          title={t("action.renommer")}
                          onClick={() => {
                            setEdition({ colonne, element });
                            setNomEdite(element.nom);
                          }}
                        >
                          <Pencil className="icon icon-sm" strokeWidth={1.75} aria-hidden="true" />
                        </button>
                        <button
                          type="button"
                          className="btn-ghost btn-icon"
                          title={t("action.supprimer")}
                          onClick={() => setSuppression({ colonne, element })}
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
              )}
            </section>
          );
        })}
      </div>

      <Modal
        ouvert={edition !== null}
        titre={t("nomenclature.renommer")}
        onFermer={() => setEdition(null)}
        pied={
          <div className="btn-group">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setEdition(null)}
              disabled={occupe}
            >
              {t("action.annuler")}
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => void renommer()}
              disabled={occupe || nomEdite.trim().length === 0}
            >
              {t("action.enregistrer")}
            </button>
          </div>
        }
      >
        <div className="champ">
          <label htmlFor="classification-nom">{t("nomenclature.nom")}</label>
          <input
            id="classification-nom"
            type="text"
            value={nomEdite}
            onChange={(evenement) => setNomEdite(evenement.target.value)}
          />
        </div>
      </Modal>

      <ConfirmModal
        ouvert={suppression !== null}
        titre={t("nomenclature.supprimer")}
        message={tp("nomenclature.supprimerMessage", { nom: suppression?.element.nom ?? "" })}
        libelleConfirmer={t("action.supprimer")}
        occupe={occupe}
        onConfirmer={() => void supprimer()}
        onAnnuler={() => setSuppression(null)}
      />
    </div>
  );
}
