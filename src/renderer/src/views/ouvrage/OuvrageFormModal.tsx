import { useCallback, useEffect, useState, type ChangeEvent } from "react";
import { History } from "lucide-react";
import {
  CODE_CONFLIT_VERSION,
  type Nomenclature,
  type OuvrageFiche,
  type OuvrageInput,
} from "../../../../shared/types";
import { t } from "../../i18n";
import { formaterDateHeure, versIdentifiant, videVersNull } from "../../utils/helpers";
import { useNomenclatures } from "../../hooks/useNomenclatures";
import { useSession } from "../../hooks/useSession";
import { useToast } from "../../hooks/useToast";
import { Modal } from "../layout/Modal";
import { CouvertureField } from "./CouvertureField";
import { HistoriqueDrawer } from "./HistoriqueDrawer";

export interface OuvrageFormModalProps {
  /** Identifiant à éditer, `"nouveau"` pour une création, `null` si la modale est fermée. */
  cible: number | "nouveau" | null;
  onFermer(): void;
  onEnregistre(): void;
}

const VIDE: OuvrageInput = {
  titre: "",
  sous_titre: null,
  auteur: "",
  auteur_2: null,
  titre_original: null,
  cycle: null,
  tome: null,
  id_illustration: null,
  id_categorie: null,
  id_genre: null,
  id_sous_genre: null,
  id_periode: null,
  edition: null,
  collection: null,
  edition_annee: null,
  edition_numero: null,
  edition_premiere_annee: null,
  isbn: null,
  id_reliure: null,
  nombre_page: null,
  dimension: null,
  id_localisation: null,
  localisation_details: null,
  resume: null,
  remarques: null,
  couverture_premiere_chemin: null,
  couverture_premiere_emplacement: null,
  couverture_quatrieme_chemin: null,
  couverture_quatrieme_emplacement: null,
};

/** Extrait les champs modifiables d'une fiche : le reste est calculé par le serveur. */
function versInput(fiche: OuvrageFiche): OuvrageInput {
  const input: Record<string, unknown> = {};
  for (const cle of Object.keys(VIDE)) input[cle] = fiche[cle as keyof OuvrageInput];
  return input as unknown as OuvrageInput;
}

