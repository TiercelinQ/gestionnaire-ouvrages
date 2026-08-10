import { useRef, useState } from "react";
import {
  ChevronDown,
  ChevronUp,
  Download,
  Eraser,
  Pencil,
  Plus,
  RefreshCw,
  Trash2,
} from "lucide-react";
import type { OuvrageListe } from "../../../shared/types";
import { t, tp } from "../i18n";
import { useNomenclatures } from "../hooks/useNomenclatures";
import {
  LOCALISATION_ABSENTE,
  LOCALISATION_TOUTES,
  useOuvrages,
  type ColonneTri,
} from "../hooks/useOuvrages";
import { useSession } from "../hooks/useSession";
import { useToast } from "../hooks/useToast";
import { useVirtualRows } from "../hooks/useVirtualRows";
import { ConfirmModal } from "./layout/ConfirmModal";
import { OuvrageFormModal } from "./ouvrage/OuvrageFormModal";

/** `largeur` est la classe de largeur figée ; la colonne qui n'en porte pas absorbe le reste. */
const COLONNES: { cle: ColonneTri; libelle: string; largeur?: string }[] = [
  { cle: "auteur", libelle: t("ouvrage.auteur"), largeur: "colonne-large" },
  { cle: "titre", libelle: t("ouvrage.titre") },
  { cle: "edition", libelle: t("ouvrage.edition"), largeur: "colonne-large" },
  { cle: "categorie", libelle: t("ouvrage.categorie"), largeur: "colonne-large" },
];

/** Ouvrage visé par une suppression, avec la version lue au chargement de la liste. */
interface CibleSuppression {
  id: number;
  titre: string;
}

