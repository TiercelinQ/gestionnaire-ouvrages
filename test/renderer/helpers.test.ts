import { describe, it, expect } from "vitest";
import {
  formaterDate,
  formaterDateHeure,
  formaterHeure,
  formaterNombre,
  versIdentifiant,
  videVersNull,
} from "../../src/renderer/src/utils/helpers";

describe("conversion vers l'heure de Paris", () => {
  it("ajoute_deux_heures_en_ete", () => {
    // 2026-08-08T14:22:07Z - heure d'été, UTC+2.
    expect(formaterHeure("2026-08-08T14:22:07Z")).toBe("16:22");
  });

  it("ajoute_une_heure_en_hiver", () => {
    // 2026-01-15T14:22:07Z - heure d'hiver, UTC+1.
    expect(formaterHeure("2026-01-15T14:22:07Z")).toBe("15:22");
  });

  it("bascule_de_jour_quand_l_heure_locale_depasse_minuit", () => {
    expect(formaterDate("2026-08-08T23:30:00Z")).toBe("09/08/2026");
  });

  it("compose_date_et_heure", () => {
    expect(formaterDateHeure("2026-08-07T09:14:32Z")).toBe("07/08/2026 11:14");
  });

  it("renvoie_une_chaine_vide_sur_une_date_absente_ou_illisible", () => {
    expect(formaterDate(null)).toBe("");
    expect(formaterDate("pas une date")).toBe("");
  });
});

describe("helpers de formulaire", () => {
  it("formate_les_milliers_a_la_francaise", () => {
    // L'espace employé est une espace insécable étroite, pas un espace ordinaire.
    expect(formaterNombre(1234).replace(/\s/gu, " ")).toBe("1 234");
  });

  it("convertit_une_saisie_vide_en_null", () => {
    expect(videVersNull("   ")).toBeNull();
    expect(videVersNull("Dune")).toBe("Dune");
  });

  it("convertit_une_valeur_de_liste_en_identifiant", () => {
    expect(versIdentifiant("12")).toBe(12);
    expect(versIdentifiant("")).toBeNull();
    expect(versIdentifiant("0")).toBeNull();
  });
});
