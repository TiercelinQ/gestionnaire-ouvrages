import { Component, useEffect, useState, type ErrorInfo, type ReactNode } from "react";
import type { Preferences, Theme } from "../../shared/types";
import { t } from "./i18n";
import { useApiStatus } from "./hooks/useApiStatus";
import { NomenclaturesContext, useNomenclaturesState } from "./hooks/useNomenclatures";
import { OuvragesContext, useOuvragesState } from "./hooks/useOuvrages";
import { SessionContext, useSession, useSessionState } from "./hooks/useSession";
import { useTheme } from "./hooks/useTheme";
import { CorbeilleView } from "./views/CorbeilleView";
import { DashboardView } from "./views/DashboardView";
import { LoginView } from "./views/LoginView";
import { OuvragesView } from "./views/OuvragesView";
import { ParametresView } from "./views/ParametresView";
import { ToastProvider } from "./views/ToastManager";
import { UpdateRequiredView } from "./views/UpdateRequiredView";
import { AProposModal } from "./views/layout/AProposModal";
import { Statusbar } from "./views/layout/Statusbar";
import { ONGLETS, Topbar, type Onglet } from "./views/layout/Topbar";

/** Dernier filet côté rendu : une erreur non interceptée n'efface pas la fenêtre. */
class ErrorBoundary extends Component<{ children: ReactNode }, { erreur: boolean }> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { erreur: false };
  }

  static getDerivedStateFromError(): { erreur: boolean } {
    return { erreur: true };
  }

  componentDidCatch(erreur: Error, infos: ErrorInfo): void {
    // La console du rendu est relayée dans le journal fichier par electron-log.
    window.console.error(erreur, infos.componentStack);
  }

  render(): ReactNode {
    if (!this.state.erreur) return this.props.children;
    return (
      <main className="ecran-plein">
        <section className="carte carte-message">
          <h1 className="carte-titre">{t("erreur.inattendue")}</h1>
          <p className="texte-corps">{t("erreur.rechargez")}</p>
        </section>
      </main>
    );
  }
}

export function App(): React.JSX.Element {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <ChargementPreferences />
      </ToastProvider>
    </ErrorBoundary>
  );
}

/** Charge les préférences avant tout rendu dépendant du thème, pour éviter un basculement visible. */
function ChargementPreferences(): React.JSX.Element {
  const [preferences, setPreferences] = useState<Preferences | null>(null);

  useEffect(() => {
    let annule = false;
    void (async () => {
      const resultat = await window.api.getPreferences();
      if (annule) return;
      setPreferences(resultat.ok ? resultat.data : { theme: null, coversRoot: null, windowBounds: null });
    })();
    return () => {
      annule = true;
    };
  }, []);

  if (!preferences) return <Attente />;
  return <Session themeInitial={preferences.theme} />;
}

function Session({ themeInitial }: { themeInitial: Preferences["theme"] }): React.JSX.Element {
  const session = useSessionState();
  const { theme, basculer } = useTheme(themeInitial);

  return (
    <SessionContext.Provider value={session}>
      <Routeur theme={theme} onTheme={basculer} />
    </SessionContext.Provider>
  );
}

function Attente(): React.JSX.Element {
  return (
    <main className="ecran-plein">
      <p className="etat-vide">{t("etat.chargement")}</p>
    </main>
  );
}

interface RouteurProps {
  theme: Theme;
  onTheme(): void;
}

function Routeur({ theme, onTheme }: RouteurProps): React.JSX.Element {
  const session = useSession();

  if (session.etat === "chargement") return <Attente />;
  if (session.etat === "mise-a-jour") return <UpdateRequiredView message={session.messageMiseAJour} />;
  if (session.etat === "connexion") return <LoginView />;
  return <Shell theme={theme} onTheme={onTheme} />;
}

function Shell({ theme, onTheme }: RouteurProps): React.JSX.Element {
  const session = useSession();
  const statut = useApiStatus();
  const nomenclatures = useNomenclaturesState(true);
  const ouvrages = useOuvragesState(true);
  const [onglet, setOnglet] = useState<Onglet>("ouvrages");
  const [apropos, setApropos] = useState(false);
  const [version, setVersion] = useState("");

  useEffect(() => {
    let annule = false;
    void (async () => {
      const resultat = await window.api.appInfo();
      if (!annule && resultat.ok) setVersion(resultat.data.version);
    })();
    return () => {
      annule = true;
    };
  }, []);

  useEffect(() => {
    const surTouche = (evenement: KeyboardEvent): void => {
      if (evenement.altKey) {
        const index = Number.parseInt(evenement.key, 10) - 1;
        const cible = ONGLETS[index];
        if (cible) {
          evenement.preventDefault();
          setOnglet(cible.cle);
        }
        return;
      }
      if (evenement.ctrlKey && evenement.key === ",") {
        evenement.preventDefault();
        setOnglet("parametres");
      }
    };
    window.addEventListener("keydown", surTouche);
    return () => window.removeEventListener("keydown", surTouche);
  }, []);

  const occupe = ouvrages.chargement || nomenclatures.chargement;

  return (
    <NomenclaturesContext.Provider value={nomenclatures}>
      <OuvragesContext.Provider value={ouvrages}>
        <div id="app-shell">
          <Topbar
            onglet={onglet}
            onOnglet={setOnglet}
            utilisateur={session.utilisateur}
            theme={theme}
            onTheme={onTheme}
            onAPropos={() => setApropos(true)}
            onDeconnexion={() => void session.deconnecter()}
          />

          <main id="main-content">
            {onglet === "dashboard" ? <DashboardView /> : null}
            {onglet === "ouvrages" ? <OuvragesView /> : null}
            {onglet === "corbeille" ? <CorbeilleView /> : null}
            {onglet === "parametres" ? <ParametresView theme={theme} onTheme={onTheme} /> : null}
          </main>

          <Statusbar
            message={occupe ? t("etat.chargement") : t("etat.pret")}
            occupe={occupe}
            affiches={ouvrages.lignes.length}
            total={ouvrages.toutes.length}
            version={version}
            statut={statut}
          />

          <AProposModal ouvert={apropos} onFermer={() => setApropos(false)} />
        </div>
      </OuvragesContext.Provider>
    </NomenclaturesContext.Provider>
  );
}
