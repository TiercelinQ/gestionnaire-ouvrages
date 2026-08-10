import { describe, it, expect, vi, beforeEach } from "vitest";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { OuvrageFormModal } from "../../src/renderer/src/views/ouvrage/OuvrageFormModal";
import { SessionContext, type SessionApi } from "../../src/renderer/src/hooks/useSession";
import {
  NomenclaturesContext,
  type NomenclaturesApi,
} from "../../src/renderer/src/hooks/useNomenclatures";
import { ToastContext, type ToastApi } from "../../src/renderer/src/hooks/useToast";
import type { OuvrageFiche } from "../../src/shared/types";

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
    localisations: [],
    periodes: [],
    reliures: [],
  },
  chargement: false,
  recharger: vi.fn().mockResolvedValue(undefined),
};

const FICHE = {
  id: 128,
  titre: "Dune",
  auteur: "Frank Herbert",
  version: 4,
  recherche_normalisee: "frank herbert dune",
  date_creation: "2026-01-01T10:00:00Z",
  date_modification: "2026-01-02T10:00:00Z",
  cree_par: 3,
  modifie_par: 3,
  supprime_le: null,
  supprime_par: null,
} as unknown as OuvrageFiche;

function afficher(onFermer: () => void): { rerender: (onFermer: () => void) => void } {
  const arbre = (fermer: () => void): React.JSX.Element => (
    <ToastContext.Provider value={toasts}>
      <SessionContext.Provider value={session}>
        <NomenclaturesContext.Provider value={nomenclatures}>
          <OuvrageFormModal cible={128} onFermer={fermer} onEnregistre={vi.fn()} />
        </NomenclaturesContext.Provider>
      </SessionContext.Provider>
    </ToastContext.Provider>
  );
  const rendu = render(arbre(onFermer));
  return { rerender: (fermer: () => void) => rendu.rerender(arbre(fermer)) };
}

describe("OuvrageFormModal", () => {
  beforeEach(() => {
    vi.mocked(window.api.ouvrageGet).mockResolvedValue({ ok: true, data: FICHE });
  });

  it("charge_la_fiche_une_seule_fois_meme_si_l_appelant_recree_ses_rappels", async () => {
    const { rerender } = afficher(vi.fn());
    await waitFor(() => expect(screen.getByLabelText("Titre *")).toHaveValue("Dune"));

    // The api:status push re-renders the whole shell after each IPC call, so the caller
    // hands over a brand new closure. That must not re-trigger the load.
    rerender(vi.fn());
    rerender(vi.fn());

    expect(vi.mocked(window.api.ouvrageGet)).toHaveBeenCalledTimes(1);
  });

  it("conserve_la_saisie_quand_l_appelant_recree_ses_rappels", async () => {
    const { rerender } = afficher(vi.fn());
    await waitFor(() => expect(screen.getByLabelText("Titre *")).toHaveValue("Dune"));

    fireEvent.change(screen.getByLabelText("Titre *"), { target: { value: "Le Messie de Dune" } });
    rerender(vi.fn());
    // Flushes the pending promises: a reload triggered by the re-render would resolve here
    // and overwrite the field with the server value.
    await act(async () => {});

    expect(screen.getByLabelText("Titre *")).toHaveValue("Le Messie de Dune");
  });
});
