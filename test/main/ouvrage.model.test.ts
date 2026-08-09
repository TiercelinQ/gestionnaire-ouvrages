import { describe, it, expect, vi, beforeEach } from "vitest";

const client = { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() };
vi.mock("../../src/main/models/api-client", () => ({ apiClient: client }));

const { ouvrageModel } = await import("../../src/main/models/ouvrage.model");

describe("ouvrage.model", () => {
  beforeEach(() => {
    Object.values(client).forEach((methode) => methode.mockReset());
  });

  it("deballe_l_enveloppe_de_la_liste", async () => {
    client.get.mockResolvedValue({ ok: true, data: { ouvrages: [{ id: 1 }] } });

    const resultat = await ouvrageModel.list();

    expect(resultat.ok && resultat.data).toEqual([{ id: 1 }]);
  });

  it("renvoie_une_liste_vide_si_l_enveloppe_est_incomplete", async () => {
    client.get.mockResolvedValue({ ok: true, data: {} });

    const resultat = await ouvrageModel.list();

    expect(resultat.ok && resultat.data).toEqual([]);
  });

  it("propage_l_erreur_sans_la_transformer", async () => {
    client.get.mockResolvedValue({ ok: false, error: { type: "danger", message: "X" } });

    const resultat = await ouvrageModel.list();

    expect(resultat.ok).toBe(false);
  });

  it("envoie_la_version_dans_le_corps_de_la_suppression", async () => {
    client.delete.mockResolvedValue({ ok: true, data: undefined });

    await ouvrageModel.remove(128, 4);

    expect(client.delete).toHaveBeenCalledWith("/ouvrages/128", { version: 4 });
  });

  it("appelle_la_route_de_restauration_sans_corps", async () => {
    client.post.mockResolvedValue({ ok: true, data: {} });

    await ouvrageModel.restore(128);

    expect(client.post).toHaveBeenCalledWith("/ouvrages/128/restaurer");
  });

  it("deballe_l_enveloppe_de_l_historique", async () => {
    client.get.mockResolvedValue({ ok: true, data: { historique: [{ id: 842 }] } });

    const resultat = await ouvrageModel.history(128);

    expect(resultat.ok && resultat.data).toHaveLength(1);
  });
});
