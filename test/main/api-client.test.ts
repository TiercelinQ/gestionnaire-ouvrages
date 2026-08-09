import { describe, it, expect, vi, beforeEach } from "vitest";
import type { ApiStatus } from "../../src/shared/types";

vi.mock("electron", () => ({ app: { getVersion: () => "1.0.0" } }));
vi.mock("electron-log/main", () => ({
  default: { error: vi.fn(), warn: vi.fn(), info: vi.fn(), debug: vi.fn() },
}));

const effacerSession = vi.fn();
vi.mock("../../src/main/models/token-store", () => ({
  lireJeton: () => "jeton-de-test",
  effacerSession: (): void => effacerSession(),
}));

const { ApiClient } = await import("../../src/main/models/api-client");

function reponse(statut: number, corps: unknown, brut = false): Response {
  return {
    ok: statut >= 200 && statut < 300,
    status: statut,
    text: async () => (brut ? String(corps) : JSON.stringify(corps)),
  } as Response;
}

describe("api-client", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    effacerSession.mockClear();
  });

  it("pose_les_trois_entetes_sur_une_route_authentifiee", async () => {
    const fetchMock = vi.fn().mockResolvedValue(reponse(200, { ouvrages: [] }));
    vi.stubGlobal("fetch", fetchMock);

    await new ApiClient().get("/ouvrages");

    const entetes = fetchMock.mock.calls[0][1].headers as Record<string, string>;
    expect(entetes["X-App-Id"]).toBe("electron");
    expect(entetes["X-App-Version"]).toBe("1.0.0");
    expect(entetes.Authorization).toBe("Bearer jeton-de-test");
  });

  it("n_envoie_aucun_entete_sur_la_route_publique", async () => {
    const fetchMock = vi.fn().mockResolvedValue(reponse(200, { versions_minimales: {} }));
    vi.stubGlobal("fetch", fetchMock);

    await new ApiClient().get("/version", "public");

    const entetes = fetchMock.mock.calls[0][1].headers as Record<string, string>;
    expect(entetes["X-App-Id"]).toBeUndefined();
    expect(entetes.Authorization).toBeUndefined();
  });

  it("renvoie_les_donnees_sur_un_succes", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(reponse(200, { id: 128 })));

    const resultat = await new ApiClient().get<{ id: number }>("/ouvrages/128");

    expect(resultat.ok).toBe(true);
    if (resultat.ok) expect(resultat.data.id).toBe(128);
  });

  it("traite_un_204_sans_tenter_d_analyser_le_corps", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(reponse(204, "", true)));

    const resultat = await new ApiClient().delete("/ouvrages/128", { version: 4 });

    expect(resultat.ok).toBe(true);
  });

  it("efface_la_session_sur_un_401_session_expiree", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        reponse(401, {
          erreur: { code: "session_expiree", champ: null, message: "Votre session a expiré" },
        }),
      ),
    );

    const resultat = await new ApiClient().get("/moi");

    expect(resultat.ok).toBe(false);
    if (!resultat.ok) expect(resultat.error.code).toBe("session_expiree");
    expect(effacerSession).toHaveBeenCalledOnce();
  });

  it("remonte_le_code_et_le_champ_d_un_conflit_de_version", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        reponse(409, {
          erreur: {
            code: "conflit_version",
            champ: "version",
            message: "Cette fiche a été modifiée par Vanina pendant votre saisie",
          },
        }),
      ),
    );

    const resultat = await new ApiClient().patch("/ouvrages/128", {});

    expect(resultat.ok).toBe(false);
    if (!resultat.ok) {
      expect(resultat.error.code).toBe("conflit_version");
      expect(resultat.error.champ).toBe("version");
      expect(resultat.error.message).toContain("Vanina");
    }
  });

  it("classe_un_426_en_danger_et_conserve_son_code", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        reponse(426, {
          erreur: {
            code: "version_trop_ancienne",
            champ: null,
            message: "Version 1.0.0 minimum requise",
          },
        }),
      ),
    );

    const resultat = await new ApiClient().get("/ouvrages");

    expect(resultat.ok).toBe(false);
    if (!resultat.ok) expect(resultat.error.code).toBe("version_trop_ancienne");
  });

  it("classe_un_429_en_avertissement", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        reponse(429, {
          erreur: { code: "trop_de_tentatives", champ: null, message: "Patientez une minute" },
        }),
      ),
    );

    const resultat = await new ApiClient().post("/connexion", { mode: "version" });

    expect(resultat.ok).toBe(false);
    if (!resultat.ok) expect(resultat.error.type).toBe("warning");
  });

  it("signale_un_serveur_indisponible_sur_une_reponse_en_texte_brut", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(reponse(500, "Internal Server Error", true)));

    const statuts: ApiStatus[] = [];
    const client = new ApiClient();
    client.setStatusListener((statut) => statuts.push(statut));

    const resultat = await client.get("/ouvrages");

    expect(resultat.ok).toBe(false);
    expect(statuts.at(-1)?.etat).toBe("serveur");
  });

  it("signale_hors_ligne_quand_le_serveur_est_injoignable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("fetch failed")));

    const statuts: ApiStatus[] = [];
    const client = new ApiClient();
    client.setStatusListener((statut) => statuts.push(statut));

    const resultat = await client.get("/ouvrages");

    expect(resultat.ok).toBe(false);
    if (!resultat.ok) expect(resultat.error.code).toBe("reseau_indisponible");
    expect(statuts.at(-1)?.etat).toBe("hors-ligne");
  });

  it("horodate_le_dernier_echange_reussi", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(reponse(200, {})));

    const statuts: ApiStatus[] = [];
    const client = new ApiClient();
    client.setStatusListener((statut) => statuts.push(statut));

    await client.get("/moi");

    expect(statuts.at(-1)?.etat).toBe("connecte");
    expect(statuts.at(-1)?.dernierEchange).not.toBeNull();
  });
});
