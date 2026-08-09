import { describe, it, expect } from "vitest";
import { normaliser } from "../../src/renderer/src/utils/normalize";

describe("normaliser — doit reproduire la normalisation du serveur", () => {
  it("retire_les_diacritiques", () => {
    expect(normaliser("Périodes")).toBe("periodes");
    expect(normaliser("Éditions Gallimard")).toBe("editions gallimard");
  });

  it("passe_en_minuscules", () => {
    expect(normaliser("DUNE")).toBe("dune");
  });

  it("supprime_les_espaces_de_bordure", () => {
    expect(normaliser("  Frank Herbert  ")).toBe("frank herbert");
  });

  it("laisse_intacte_une_chaine_deja_normalisee", () => {
    expect(normaliser("frank herbert dune")).toBe("frank herbert dune");
  });

  it("permet_de_retrouver_un_titre_accentue_saisi_sans_accent", () => {
    const indexe = normaliser("Le Château des Étoiles");
    expect(indexe.includes(normaliser("chateau"))).toBe(true);
    expect(indexe.includes(normaliser("Étoiles"))).toBe(true);
  });
});
