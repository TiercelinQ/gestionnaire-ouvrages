import { useState } from "react";
import type { Theme } from "../../../shared/types";
import { t } from "../i18n";
import { useNomenclatures } from "../hooks/useNomenclatures";
import { ClassificationPanel } from "./parametres/ClassificationPanel";
import { ListePanel } from "./parametres/ListePanel";
import { PreferencesPanel } from "./parametres/PreferencesPanel";

type Rubrique =
  "classification" | "illustrations" | "periodes" | "reliures" | "localisations" | "preferences";

const RUBRIQUES: { cle: Rubrique; libelle: string }[] = [
  { cle: "classification", libelle: t("classification.titre") },
  { cle: "illustrations", libelle: t("liste.illustrations") },
  { cle: "periodes", libelle: t("liste.periodes") },
  { cle: "reliures", libelle: t("liste.reliures") },
  { cle: "localisations", libelle: t("liste.localisations") },
  { cle: "preferences", libelle: t("preferences.titre") },
];

export interface ParametresViewProps {
  theme: Theme;
  onTheme(): void;
}

export function ParametresView({ theme, onTheme }: ParametresViewProps): React.JSX.Element {
  const { nomenclatures } = useNomenclatures();
  const [rubrique, setRubrique] = useState<Rubrique>("classification");

  function panneau(): React.JSX.Element {
    switch (rubrique) {
      case "classification":
        return <ClassificationPanel />;
      case "illustrations":
        return (
          <ListePanel
            ressource="illustrations"
            titre={t("liste.illustrations")}
            elements={nomenclatures.illustrations}
          />
        );
      case "periodes":
        return (
          <ListePanel
            ressource="periodes"
            titre={t("liste.periodes")}
            elements={nomenclatures.periodes}
          />
        );
      case "reliures":
        return (
          <ListePanel
            ressource="reliures"
            titre={t("liste.reliures")}
            elements={nomenclatures.reliures}
          />
        );
      case "localisations":
        return (
          <ListePanel
            ressource="localisations"
            titre={t("liste.localisations")}
            elements={nomenclatures.localisations}
          />
        );
      case "preferences":
        return <PreferencesPanel theme={theme} onTheme={onTheme} />;
    }
  }

  return (
    <section className="vue">
      <header className="vue-entete">
        <h1 className="vue-titre">{t("onglet.parametres")}</h1>
        <p className="vue-sous-titre">{t("parametres.soustitre")}</p>
      </header>

      <div className="parametres">
        <nav id="params-nav" aria-label={t("parametres.rubriques")}>
          {RUBRIQUES.map((element) => (
            <button
              key={element.cle}
              type="button"
              className={`nav-item${element.cle === rubrique ? " is-active" : ""}`}
              onClick={() => setRubrique(element.cle)}
              aria-current={element.cle === rubrique ? "true" : undefined}
            >
              {element.libelle}
            </button>
          ))}
        </nav>

        <div className="parametres-contenu">{panneau()}</div>
      </div>
    </section>
  );
}