export function OuvragesView(): React.JSX.Element {
  const ouvrages = useOuvrages();
  const { nomenclatures } = useNomenclatures();
  const { echouer } = useSession();
  const { toast } = useToast();
  const conteneur = useRef<HTMLDivElement>(null);
  const fenetre = useVirtualRows(ouvrages.lignes.length, conteneur);

  const [fiche, setFiche] = useState<number | "nouveau" | null>(null);
  const [cible, setCible] = useState<CibleSuppression | null>(null);
  const [suppression, setSuppression] = useState(false);

  async function supprimer(): Promise<void> {
    if (!cible) return;
    setSuppression(true);
    // La version est relue sur la fiche : la liste ne la porte pas et le serveur l'exige.
    const courante = await window.api.ouvrageGet(cible.id);
    if (!courante.ok) {
      setSuppression(false);
      setCible(null);
      echouer(courante.error);
      return;
    }
    const resultat = await window.api.ouvrageDelete(cible.id, courante.data.version);
    setSuppression(false);
    setCible(null);
    if (!resultat.ok) {
      echouer(resultat.error);
      return;
    }
    toast("success", tp("ouvrage.supprime", { titre: cible.titre }));
    await ouvrages.recharger();
  }

  async function exporter(): Promise<void> {
    const resultat = await window.api.exportCsv(ouvrages.lignes);
    if (!resultat.ok) {
      echouer(resultat.error);
      return;
    }
    if (resultat.data) toast("success", t("export.reussi"), resultat.data);
  }

  const visibles = ouvrages.lignes.slice(fenetre.debut, fenetre.fin);

  return (
    <section className="vue">
      <header className="vue-entete">
        <h1 className="vue-titre">{t("onglet.ouvrages")}</h1>
        <p className="vue-sous-titre">{t("ouvrages.soustitre")}</p>
      </header>

      <div className="barre-outils">
        <input
          type="search"
          className="champ-recherche"
          placeholder={t("ouvrages.recherche")}
          value={ouvrages.recherche}
          onChange={(evenement) => ouvrages.setRecherche(evenement.target.value)}
          aria-label={t("ouvrages.recherche")}
        />

        {ouvrages.champs.localisation ? (
          <select
            className="champ-filtre"
            value={ouvrages.localisation}
            onChange={(evenement) => ouvrages.setLocalisation(evenement.target.value)}
            aria-label={t("ouvrage.localisation")}
          >
            <option value={LOCALISATION_TOUTES}>{t("filtre.toutes")}</option>
            <option value={LOCALISATION_ABSENTE}>{t("filtre.nonRenseignee")}</option>
            {nomenclatures.localisations.map((element) => (
              <option key={element.id} value={String(element.id)}>
                {element.nom}
              </option>
            ))}
          </select>
        ) : null}

        <button type="button" className="btn btn-secondary" onClick={ouvrages.effacerFiltres}>
          <Eraser className="icon icon-sm" strokeWidth={1.75} aria-hidden="true" />
          {t("action.effacer")}
        </button>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => void ouvrages.recharger()}
          disabled={ouvrages.chargement}
        >
          <RefreshCw className="icon icon-sm" strokeWidth={1.75} aria-hidden="true" />
          {t("action.actualiser")}
        </button>
        <button type="button" className="btn btn-secondary" onClick={() => void exporter()}>
          <Download className="icon icon-sm" strokeWidth={1.75} aria-hidden="true" />
          {t("action.exporter")}
        </button>
        <button type="button" className="btn btn-primary" onClick={() => setFiche("nouveau")}>
          <Plus className="icon icon-sm" strokeWidth={1.75} aria-hidden="true" />
          {t("ouvrages.ajouter")}
        </button>
      </div>

      <div className="table-cadre">
        {/* En-tête hors du conteneur défilant : la piste de défilement commence sous lui. */}
        <div className="table-entete">
          <table className="data-table">
            <thead>
              <tr>
                {COLONNES.map((colonne) => (
                  <th
                    key={colonne.cle}
                    className={colonne.largeur ? `is-sortable ${colonne.largeur}` : "is-sortable"}
                    onClick={() => ouvrages.basculerTri(colonne.cle)}
                    aria-sort={
                      ouvrages.colonne === colonne.cle
                        ? ouvrages.sens === "asc"
                          ? "ascending"
                          : "descending"
                        : "none"
                    }
                  >
                    {colonne.libelle}
                    {ouvrages.colonne === colonne.cle ? (
                      ouvrages.sens === "asc" ? (
                        <ChevronUp className="icon icon-sm" strokeWidth={1.75} aria-hidden="true" />
                      ) : (
                        <ChevronDown
                          className="icon icon-sm"
                          strokeWidth={1.75}
                          aria-hidden="true"
                        />
                      )
                    ) : null}
                  </th>
                ))}
                <th className="colonne-actions">{t("table.actions")}</th>
              </tr>
            </thead>
          </table>
        </div>

        <div className="table-defilante" ref={conteneur}>
          <table className="data-table">
            <colgroup>
              {COLONNES.map((colonne) => (
                <col key={colonne.cle} className={colonne.largeur} />
              ))}
              <col className="colonne-actions" />
            </colgroup>
            <tbody>
              {/* Espaceurs de virtualisation : hauteurs calculées au défilement, hors de portée du CSS. */}
              {fenetre.hauteurAvant > 0 ? (
                <tr
                  className="espaceur"
                  style={{ height: fenetre.hauteurAvant }}
                  aria-hidden="true"
                >
                  <td colSpan={5} />
                </tr>
              ) : null}

              {visibles.map((ligne: OuvrageListe) => (
                <tr
                  key={ligne.id}
                  className="ligne-ouvrage"
                  onDoubleClick={() => setFiche(ligne.id)}
                >
                  <td title={ligne.auteur}>{ligne.auteur}</td>
                  <td title={ligne.titre}>{ligne.titre}</td>
                  <td title={ligne.edition ?? ""}>{ligne.edition ?? ""}</td>
                  <td title={ligne.categorie_nom ?? ""}>{ligne.categorie_nom ?? ""}</td>
                  <td className="colonne-actions">
                    <button
                      type="button"
                      className="btn-ghost btn-icon"
                      onClick={() => setFiche(ligne.id)}
                      title={t("action.editer")}
                    >
                      <Pencil className="icon icon-sm" strokeWidth={1.75} aria-hidden="true" />
                    </button>
                    <button
                      type="button"
                      className="btn-ghost btn-icon"
                      onClick={() => setCible({ id: ligne.id, titre: ligne.titre })}
                      title={t("action.supprimer")}
                    >
                      <Trash2
                        className="icon icon-sm icon-danger"
                        strokeWidth={1.75}
                        aria-hidden="true"
                      />
                    </button>
                  </td>
                </tr>
              ))}

              {fenetre.hauteurApres > 0 ? (
                <tr
                  className="espaceur"
                  style={{ height: fenetre.hauteurApres }}
                  aria-hidden="true"
                >
                  <td colSpan={5} />
                </tr>
              ) : null}
            </tbody>
          </table>

          {ouvrages.lignes.length === 0 && !ouvrages.chargement ? (
            <p className="etat-vide">{t("ouvrages.aucun")}</p>
          ) : null}
        </div>
      </div>

      <OuvrageFormModal
        key={String(fiche)}
        cible={fiche}
        onFermer={() => setFiche(null)}
        onEnregistre={() => {
          setFiche(null);
          void ouvrages.recharger();
        }}
      />

      <ConfirmModal
        ouvert={cible !== null}
        titre={t("ouvrage.supprimerTitre")}
        message={tp("ouvrage.supprimerMessage", { titre: cible?.titre ?? "" })}
        libelleConfirmer={t("action.supprimer")}
        occupe={suppression}
        onConfirmer={() => void supprimer()}
        onAnnuler={() => setCible(null)}
      />
    </section>
  );
}
