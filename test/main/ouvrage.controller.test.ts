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

const modele = {
  list: vi.fn(),
  get: vi.fn(),
  create: vi.fn(),
  update: vi.fn(),
  remove: vi.fn(),
  restore: vi.fn(),
  trash: vi.fn(),
  history: vi.fn(),
};
vi.mock("../../src/main/models/ouvrage.model", () => ({ ouvrageModel: modele }));

const { registerOuvrageController } = await import("../../src/main/controllers/ouvrage.controller");
registerOuvrageController();

async function appeler(canal: string, ...args: unknown[]): Promise<IpcResult<unknown>> {
  const gestionnaire = handlers.get(canal);
  if (!gestionnaire) throw new Error(`Canal non enregistré : ${canal}`);
  return (await gestionnaire({}, ...args)) as IpcResult<unknown>;
}

const OUVRAGE = { titre: "Dune", auteur: "Frank Herbert" };

describe("ouvrage.controller", () => {
  beforeEach(() => {
    Object.values(modele).forEach((methode) => methode.mockReset());
  });

  it("enregistre_les_huit_canaux_du_contrat", () => {
    expect(handlers.has(IPC.OUVRAGE_LIST)).toBe(true);
    expect(handlers.has(IPC.OUVRAGE_GET)).toBe(true);
    expect(handlers.has(IPC.OUVRAGE_CREATE)).toBe(true);
    expect(handlers.has(IPC.OUVRAGE_UPDATE)).toBe(true);
    expect(handlers.has(IPC.OUVRAGE_DELETE)).toBe(true);
    expect(handlers.has(IPC.OUVRAGE_RESTORE)).toBe(true);
    expect(handlers.has(IPC.OUVRAGE_HISTORY)).toBe(true);
    expect(handlers.has(IPC.CORBEILLE_LIST)).toBe(true);
  });

  it("rejette_une_creation_sans_titre_sans_appeler_le_modele", async () => {
    const resultat = await appeler(IPC.OUVRAGE_CREATE, { auteur: "Frank Herbert" });

    expect(resultat.ok).toBe(false);
    if (!resultat.ok) {
      expect(resultat.error.type).toBe("danger");
      expect(resultat.error.champ).toBe("titre");
    }
    expect(modele.create).not.toHaveBeenCalled();
  });

  it("rejette_un_identifiant_non_entier", async () => {
    const resultat = await appeler(IPC.OUVRAGE_GET, "abc");

    expect(resultat.ok).toBe(false);
    expect(modele.get).not.toHaveBeenCalled();
  });

  it("rejette_une_version_transmise_en_chaine", async () => {
    const resultat = await appeler(IPC.OUVRAGE_UPDATE, 128, { ...OUVRAGE, version: "3" });

    expect(resultat.ok).toBe(false);
    if (!resultat.ok) expect(resultat.error.champ).toBe("version");
    expect(modele.update).not.toHaveBeenCalled();
  });

  it("exige_une_version_sur_la_suppression", async () => {
    const resultat = await appeler(IPC.OUVRAGE_DELETE, 128, undefined);

    expect(resultat.ok).toBe(false);
    expect(modele.remove).not.toHaveBeenCalled();
  });

  it("transmet_une_charge_valide_au_modele", async () => {
    modele.update.mockResolvedValue({ ok: true, data: { id: 128 } });

    const resultat = await appeler(IPC.OUVRAGE_UPDATE, 128, { ...OUVRAGE, version: 3 });

    expect(resultat.ok).toBe(true);
    expect(modele.update).toHaveBeenCalledWith(128, { ...OUVRAGE, version: 3 });
  });
});
