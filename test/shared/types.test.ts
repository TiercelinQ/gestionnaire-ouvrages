import { describe, it, expect } from "vitest";
import {
  estChaineNonVide,
  estEntierPositif,
  estNomenclatureInput,
  estOuvrageInput,
  estRessourceNomenclature,
} from "../../src/shared/types";

describe("gardes de type", () => {
  it("rejette_une_chaine_vide_ou_faite_d_espaces", () => {
    expect(estChaineNonVide("Dune")).toBe(true);
    expect(estChaineNonVide("   ")).toBe(false);
    expect(estChaineNonVide("")).toBe(false);
    expect(estChaineNonVide(42)).toBe(false);
  });

  it("rejette_un_identifiant_non_entier_ou_negatif", () => {
    expect(estEntierPositif(128)).toBe(true);
    expect(estEntierPositif(0)).toBe(false);
    expect(estEntierPositif(-1)).toBe(false);
    expect(estEntierPositif(1.5)).toBe(false);
    expect(estEntierPositif("128")).toBe(false);
  });

  it("accepte_les_sept_ressources_et_refuse_les_autres", () => {
    expect(estRessourceNomenclature("categories")).toBe(true);
    expect(estRessourceNomenclature("sous-genres")).toBe(true);
    // La table s'appelle sous_genres, mais le segment d'URL emploie le trait d'union.
    expect(estRessourceNomenclature("sous_genres")).toBe(false);
    expect(estRessourceNomenclature("utilisateurs")).toBe(false);
  });

  it("exige_titre_et_auteur_sur_un_ouvrage", () => {
    expect(estOuvrageInput({ titre: "Dune", auteur: "Frank Herbert" })).toBe(true);
    expect(estOuvrageInput({ titre: "Dune", auteur: "  " })).toBe(false);
    expect(estOuvrageInput({ titre: "Dune" })).toBe(false);
    expect(estOuvrageInput(null)).toBe(false);
  });

  it("exige_un_nom_sur_une_nomenclature", () => {
    expect(estNomenclatureInput({ nom: "Roman" })).toBe(true);
    expect(estNomenclatureInput({ nom: "" })).toBe(false);
    expect(estNomenclatureInput({})).toBe(false);
  });
});
