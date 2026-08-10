import { useEffect, useMemo, useState } from "react";
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { OuvrageListe } from "../../../shared/types";
import { t, tp } from "../i18n";
import { formaterDate, formaterNombre } from "../utils/helpers";
import { useNomenclatures } from "../hooks/useNomenclatures";
import { LOCALISATION_TOUTES, useOuvrages } from "../hooks/useOuvrages";

/** The five visualisation tokens, cycled beyond five segments. */
const TOKENS_GRAPHIQUE = [
  "--chart-primary",
  "--chart-success",
  "--chart-warning",
  "--chart-danger",
  "--chart-info",
] as const;

/**
 * Reads the chart colours from the tokens and re-reads them when the theme changes.
 * Recharts expects colours as props: the values come from tokens.css, never from a
 * literal inside the component.
 */
function useCouleursGraphique(): string[] {
  const [couleurs, setCouleurs] = useState<string[]>([]);

  useEffect(() => {
    const lire = (): void => {
      const styles = getComputedStyle(document.documentElement);
      setCouleurs(TOKENS_GRAPHIQUE.map((token) => styles.getPropertyValue(token).trim()));
    };
    lire();
    const observateur = new MutationObserver(lire);
    observateur.observe(document.documentElement, { attributeFilter: ["data-theme"] });
    return () => observateur.disconnect();
  }, []);

  return couleurs;
}

interface Segment {
  name: string;
  value: number;
}

function agreger(lignes: OuvrageListe[], cle: (ligne: OuvrageListe) => string | null): Segment[] {
  const compte = new Map<string, number>();
  for (const ligne of lignes) {
    const valeur = cle(ligne) ?? t("filtre.nonRenseignee");
    compte.set(valeur, (compte.get(valeur) ?? 0) + 1);
  }
  return [...compte.entries()]
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);
}

export function DashboardView(): React.JSX.Element {
  const { toutes, champs } = useOuvrages();
  const { nomenclatures } = useNomenclatures();
  const couleurs = useCouleursGraphique();
  const [localisation, setLocalisation] = useState<string>(LOCALISATION_TOUTES);

  const lignes = useMemo(() => {
    if (!champs.localisation || localisation === LOCALISATION_TOUTES) return toutes;
    return toutes.filter((ligne) => String(ligne.id_localisation ?? "") === localisation);
  }, [toutes, champs.localisation, localisation]);

  const parCategorie = useMemo(() => agreger(lignes, (ligne) => ligne.categorie_nom), [lignes]);
  const parPeriode = useMemo(
    () => (champs.periode ? agreger(lignes, (ligne) => ligne.periode_nom ?? null) : []),
    [lignes, champs.periode],
  );

  const couvertures = useMemo(() => {
    if (!champs.couvertures) return null;
    const avecPremiere = lignes.filter((ligne) => ligne.a_couverture_premiere).length;
    const avecQuatrieme = lignes.filter((ligne) => ligne.a_couverture_quatrieme).length;
    return { avecPremiere, avecQuatrieme, total: lignes.length };
  }, [lignes, champs.couvertures]);

  const derniers = useMemo(() => {
    if (!champs.dateCreation) return [];
    return [...lignes]
      .sort((a, b) => (b.date_creation ?? "").localeCompare(a.date_creation ?? ""))
      .slice(0, 5);
  }, [lignes, champs.dateCreation]);

  return (
    <section className="vue">
      <header className="vue-entete">
        <h1 className="vue-titre">{t("onglet.dashboard")}</h1>
        <p className="vue-sous-titre">{t("dashboard.soustitre")}</p>
      </header>

      {champs.localisation ? (
        <div className="barre-outils">
          <select
            className="champ-filtre"
            value={localisation}
            onChange={(evenement) => setLocalisation(evenement.target.value)}
            aria-label={t("ouvrage.localisation")}
          >
            <option value={LOCALISATION_TOUTES}>{t("filtre.toutes")}</option>
            {nomenclatures.localisations.map((element) => (
              <option key={element.id} value={String(element.id)}>
                {element.nom}
              </option>
            ))}
          </select>
        </div>
      ) : null}

      <div className="tableau-bord">
        <div className="colonne-kpi">
          <article className="carte-kpi">
            <h2 className="kpi-titre">{t("kpi.total")}</h2>
            <p className="kpi-valeur">{formaterNombre(lignes.length)}</p>
          </article>

          <article className="carte-kpi">
            <h2 className="kpi-titre">{t("kpi.couvertures")}</h2>
            {couvertures ? (
              <ul className="kpi-liste">
                <li>
                  {tp("kpi.couverturePremiere", {
                    avec: formaterNombre(couvertures.avecPremiere),
                    total: formaterNombre(couvertures.total),
                  })}
                </li>
                <li>
                  {tp("kpi.couvertureQuatrieme", {
                    avec: formaterNombre(couvertures.avecQuatrieme),
                    total: formaterNombre(couvertures.total),
                  })}
                </li>
              </ul>
            ) : (
              <p className="etat-vide">{t("kpi.indisponible")}</p>
            )}
          </article>

          <article className="carte-kpi">
            <h2 className="kpi-titre">{t("kpi.topCategories")}</h2>
            {parCategorie.length > 0 ? (
              <ul className="kpi-liste">
                {parCategorie.slice(0, 3).map((segment) => (
                  <li key={segment.name}>
                    {segment.name}
                    <span className="kpi-compte">{formaterNombre(segment.value)}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="etat-vide">{t("dashboard.aucuneDonnee")}</p>
            )}
          </article>

          <article className="carte-kpi">
            <h2 className="kpi-titre">{t("kpi.derniersAjouts")}</h2>
            {champs.dateCreation ? (
              <ul className="kpi-liste">
                {derniers.map((ligne) => (
                  <li key={ligne.id} title={formaterDate(ligne.date_creation)}>
                    {ligne.titre}
                    <span className="kpi-compte">{ligne.auteur}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="etat-vide">{t("kpi.indisponible")}</p>
            )}
          </article>
        </div>

        <div className="colonne-graphiques">
          <article className="carte-graphique">
            <h2 className="kpi-titre">{t("graphique.parCategorie")}</h2>
            {parCategorie.length > 0 && couleurs.length > 0 ? (
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie data={parCategorie} dataKey="value" nameKey="name" outerRadius="80%">
                    {parCategorie.map((segment, index) => (
                      <Cell key={segment.name} fill={couleurs[index % couleurs.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="etat-vide">{t("dashboard.aucuneDonnee")}</p>
            )}
          </article>

          <article className="carte-graphique">
            <h2 className="kpi-titre">{t("graphique.parPeriode")}</h2>
            {!champs.periode ? (
              <p className="etat-vide">{t("kpi.indisponible")}</p>
            ) : parPeriode.length > 0 && couleurs.length > 0 ? (
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie data={parPeriode} dataKey="value" nameKey="name" outerRadius="80%">
                    {parPeriode.map((segment, index) => (
                      <Cell key={segment.name} fill={couleurs[index % couleurs.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="etat-vide">{t("dashboard.aucuneDonnee")}</p>
            )}
          </article>
        </div>
      </div>
    </section>
  );
}
