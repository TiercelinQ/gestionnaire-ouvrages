import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { LoginView } from "../../src/renderer/src/views/LoginView";
import { SessionContext, type SessionApi } from "../../src/renderer/src/hooks/useSession";

const session: SessionApi = {
  etat: "connexion",
  utilisateur: null,
  messageMiseAJour: "",
  connecter: vi.fn().mockResolvedValue(null),
  deconnecter: vi.fn(),
  echouer: vi.fn(),
};

function afficher(): void {
  render(
    <SessionContext.Provider value={session}>
      <LoginView />
    </SessionContext.Provider>,
  );
}

describe("LoginView", () => {
  it("se_rend_sans_crash_et_expose_les_deux_champs", () => {
    afficher();

    expect(screen.getByLabelText(/adresse e-mail/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/mot de passe/i)).toBeInTheDocument();
  });

  it("desactive_la_connexion_tant_que_les_champs_sont_vides", () => {
    afficher();

    expect(screen.getByRole("button", { name: /se connecter/i })).toBeDisabled();
  });
});
