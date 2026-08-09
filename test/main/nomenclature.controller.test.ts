import { describe, it, expect, vi, beforeEach } from "vitest";
import { IPC } from "../../src/shared/ipc-channels";
import type { IpcResult } from "../../src/shared/types";

type Gestionnaire = (evenement: unknown, ...args: unknown[]) => unknown;
const handlers = new Map<string, Gestionnaire>();

vi.mock("electron", () => ({
  ipcMain: {
    handle: (canal: string, gestionnaire: Gestionnaire): void => {
      handlers.set(canal, gestionnaire);
    },
  },
}));

const modele = { list: vi.fn(), create: vi.fn(), update: vi.fn(), remove: vi.fn() };
vi.mock("../../src/main/models/nomenclature.model", () => ({ nomenclatureModel: modele }));

const { registerNomenclatureController } = await import(
  "../../src/main/controllers/nomenclature.controller"
);
registerNomenclatureController();

async function appeler(canal: string, ...args: unknown[]): Promise<IpcResult<unknown>> {
  const gestionnaire = handlers.get(canal);
  if (!gestionnaire) throw new Error(`Canal non enregistré : ${canal}`);
  return (await gestionnaire({}, ...args)) as IpcResult<unknown>;
}

describe("nomenclature.controller", () => {
  beforeEach(() => {
    Object.values(modele).forEach((methode) => methode.mockReset());
  });

  it("rejette_une_ressource_inconnue", async () => {
    const resultat = await appeler(IPC.NOMENCLATURE_CREATE, "utilisateurs", { nom: "X" });

    expect(resultat.ok).toBe(false);
    expect(modele.create).not.toHaveBeenCalled();
  });

  it("rejette_le_nom_de_table_a_la_place_du_segment_d_url", async () => {
    const resultat = await appeler(IPC.NOMENCLATURE_CREATE, "sous_genres", { nom: "Space opera" });

    expect(resultat.ok).toBe(false);
    expect(modele.create).not.toHaveBeenCalled();
  });

  it("exige_la_categorie_a_la_creation_d_un_genre", async () => {
    const resultat = await appeler(IPC.NOMENCLATURE_CREATE, "genres", { nom: "Science-fiction" });

    expect(resultat.ok).toBe(false);
    if (!resultat.ok) expect(resultat.error.champ).toBe("id_categorie");
    expect(modele.create).not.toHaveBeenCalled();
  });

  it("accepte_un_genre_rattache_a_une_categorie", async () => {
    modele.create.mockResolvedValue({ ok: true, data: { id: 12, nom: "Science-fiction" } });

    const resultat = await appeler(IPC.NOMENCLATURE_CREATE, "genres", {
      nom: "Science-fiction",
      id_categorie: 1,
    });

    expect(resultat.ok).toBe(true);
    expect(modele.create).toHaveBeenCalledOnce();
  });

  it("n_exige_pas_de_rattachement_sur_une_liste_simple", async () => {
    modele.create.mockResolvedValue({ ok: true, data: { id: 5, nom: "Salon" } });

    const resultat = await appeler(IPC.NOMENCLATURE_CREATE, "localisations", { nom: "Salon" });

    expect(resultat.ok).toBe(true);
  });

  it("rejette_un_nom_vide_au_renommage", async () => {
    const resultat = await appeler(IPC.NOMENCLATURE_UPDATE, "categories", 1, { nom: "  " });

    expect(resultat.ok).toBe(false);
    if (!resultat.ok) expect(resultat.error.champ).toBe("nom");
    expect(modele.update).not.toHaveBeenCalled();
  });
});
