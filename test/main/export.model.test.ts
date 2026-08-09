import { describe, it, expect, vi, beforeEach } from "vitest";
import type { OuvrageListe } from "../../src/shared/types";

const writeFileSync = vi.fn();
vi.mock("node:fs", () => {
  // L'export `default` est requis : certaines dépendances importent le module entier.
  const fs = {
    writeFileSync: (chemin: string, contenu: string, encodage: string): void =>
      writeFileSync(chemin, contenu, encodage),
  };
  return { ...fs, default: fs };
});

const { exportModel } = await import("../../src/main/models/export.model");

function ligne(partiel: Partial<OuvrageListe>): OuvrageListe {
  return {
    id: 1,
    titre: "Dune",
    auteur: "Frank Herbert",
    edition: "Robert Laffont",
    recherche_normalisee: "",
    categorie_nom: "Roman",
    ...partiel,
  };
}

describe("export.model", () => {
  beforeEach(() => writeFileSync.mockReset());

  it("ecrit_un_entete_et_une_ligne_par_ouvrage", () => {
    exportModel.toCsv([ligne({}), ligne({ titre: "Messie de Dune" })], "C:\\sortie.csv");

    const contenu = writeFileSync.mock.calls[0][1] as string;
    expect(contenu.split("\r\n")).toHaveLength(3);
    expect(contenu).toContain("Auteur;Titre;Édition;Catégorie");
  });

  it("commence_par_une_marque_d_ordre_pour_excel", () => {
    exportModel.toCsv([], "C:\\sortie.csv");
    const contenu = writeFileSync.mock.calls[0][1] as string;
    expect(contenu.charCodeAt(0)).toBe(0xfeff);
  });

  it("encadre_et_double_les_guillemets_d_une_valeur_a_risque", () => {
    exportModel.toCsv([ligne({ titre: 'Le "Cycle"; suite' })], "C:\\sortie.csv");
    const contenu = writeFileSync.mock.calls[0][1] as string;
    expect(contenu).toContain('"Le ""Cycle""; suite"');
  });

  it("remplace_une_valeur_nulle_par_une_cellule_vide", () => {
    exportModel.toCsv([ligne({ edition: null, categorie_nom: null })], "C:\\sortie.csv");
    const contenu = writeFileSync.mock.calls[0][1] as string;
    expect(contenu.split("\r\n")[1]).toBe("Frank Herbert;Dune;;");
  });
});
