import { describe, it, expect, vi, beforeEach } from "vitest";

const chiffrementDisponible = vi.fn().mockReturnValue(true);
vi.mock("electron", () => ({
  app: { getPath: () => "C:\\userData" },
  safeStorage: {
    isEncryptionAvailable: (): boolean => chiffrementDisponible(),
    encryptString: (texte: string): Buffer => Buffer.from(texte, "utf8"),
    decryptString: (tampon: Buffer): string => tampon.toString("utf8"),
  },
}));

vi.mock("electron-log/main", () => ({
  default: { error: vi.fn(), warn: vi.fn(), info: vi.fn(), debug: vi.fn() },
}));

const fichiers = new Map<string, Buffer>();
vi.mock("node:fs", () => {
  // The `default` export is required: some dependencies import the whole module.
  const fs = {
    existsSync: (chemin: string): boolean => fichiers.has(chemin),
    readFileSync: (chemin: string): Buffer => {
      const contenu = fichiers.get(chemin);
      if (!contenu) throw new Error("ENOENT");
      return contenu;
    },
    writeFileSync: (chemin: string, contenu: Buffer): void => {
      fichiers.set(chemin, contenu);
    },
    rmSync: (chemin: string): void => {
      fichiers.delete(chemin);
    },
  };
  return { ...fs, default: fs };
});

const store = await import("../../src/main/models/token-store");

const UTILISATEUR = { id: 3, email: "q@example.com", nom_affichage: "Quentin" };

function dansUnMois(): string {
  return new Date(Date.now() + 30 * 24 * 3600 * 1000).toISOString();
}

describe("token-store", () => {
  beforeEach(() => {
    fichiers.clear();
    chiffrementDisponible.mockReturnValue(true);
    store.effacerSession();
  });

  it("relit_une_session_ecrite", () => {
    store.ecrireSession({ jeton: "abc", expire_le: dansUnMois(), utilisateur: UTILISATEUR });

    expect(store.lireJeton()).toBe("abc");
  });

  it("refuse_d_ecrire_en_clair_si_le_chiffrement_est_indisponible", () => {
    chiffrementDisponible.mockReturnValue(false);

    expect(() =>
      store.ecrireSession({ jeton: "abc", expire_le: dansUnMois(), utilisateur: UTILISATEUR }),
    ).toThrowError(/chiffrement/i);
    expect(fichiers.size).toBe(0);
  });

  it("ignore_une_session_dont_l_echeance_est_passee", () => {
    store.ecrireSession({
      jeton: "abc",
      expire_le: new Date(Date.now() - 1000).toISOString(),
      utilisateur: UTILISATEUR,
    });
    // The memory cache is cleared to force a re-read from the file.
    store.effacerSession();
    fichiers.set(
      "C:\\userData\\session.bin",
      Buffer.from(
        JSON.stringify({
          jeton: "abc",
          expire_le: new Date(Date.now() - 1000).toISOString(),
          utilisateur: UTILISATEUR,
        }),
        "utf8",
      ),
    );

    expect(store.lireSession()).toBeNull();
  });

  it("efface_le_fichier_a_la_deconnexion", () => {
    store.ecrireSession({ jeton: "abc", expire_le: dansUnMois(), utilisateur: UTILISATEUR });

    store.effacerSession();

    expect(store.lireJeton()).toBeNull();
    expect(fichiers.size).toBe(0);
  });
});
