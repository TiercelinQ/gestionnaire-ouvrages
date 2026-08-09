import { describe, it, expect } from "vitest";
import { calculerFenetre } from "../../src/renderer/src/hooks/useVirtualRows";

const HAUTEUR = 36;
const MARGE = 8;

describe("calculerFenetre", () => {
  it("renvoie_une_fenetre_vide_sans_donnees", () => {
    expect(calculerFenetre(0, HAUTEUR, 0, 600, MARGE)).toEqual({
      debut: 0,
      fin: 0,
      hauteurAvant: 0,
      hauteurApres: 0,
    });
  });

  it("part_du_debut_de_la_liste_au_repos", () => {
    const fenetre = calculerFenetre(414, HAUTEUR, 0, 600, MARGE);

    expect(fenetre.debut).toBe(0);
    expect(fenetre.hauteurAvant).toBe(0);
    expect(fenetre.fin).toBeGreaterThan(16);
  });

  it("ne_rend_qu_une_fraction_des_lignes", () => {
    const fenetre = calculerFenetre(414, HAUTEUR, 0, 600, MARGE);

    expect(fenetre.fin - fenetre.debut).toBeLessThan(414);
  });

  it("decale_la_fenetre_au_defilement_et_compense_par_l_espaceur", () => {
    const fenetre = calculerFenetre(414, HAUTEUR, 100 * HAUTEUR, 600, MARGE);

    expect(fenetre.debut).toBe(100 - MARGE);
    expect(fenetre.hauteurAvant).toBe((100 - MARGE) * HAUTEUR);
  });

  it("conserve_la_hauteur_totale_quelle_que_soit_la_position", () => {
    const fenetre = calculerFenetre(414, HAUTEUR, 100 * HAUTEUR, 600, MARGE);
    const rendues = (fenetre.fin - fenetre.debut) * HAUTEUR;

    expect(fenetre.hauteurAvant + rendues + fenetre.hauteurApres).toBe(414 * HAUTEUR);
  });

  it("ne_depasse_pas_la_derniere_ligne_en_fin_de_liste", () => {
    const fenetre = calculerFenetre(414, HAUTEUR, 414 * HAUTEUR, 600, MARGE);

    expect(fenetre.fin).toBe(414);
    expect(fenetre.hauteurApres).toBe(0);
  });

  it("ignore_une_position_de_defilement_negative", () => {
    const fenetre = calculerFenetre(414, HAUTEUR, -50, 600, MARGE);

    expect(fenetre.debut).toBe(0);
  });
});
