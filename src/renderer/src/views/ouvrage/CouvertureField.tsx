import { useEffect, useState } from "react";
import { FolderOpen, ImageOff, X } from "lucide-react";
import type { CouvertureResolue } from "../../../../shared/types";
import { t } from "../../i18n";
import { useSession } from "../../hooks/useSession";
import { ImagePreviewModal } from "../layout/ImagePreviewModal";

export interface CouvertureFieldProps {
  libelle: string;
  chemin: string | null;
  onChange(chemin: string | null, emplacement: string | null): void;
}

const MESSAGE_RAISON = {
  vide: "couverture.aucune",
  "racine-absente": "couverture.racineAbsente",
  introuvable: "couverture.introuvable",
  invalide: "couverture.invalide",
  ok: "couverture.aucune",
} as const;

/**
 * Champ de couverture : sélection, miniature, aperçu.
 *
 * L'API ne stocke aucun binaire, seulement le chemin. Le fichier choisi n'est ni copié
 * ni transmis : son chemin est enregistré tel quel.
 */
export function CouvertureField({
  libelle,
  chemin,
  onChange,
}: CouvertureFieldProps): React.JSX.Element {
  const { echouer } = useSession();
  const [resolue, setResolue] = useState<CouvertureResolue>({ dataUrl: null, raison: "vide" });
  const [apercu, setApercu] = useState(false);

  useEffect(() => {
    let annule = false;
    void (async () => {
      const resultat = await window.api.couvertureRead(chemin);
      if (annule) return;
      if (!resultat.ok) {
        echouer(resultat.error);
        return;
      }
      setResolue(resultat.data);
    })();
    return () => {
      annule = true;
    };
  }, [chemin, echouer]);

  async function choisir(): Promise<void> {
    const resultat = await window.api.couverturePick();
    if (!resultat.ok) {
      echouer(resultat.error);
      return;
    }
    // Chemin absolu du fichier choisi : l'emplacement suit la convention héritée de la v1.
    if (resultat.data) onChange(resultat.data, "Local");
  }

  return (
    <div className="couverture">
      <span className="champ-libelle">{libelle}</span>

      <div className="couverture-apercu">
        {resolue.dataUrl ? (
          <button type="button" className="couverture-vignette" onClick={() => setApercu(true)}>
            <img src={resolue.dataUrl} alt={libelle} />
          </button>
        ) : (
          <div className="couverture-absente">
            <ImageOff className="icon icon-md icon-muted" strokeWidth={1.75} aria-hidden="true" />
            <span className="texte-secondaire">{t(MESSAGE_RAISON[resolue.raison])}</span>
          </div>
        )}
      </div>

      {chemin ? <p className="couverture-chemin" title={chemin}>{chemin}</p> : null}

      <div className="couverture-actions">
        <button type="button" className="btn btn-secondary btn-sm" onClick={() => void choisir()}>
          <FolderOpen className="icon icon-sm" strokeWidth={1.75} aria-hidden="true" />
          {t("action.parcourir")}
        </button>
        {chemin ? (
          <button
            type="button"
            className="btn btn-ghost btn-sm"
            onClick={() => onChange(null, null)}
          >
            <X className="icon icon-sm" strokeWidth={1.75} aria-hidden="true" />
            {t("action.retirer")}
          </button>
        ) : null}
      </div>

      <ImagePreviewModal
        ouvert={apercu}
        titre={libelle}
        dataUrl={resolue.dataUrl}
        onFermer={() => setApercu(false)}
      />
    </div>
  );
}
