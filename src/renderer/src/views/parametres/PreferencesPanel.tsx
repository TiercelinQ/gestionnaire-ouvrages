import { useEffect, useState } from "react";
import { FolderOpen, Moon, Sun } from "lucide-react";
import type { Theme } from "../../../../shared/types";
import { t } from "../../i18n";
import { useSession } from "../../hooks/useSession";
import { useToast } from "../../hooks/useToast";

export interface PreferencesPanelProps {
  theme: Theme;
  onTheme(): void;
}

/** Préférences locales. Le jeton de session n'y figure jamais : il est chiffré à part. */
export function PreferencesPanel({ theme, onTheme }: PreferencesPanelProps): React.JSX.Element {
  const { utilisateur, echouer } = useSession();
  const { toast } = useToast();
  const [dossier, setDossier] = useState<string | null>(null);

  useEffect(() => {
    let annule = false;
    void (async () => {
      const resultat = await window.api.getPreferences();
      if (!annule && resultat.ok) setDossier(resultat.data.coversRoot);
    })();
    return () => {
      annule = true;
    };
  }, []);

  async function choisirDossier(): Promise<void> {
    const resultat = await window.api.pickCoversFolder();
    if (!resultat.ok) {
      echouer(resultat.error);
      return;
    }
    if (!resultat.data) return;
    setDossier(resultat.data);
    toast("success", t("preferences.dossierEnregistre"));
  }

  return (
    <div className="panneau">
      <h2 className="panneau-titre">{t("preferences.titre")}</h2>

      <section className="bloc-preference">
        <h3 className="section-titre">{t("preferences.compte")}</h3>
        <dl className="liste-definition">
          <dt>{t("preferences.nom")}</dt>
          <dd>{utilisateur?.nom_affichage ?? "—"}</dd>
          <dt>{t("preferences.email")}</dt>
          <dd>{utilisateur?.email ?? "—"}</dd>
        </dl>
      </section>

      <section className="bloc-preference">
        <h3 className="section-titre">{t("preferences.couvertures")}</h3>
        <p className="texte-secondaire">{t("preferences.couverturesAide")}</p>
        <p className="chemin-dossier">{dossier ?? t("preferences.aucunDossier")}</p>
        <button type="button" className="btn btn-secondary btn-sm" onClick={() => void choisirDossier()}>
          <FolderOpen className="icon icon-sm" strokeWidth={1.75} aria-hidden="true" />
          {t("action.parcourir")}
        </button>
      </section>

      <section className="bloc-preference">
        <h3 className="section-titre">{t("preferences.apparence")}</h3>
        <button type="button" className="btn btn-secondary btn-sm" onClick={onTheme}>
          {theme === "dark" ? (
            <Sun className="icon icon-sm" strokeWidth={1.75} aria-hidden="true" />
          ) : (
            <Moon className="icon icon-sm" strokeWidth={1.75} aria-hidden="true" />
          )}
          {theme === "dark" ? t("theme.clair") : t("theme.sombre")}
        </button>
      </section>
    </div>
  );
}
