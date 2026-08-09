import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { CorbeilleView } from "../../src/renderer/src/views/CorbeilleView";
import { SessionContext, type SessionApi } from "../../src/renderer/src/hooks/useSession";
import { OuvragesContext, type OuvragesApi } from "../../src/renderer/src/hooks/useOuvrages";
import { ToastContext, type ToastApi } from "../../src/renderer/src/hooks/useToast";

const session: SessionApi = {
  etat: "pret",
  utilisateur: { id: 3, email: "q@example.com", nom_affichage: "Quentin" },
  messageMiseAJour: "",
  connecter: vi.fn(),
  deconnecter: vi.fn(),
  echouer: vi.fn(),
};

const toasts: ToastApi = { toast: vi.fn(), toastErreur: vi.fn(), fermer: vi.fn() };

const ouvrages = {
  toutes: [],
  lignes: [],
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
  champs: { localisation: false, periode: false, dateCreation: false, couvertures: false },
} as OuvragesApi;

describe("CorbeilleView", () => {
  it("se_rend_sans_crash_et_annonce_une_corbeille_vide", async () => {
    render(
      <ToastContext.Provider value={toasts}>
        <SessionContext.Provider value={session}>
          <OuvragesContext.Provider value={ouvrages}>
            <CorbeilleView />
          </OuvragesContext.Provider>
        </SessionContext.Provider>
      </ToastContext.Provider>,
    );

    expect(await screen.findByText(/la corbeille est vide/i)).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: /jours restants/i })).toBeInTheDocument();
  });
});
