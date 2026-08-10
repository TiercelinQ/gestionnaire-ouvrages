import { useEffect, useRef, useState, type FormEvent } from "react";
import { Library } from "lucide-react";
import * as config from "../../../shared/config";
import { CODE_COMPTE_BLOQUE, type IpcError } from "../../../shared/types";
import { t } from "../i18n";
import { useSession } from "../hooks/useSession";

/** Duration of the lockout the server applies after five consecutive failures. */
const BLOCAGE_MS = 15 * 60 * 1000;

export function LoginView(): React.JSX.Element {
  const { connecter } = useSession();
  const [email, setEmail] = useState("");
  const [motDePasse, setMotDePasse] = useState("");
  const [erreur, setErreur] = useState<IpcError | null>(null);
  const [envoi, setEnvoi] = useState(false);
  const [bloque, setBloque] = useState(false);
  const minuterie = useRef<number | null>(null);

  useEffect(
    () => () => {
      if (minuterie.current !== null) window.clearTimeout(minuterie.current);
    },
    [],
  );

  async function soumettre(evenement: FormEvent): Promise<void> {
    evenement.preventDefault();
    setEnvoi(true);
    setErreur(null);
    // The password is not kept beyond this call: no remember-me option.
    const echec = await connecter({ email, mot_de_passe: motDePasse });
    setEnvoi(false);
    if (!echec) return;

    setErreur(echec);
    setMotDePasse("");
    if (echec.code === CODE_COMPTE_BLOQUE) {
      setBloque(true);
      minuterie.current = window.setTimeout(() => setBloque(false), BLOCAGE_MS);
    }
  }

  const desactive = envoi || bloque || email.trim().length === 0 || motDePasse.length === 0;

  return (
    <main className="ecran-plein">
      <section className="carte carte-connexion">
        <Library className="icon icon-lg icon-active" strokeWidth={1.75} aria-hidden="true" />
        <h1 className="carte-titre">{config.APP_DISPLAY_NAME}</h1>
        <p className="texte-secondaire">{t("connexion.intro")}</p>

        <form className="formulaire" onSubmit={(evenement) => void soumettre(evenement)}>
          <div className="champ">
            <label htmlFor="email">{t("connexion.email")}</label>
            <input
              id="email"
              type="email"
              autoComplete="username"
              value={email}
              onChange={(evenement) => setEmail(evenement.target.value)}
              disabled={envoi || bloque}
              required
            />
          </div>

          <div className="champ">
            <label htmlFor="motdepasse">{t("connexion.motDePasse")}</label>
            <input
              id="motdepasse"
              type="password"
              autoComplete="current-password"
              value={motDePasse}
              onChange={(evenement) => setMotDePasse(evenement.target.value)}
              disabled={envoi || bloque}
              required
            />
          </div>

          {erreur ? (
            <p className="message-erreur" role="alert">
              {erreur.message}
            </p>
          ) : null}

          <button type="submit" className="btn btn-primary btn-lg" disabled={desactive}>
            {envoi ? t("connexion.enCours") : t("connexion.action")}
          </button>
        </form>
      </section>
    </main>
  );
}
