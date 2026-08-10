import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("electron", () => ({ app: { getPath: () => "C:\\userData" } }));
vi.mock("electron-log/main", () => ({
  default: { error: vi.fn(), warn: vi.fn(), info: vi.fn(), debug: vi.fn() },
}));

const fichiers = new Map<string, string>();
vi.mock("node:fs", () => {
  // The `default` export is required: some dependencies import the whole module.
  const fs = {
    existsSync: (chemin: string): boolean => fichiers.has(chemin),
    readFileSync: (chemin: string): string => {
      const contenu = fichiers.get(chemin);
      if (contenu === undefined) throw new Error("ENOENT");
      return contenu;
    },
    writeFileSync: (chemin: string, contenu: string): void => {
      fichiers.set(chemin, contenu);
    },
  };
  return { ...fs, default: fs };
});

const preferences = await import("../../src/main/models/preferences.model");

const CHEMIN = "C:\\userData\\preferences.json";

describe("preferences.model", () => {
  beforeEach(() => fichiers.clear());

  it("renvoie_les_valeurs_par_defaut_sans_fichier", () => {
    const valeurs = preferences.getAll();

    expect(valeurs.theme).toBeNull();
    expect(valeurs.coversRoot).toBeNull();
  });

  it("persiste_une_preference_ecrite", () => {
    preferences.set("coversRoot", "C:\\OneDrive\\Biblio");

    expect(preferences.coversRoot()).toBe("C:\\OneDrive\\Biblio");
    expect(JSON.parse(fichiers.get(CHEMIN) as string).coversRoot).toBe("C:\\OneDrive\\Biblio");
  });

  it("conserve_les_autres_cles_lors_d_une_ecriture", () => {
    preferences.set("theme", "dark");
    preferences.set("coversRoot", "C:\\Biblio");

    const ecrit = JSON.parse(fichiers.get(CHEMIN) as string);
    expect(ecrit.theme).toBe("dark");
    expect(ecrit.coversRoot).toBe("C:\\Biblio");
  });
});
