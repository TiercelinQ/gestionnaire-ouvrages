import { createContext, useCallback, useContext, useEffect, useState } from "react";
import {
  CODE_SESSION_EXPIREE,
  CODE_VERSION_ANCIENNE,
  CODE_VERSION_INVALIDE,
  type Identifiants,
  type IpcError,
  type Utilisateur,
} from "../../../shared/types";
import { useToast } from "./useToast";

/** Écran affiché par la racine de l'application. */
export type EtatApplication = "chargement" | "connexion" | "mise-a-jour" | "pret";

export interface SessionApi {
  etat: EtatApplication;
  utilisateur: Utilisateur | null;
  /** Message serveur associé au refus de version, affiché tel quel. */
  messageMiseAJour: string;
  connecter(identifiants: Identifiants): Promise<IpcError | null>;
  deconnecter(): Promise<void>;
  /**
   * Traite une erreur d'appel : bascule d'écran sur session expirée ou refus de version,
   * toast sinon. À appeler sur tout `IpcResult` en échec.
   */
  echouer(erreur: IpcError): void;
}

export const SessionContext = createContext<SessionApi | null>(null);

export function useSession(): SessionApi {
  const api = useContext(SessionContext);
  if (!api) throw new Error("useSession doit être utilisé à l'intérieur de SessionContext.");
  return api;
}

function estRefusDeVersion(code: string | undefined): boolean {
  return code === CODE_VERSION_INVALIDE || code === CODE_VERSION_ANCIENNE;
}

/** État de session. Instancié une seule fois, par la racine de l'application. */
export function useSessionState(): SessionApi {
  const { toastErreur } = useToast();
  const [etat, setEtat] = useState<EtatApplication>("chargement");
  const [utilisateur, setUtilisateur] = useState<Utilisateur | null>(null);
  const [messageMiseAJour, setMessageMiseAJour] = useState("");

  useEffect(() => {
    let annule = false;
    void (async () => {
      const resultat = await window.api.sessionStatus();
      if (annule) return;
      if (!resultat.ok) {
        // Serveur injoignable au démarrage : on présente l'écran de connexion.
        toastErreur(resultat.error);
        setEtat("connexion");
        return;
      }
      if (resultat.data.miseAJourRequise) {
        setMessageMiseAJour(resultat.data.message ?? "");
        setEtat("mise-a-jour");
        return;
      }
      setUtilisateur(resultat.data.utilisateur ?? null);
      setEtat(resultat.data.authentifie ? "pret" : "connexion");
    })();
    return () => {
      annule = true;
    };
  }, [toastErreur]);

  const connecter = useCallback(async (identifiants: Identifiants): Promise<IpcError | null> => {
    const resultat = await window.api.sessionLogin(identifiants);
    if (!resultat.ok) {
      if (estRefusDeVersion(resultat.error.code)) {
        setMessageMiseAJour(resultat.error.message);
        setEtat("mise-a-jour");
        return null;
      }
      return resultat.error;
    }
    setUtilisateur(resultat.data);
    setEtat("pret");
    return null;
  }, []);

  const deconnecter = useCallback(async () => {
    await window.api.sessionLogout();
    setUtilisateur(null);
    setEtat("connexion");
  }, []);

  const echouer = useCallback(
    (erreur: IpcError) => {
      if (estRefusDeVersion(erreur.code)) {
        setMessageMiseAJour(erreur.message);
        setEtat("mise-a-jour");
        return;
      }
      if (erreur.code === CODE_SESSION_EXPIREE) {
        setUtilisateur(null);
        setEtat("connexion");
        toastErreur(erreur);
        return;
      }
      toastErreur(erreur);
    },
    [toastErreur],
  );

  return { etat, utilisateur, messageMiseAJour, connecter, deconnecter, echouer };
}
