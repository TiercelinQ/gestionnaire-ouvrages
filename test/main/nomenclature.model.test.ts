import { describe, it, expect, vi, beforeEach } from "vitest";

const client = { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() };
vi.mock("../../src/main/models/api-client", () => ({ apiClient: client }));

const { nomenclatureModel, CLE_JSON } = await import("../../src/main/models/nomenclature.model");

describe("nomenclature.model", () => {
  beforeEach(() => {
    Object.values(client).forEach((methode) => methode.mockReset());
  });

  it("associe_le_segment_a_tirets_a_la_cle_json_a_tirets_bas", () => {
    expect(CLE_JSON["sous-genres"]).toBe("sous_genres");
    expect(CLE_JSON.categories).toBe("categories");
  });

  it("complete_les_sept_listes_meme_si_la_reponse_en_omet", async () => {
    client.get.mockResolvedValue({ ok: true, data: { categories: [{ id: 1, nom: "Roman" }] } });

    const resultat = await nomenclatureModel.list();

    expect(resultat.ok).toBe(true);
    if (resultat.ok) {
      expect(resultat.data.categories).toHaveLength(1);
      expect(resultat.data.reliures).toEqual([]);
      expect(resultat.data.sous_genres).toEqual([]);
    }
  });

  it("construit_l_url_avec_le_segment_a_trait_d_union", async () => {
    client.post.mockResolvedValue({ ok: true, data: { id: 51, nom: "Space opera" } });

    await nomenclatureModel.create("sous-genres", { nom: "Space opera", id_genre: 12 });

    expect(client.post).toHaveBeenCalledWith("/sous-genres", {
      corps: { nom: "Space opera", id_genre: 12 },
    });
  });

  it("supprime_sans_corps_de_requete", async () => {
    client.delete.mockResolvedValue({ ok: true, data: undefined });

    await nomenclatureModel.remove("categories", 1);

    expect(client.delete).toHaveBeenCalledWith("/categories/1");
  });
});
