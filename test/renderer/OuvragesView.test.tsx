import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { OuvragesView } from "../../src/renderer/src/views/OuvragesView";
import { SessionContext, type SessionApi } from "../../src/renderer/src/hooks/useSession";
import { OuvragesContext, type OuvragesApi } from "../../src/renderer/src/hooks/useOuvrages";
import {
  NomenclaturesContext,
  type NomenclaturesApi,
} from "../../src/renderer/src/hooks/useNomenclatures";
import { ToastContext, type ToastApi } from "../../src/renderer/src/hooks/useToast";
import type { OuvrageListe } from "../../src/shared/types";

const session: SessionApi = {
  etat: "pret",
  utilisateur: { id: 3, email: "q@example.com", nom_affichage: "Quentin" },
  messageMiseAJour: "",
  connecter: vi.fn(),
  deconnecter: vi.fn(),
  echouer: vi.fn(),
};

const toasts: ToastApi = { toast: vi.fn(), toastErreur: vi.fn(), fermer: vi.fn() };

const nomenclatures: NomenclaturesApi = {
  nomenclatures: {
    categories: [],
    genres: [],
    sous_genres: [],
    illustrations: [],
    localisations: [{ id: 5, nom: "Salon" }],
    periodes: [],
    reliures: [],
  },
  chargement: false,
  recharger: vi.fn().mockResolvedValue(undefined),
};

const DUNE: OuvrageListe = {
  id: 128,
  titre: "Dune",
  auteur: "Frank Herbert",
  edition: "Robert Laffont",
  recherche_normalisee: "frank herbert dune robert laffont",
  categorie_nom: "Roman",
};

function ouvragesApi(champs: OuvragesApi["champs"]): OuvragesApi {
  return {
    toutes: [DUNE],
    lignes: [DUNE],
    chargement: false,
    recherche: "",
    setRecherche: vi.fn(),
    localisation: "toutes",
    setLocalisation: vi.fn(),
    colonne: "auteur",
    sens: "asc",
    basculerTri: vi.fn(),
    effacerFiltres: vi.fn(),
    recharger: vi.fn().mockResolvedValue(undefined),
    champs,
  };
}

function afficher(champs: OuvragesApi["champs"]): void {
  render(
    <ToastContext.Provider value={toasts}>
      <SessionContext.Provider value={session}>
        <NomenclaturesContext.Provider value={nomenclatures}>
          <OuvragesContext.Provider value={ouvragesApi(champs)}>
            <OuvragesView />
          </OuvragesContext.Provider>
        </NomenclaturesContext.Provider>
      </SessionContext.Provider>
    </ToastContext.Provider>,
  );
}

const SANS_ENRICHISSEMENT = {
  localisation: false,
  periode: false,
  dateCreation: false,
  couvertures: false,
};

describe("OuvragesView", () => {
  it("se_rend_sans_crash_et_expose_le_bouton_principal", () => {
    afficher(SANS_ENRICHISSEMENT);

    expect(screen.getByRole("button", { name: /ajouter un ouvrage/i })).toBeInTheDocument();
    expect(screen.getByText("Dune")).toBeInTheDocument();
  });

  it("masque_le_filtre_de_localisation_quand_l_api_ne_fournit_pas_le_champ", () => {
    afficher(SANS_ENRICHISSEMENT);

    expect(screen.queryByLabelText(/localisation/i)).not.toBeInTheDocument();
  });

  it("affiche_le_filtre_de_localisation_des_que_l_api_fournit_le_champ", () => {
    afficher({ ...SANS_ENRICHISSEMENT, localisation: true });

    expect(screen.getByLabelText(/localisation/i)).toBeInTheDocument();
  });
});
