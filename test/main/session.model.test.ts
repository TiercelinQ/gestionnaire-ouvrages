import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("electron", () => ({ app: { getVersion: () => "1.0.0" } }));
vi.mock("electron-log/main", () => ({
  default: { error: vi.fn(), warn: vi.fn(), info: vi.fn(), debug: vi.fn() },
}));
vi.mock("node:os", () => {
  // The `default` export is required: some dependencies import the whole module.
  const os = { hostname: () => "POSTE-TEST" };
  return { ...os, default: os };
});

const client = { get: vi.fn(), post: vi.fn() };
vi.mock("../../src/main/models/api-client", () => ({ apiClient: client }));

const session = { valeur: null as unknown };
const ecrireSession = vi.fn();
const effacerSession = vi.fn();
vi.mock("../../src/main/models/token-store", () => ({
  lireSession: () => session.valeur,
  ecrireSession: (valeur: unknown) => ecrireSession(valeur),
  effacerSession: () => effacerSession(),
}));

const { sessionModel } = await import("../../src/main/models/session.model");

const UTILISATEUR = { id: 3, email: "q@example.com", nom_affichage: "Quentin" };

describe("session.model", () => {
  beforeEach(() => {
    client.get.mockReset();
    client.post.mockReset();
    ecrireSession.mockReset();
    effacerSession.mockReset();
    session.valeur = null;
  });

  it("annonce_non_authentifie_sans_jeton_local_et_sans_appel_reseau", async () => {
    const resultat = await sessionModel.status();

    expect(resultat.ok && resultat.data.authentifie).toBe(false);
    expect(client.get).not.toHaveBeenCalled();
  });

  it("verifie_le_jeton_stocke_aupres_du_serveur", async () => {
    session.valeur = { jeton: "abc" };
    client.get.mockResolvedValue({ ok: true, data: UTILISATEUR });

    const resultat = await sessionModel.status();

    expect(client.get).toHaveBeenCalledWith("/moi");
    expect(resultat.ok && resultat.data.utilisateur?.nom_affichage).toBe("Quentin");
  });

  it("signale_une_mise_a_jour_requise_sur_un_refus_de_version", async () => {
    session.valeur = { jeton: "abc" };
    client.get.mockResolvedValue({
      ok: false,
      error: { type: "danger", code: "version_trop_ancienne", message: "Version 1.0.0 minimum" },
    });

    const resultat = await sessionModel.status();

    expect(resultat.ok && resultat.data.miseAJourRequise).toBe(true);
    expect(resultat.ok && resultat.data.message).toContain("1.0.0");
  });

  it("transmet_le_nom_de_machine_comme_appareil", async () => {
    client.post.mockResolvedValue({
      ok: true,
      data: { jeton: "abc", expire_le: "2026-09-08T14:22:07Z", utilisateur: UTILISATEUR },
    });

    await sessionModel.login({ email: "q@example.com", mot_de_passe: "secret" });

    expect(client.post).toHaveBeenCalledWith("/connexion", {
      mode: "version",
      corps: { email: "q@example.com", mot_de_passe: "secret", appareil: "POSTE-TEST" },
    });
    expect(ecrireSession).toHaveBeenCalledOnce();
  });

  it("n_ecrit_aucune_session_quand_la_connexion_echoue", async () => {
    client.post.mockResolvedValue({
      ok: false,
      error: { type: "danger", code: "identifiants_incorrects", message: "E-mail ou mot de passe incorrect" },
    });

    const resultat = await sessionModel.login({ email: "q@example.com", mot_de_passe: "faux" });

    expect(resultat.ok).toBe(false);
    expect(ecrireSession).not.toHaveBeenCalled();
  });

  it("efface_la_session_locale_meme_si_la_deconnexion_serveur_echoue", async () => {
    client.post.mockResolvedValue({
      ok: false,
      error: { type: "danger", code: "session_expiree", message: "Votre session a expiré" },
    });

    const resultat = await sessionModel.logout();

    expect(resultat.ok).toBe(true);
    expect(effacerSession).toHaveBeenCalledOnce();
  });

  it("renvoie_la_version_installee_meme_si_la_route_publique_est_muette", async () => {
    client.get.mockResolvedValue({ ok: false, error: { type: "danger", message: "X" } });

    const resultat = await sessionModel.appInfo();

    expect(resultat.ok).toBe(true);
    if (resultat.ok) {
      expect(resultat.data.version).toBe("1.0.0");
      expect(resultat.data.versionsMinimales).toBeUndefined();
    }
  });
});