export function OuvrageFormModal({
  cible,
  onFermer,
  onEnregistre,
}: OuvrageFormModalProps): React.JSX.Element {
  const { nomenclatures } = useNomenclatures();
  const { echouer } = useSession();
  const { toast } = useToast();

  const [form, setForm] = useState<OuvrageInput>(VIDE);
  const [fiche, setFiche] = useState<OuvrageFiche | null>(null);
  const [erreurChamp, setErreurChamp] = useState<{ champ: string; message: string } | null>(null);
  const [conflit, setConflit] = useState<string | null>(null);
  // Une édition démarre en chargement, une création non : la modale est remontée à chaque cible.
  const [chargement, setChargement] = useState(typeof cible === "number");
  const [envoi, setEnvoi] = useState(false);
  const [historique, setHistorique] = useState(false);

  const edition = typeof cible === "number";

  const charger = useCallback(
    async (id: number) => {
      setChargement(true);
      const resultat = await window.api.ouvrageGet(id);
      setChargement(false);
      if (!resultat.ok) {
        echouer(resultat.error);
        onFermer();
        return;
      }
      setFiche(resultat.data);
      setForm(versInput(resultat.data));
      setConflit(null);
      setErreurChamp(null);
    },
    [echouer, onFermer],
  );

  // Le composant est remonté à chaque changement de cible (clé côté appelant) : une création
  // repart d'un état vierge, et le chargement d'une fiche s'écrit dans l'effet lui-même.
  useEffect(() => {
    if (typeof cible !== "number") return;
    let annule = false;
    void (async () => {
      const resultat = await window.api.ouvrageGet(cible);
      if (annule) return;
      setChargement(false);
      if (!resultat.ok) {
        echouer(resultat.error);
        onFermer();
        return;
      }
      setFiche(resultat.data);
      setForm(versInput(resultat.data));
    })();
    return () => {
      annule = true;
    };
  }, [cible, echouer, onFermer]);

  function modifier<K extends keyof OuvrageInput>(cle: K, valeur: OuvrageInput[K]): void {
    setForm((courant) => ({ ...courant, [cle]: valeur }));
  }

  /**
   * Changer un parent réinitialise ses enfants : le formulaire ne doit jamais produire
   * une combinaison partielle, le serveur ne contrôlant que les paires effectivement fournies.
   */
  function changerCategorie(valeur: string): void {
    setForm((courant) => ({
      ...courant,
      id_categorie: versIdentifiant(valeur),
      id_genre: null,
      id_sous_genre: null,
    }));
  }

  function changerGenre(valeur: string): void {
    setForm((courant) => ({
      ...courant,
      id_genre: versIdentifiant(valeur),
      id_sous_genre: null,
    }));
  }

  async function enregistrer(): Promise<void> {
    setEnvoi(true);
    setErreurChamp(null);
    setConflit(null);

    const resultat =
      edition && fiche
        ? await window.api.ouvrageUpdate(fiche.id, { ...form, version: fiche.version })
        : await window.api.ouvrageCreate(form);

    setEnvoi(false);

    if (!resultat.ok) {
      if (resultat.error.code === CODE_CONFLIT_VERSION) {
        setConflit(resultat.error.message);
        return;
      }
      if (resultat.error.champ) {
        setErreurChamp({ champ: resultat.error.champ, message: resultat.error.message });
        return;
      }
      echouer(resultat.error);
      return;
    }

    toast("success", edition ? t("ouvrage.modifie") : t("ouvrage.cree"));
    onEnregistre();
  }

  const genresFiltres = nomenclatures.genres.filter(
    (genre) => genre.id_categorie === form.id_categorie,
  );
  const sousGenresFiltres = nomenclatures.sous_genres.filter(
    (sousGenre) => sousGenre.id_genre === form.id_genre,
  );

  function messageChamp(nom: keyof OuvrageInput): string | null {
    return erreurChamp?.champ === nom ? erreurChamp.message : null;
  }

  function champTexte(
    nom: keyof OuvrageInput,
    libelle: string,
    obligatoire = false,
  ): React.JSX.Element {
    const erreur = messageChamp(nom);
    const valeur = (form[nom] as string | null) ?? "";
    return (
      <div className={`champ${erreur ? " has-error" : ""}`}>
        <label htmlFor={`champ-${nom}`}>
          {libelle}
          {obligatoire ? <span className="champ-requis"> *</span> : null}
        </label>
        <input
          id={`champ-${nom}`}
          type="text"
          value={valeur}
          onChange={(evenement: ChangeEvent<HTMLInputElement>) =>
            modifier(
              nom,
              (obligatoire
                ? evenement.target.value
                : videVersNull(evenement.target.value)) as OuvrageInput[typeof nom],
            )
          }
        />
        {erreur ? <p className="champ-erreur">{erreur}</p> : null}
      </div>
    );
  }

  function champZone(nom: keyof OuvrageInput, libelle: string): React.JSX.Element {
    return (
      <div className="champ">
        <label htmlFor={`champ-${nom}`}>{libelle}</label>
        <textarea
          id={`champ-${nom}`}
          rows={5}
          value={(form[nom] as string | null) ?? ""}
          onChange={(evenement) =>
            modifier(nom, videVersNull(evenement.target.value) as OuvrageInput[typeof nom])
          }
        />
      </div>
    );
  }

  function champListe(
    nom: keyof OuvrageInput,
    libelle: string,
    options: Nomenclature[],
    surChangement?: (valeur: string) => void,
  ): React.JSX.Element {
    const erreur = messageChamp(nom);
    return (
      <div className={`champ${erreur ? " has-error" : ""}`}>
        <label htmlFor={`champ-${nom}`}>{libelle}</label>
        <select
          id={`champ-${nom}`}
          value={form[nom] === null ? "" : String(form[nom])}
          onChange={(evenement) =>
            surChangement
              ? surChangement(evenement.target.value)
              : modifier(nom, versIdentifiant(evenement.target.value) as OuvrageInput[typeof nom])
          }
        >
          <option value="">{t("champ.nonRenseigne")}</option>
          {options.map((option) => (
            <option key={option.id} value={String(option.id)}>
              {option.nom}
            </option>
          ))}
        </select>
        {erreur ? <p className="champ-erreur">{erreur}</p> : null}
      </div>
    );
  }

  return (
    <>
      <Modal
        ouvert={cible !== null}
        titre={edition ? t("ouvrage.editerTitre") : t("ouvrage.ajouterTitre")}
        taille="large"
        onFermer={onFermer}
        pied={
          <div className="btn-group">
            <button type="button" className="btn btn-secondary" onClick={onFermer} disabled={envoi}>
              {t("action.annuler")}
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => void enregistrer()}
              disabled={envoi || chargement}
            >
              {edition ? t("action.enregistrer") : t("ouvrages.ajouter")}
            </button>
          </div>
        }
      >
        {chargement ? <p className="etat-vide">{t("etat.chargement")}</p> : null}

        {conflit ? (
          <div className="bandeau-conflit" role="alert">
            <p className="texte-corps">{conflit}</p>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => fiche && void charger(fiche.id)}
            >
              {t("ouvrage.recharger")}
            </button>
          </div>
        ) : null}

        <form className="formulaire-fiche" onSubmit={(evenement) => evenement.preventDefault()}>
          <section className="colonne-fiche">
            <h3 className="section-titre">{t("fiche.identification")}</h3>
            {champTexte("auteur", t("ouvrage.auteur"), true)}
            {champTexte("auteur_2", t("ouvrage.auteur2"))}
            {champTexte("titre", t("ouvrage.titre"), true)}
            {champTexte("sous_titre", t("ouvrage.sousTitre"))}
            {champTexte("titre_original", t("ouvrage.titreOriginal"))}
            {champTexte("cycle", t("ouvrage.cycle"))}
            {champTexte("tome", t("ouvrage.tome"))}
            {champListe("id_illustration", t("ouvrage.illustration"), nomenclatures.illustrations)}
          </section>

          <section className="colonne-fiche">
            <h3 className="section-titre">{t("fiche.classification")}</h3>
            {champListe(
              "id_categorie",
              t("ouvrage.categorie"),
              nomenclatures.categories,
              changerCategorie,
            )}
            {champListe("id_genre", t("ouvrage.genre"), genresFiltres, changerGenre)}
            {champListe("id_sous_genre", t("ouvrage.sousGenre"), sousGenresFiltres)}
            {champListe("id_periode", t("ouvrage.periode"), nomenclatures.periodes)}

            <h3 className="section-titre">{t("fiche.publication")}</h3>
            {champTexte("edition", t("ouvrage.edition"))}
            {champTexte("collection", t("ouvrage.collection"))}
            {champTexte("edition_annee", t("ouvrage.editionAnnee"))}
            {champTexte("edition_numero", t("ouvrage.editionNumero"))}
            {champTexte("edition_premiere_annee", t("ouvrage.editionPremiereAnnee"))}
            {champTexte("isbn", t("ouvrage.isbn"))}

            <h3 className="section-titre">{t("fiche.format")}</h3>
            {champListe("id_reliure", t("ouvrage.reliure"), nomenclatures.reliures)}
            {champTexte("nombre_page", t("ouvrage.nombrePage"))}
            {champTexte("dimension", t("ouvrage.dimension"))}
            {champListe("id_localisation", t("ouvrage.localisation"), nomenclatures.localisations)}
            {champTexte("localisation_details", t("ouvrage.localisationDetails"))}
          </section>

          <section className="colonne-fiche">
            <h3 className="section-titre">{t("fiche.contenu")}</h3>
            {champZone("resume", t("ouvrage.resume"))}
            {champZone("remarques", t("ouvrage.remarques"))}

            <h3 className="section-titre">{t("fiche.couvertures")}</h3>
            <CouvertureField
              libelle={t("ouvrage.couverturePremiere")}
              chemin={form.couverture_premiere_chemin}
              onChange={(chemin, emplacement) =>
                setForm((courant) => ({
                  ...courant,
                  couverture_premiere_chemin: chemin,
                  couverture_premiere_emplacement: emplacement,
                }))
              }
            />
            <CouvertureField
              libelle={t("ouvrage.couvertureQuatrieme")}
              chemin={form.couverture_quatrieme_chemin}
              onChange={(chemin, emplacement) =>
                setForm((courant) => ({
                  ...courant,
                  couverture_quatrieme_chemin: chemin,
                  couverture_quatrieme_emplacement: emplacement,
                }))
              }
            />

            {fiche ? (
              <>
                <h3 className="section-titre">{t("fiche.systeme")}</h3>
                <dl className="liste-definition">
                  <dt>{t("fiche.creeLe")}</dt>
                  <dd>{formaterDateHeure(fiche.date_creation)}</dd>
                  <dt>{t("fiche.modifieLe")}</dt>
                  <dd>{formaterDateHeure(fiche.date_modification)}</dd>
                  <dt>{t("fiche.version")}</dt>
                  <dd>{fiche.version}</dd>
                </dl>
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={() => setHistorique(true)}
                >
                  <History className="icon icon-sm" strokeWidth={1.75} aria-hidden="true" />
                  {t("historique.ouvrir")}
                </button>
              </>
            ) : null}
          </section>
        </form>
      </Modal>

      <HistoriqueDrawer
        key={`${fiche?.id ?? 0}-${historique ? "ouvert" : "ferme"}`}
        ouvert={historique}
        ouvrageId={fiche?.id ?? null}
        onFermer={() => setHistorique(false)}
      />
    </>
  );
}
