import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("electron-log/main", () => ({
  default: { error: vi.fn(), warn: vi.fn(), info: vi.fn(), debug: vi.fn() },
}));

const coversRoot = vi.fn<() => string | null>();
vi.mock("../../src/main/models/preferences.model", () => ({
  coversRoot: (): string | null => coversRoot(),
}));

const existsSync = vi.fn();
const readFileSync = vi.fn();
const statSync = vi.fn();
vi.mock("node:fs", () => {
  // L'export `default` est requis : certaines dépendances importent le module entier.
  const fs = {
    existsSync: (chemin: string): boolean => existsSync(chemin),
    readFileSync: (chemin: string): Buffer => readFileSync(chemin),
    statSync: (chemin: string): { isFile(): boolean } => statSync(chemin),
  };
  return { ...fs, default: fs };
});

const { couvertureModel } = await import("../../src/main/models/couverture.model");

describe("couverture.model - les quatre cas de chemin du parc existant", () => {
  beforeEach(() => {
    existsSync.mockReset();
    readFileSync.mockReset();
    statSync.mockReset();
    coversRoot.mockReset();
  });

  it("renvoie_vide_quand_aucun_chemin_n_est_enregistre", () => {
    const resultat = couvertureModel.read(null);
    expect(resultat.ok && resultat.data.raison).toBe("vide");
  });

  it("signale_la_racine_absente_pour_un_chemin_relatif_sans_dossier_configure", () => {
    coversRoot.mockReturnValue(null);
    const resultat = couvertureModel.read("Couvertures\\dune.jpg");
    expect(resultat.ok && resultat.data.raison).toBe("racine-absente");
  });

  it("resout_un_chemin_relatif_sous_la_racine_configuree", () => {
    coversRoot.mockReturnValue("C:\\OneDrive\\Biblio");
    existsSync.mockReturnValue(true);
    statSync.mockReturnValue({ isFile: () => true });
    readFileSync.mockReturnValue(Buffer.from("image"));

    const resultat = couvertureModel.read("Couvertures\\dune.jpg");

    expect(resultat.ok && resultat.data.raison).toBe("ok");
    expect(resultat.ok && resultat.data.dataUrl?.startsWith("data:image/jpeg;base64,")).toBe(true);
  });

  it("refuse_un_chemin_relatif_qui_remonte_hors_de_la_racine", () => {
    coversRoot.mockReturnValue("C:\\OneDrive\\Biblio");
    const resultat = couvertureModel.read("..\\..\\Windows\\secret.png");
    expect(resultat.ok && resultat.data.raison).toBe("invalide");
  });

  it("lit_un_chemin_absolu_tel_quel", () => {
    existsSync.mockReturnValue(true);
    statSync.mockReturnValue({ isFile: () => true });
    readFileSync.mockReturnValue(Buffer.from("image"));

    const resultat = couvertureModel.read("C:\\Users\\q\\OneDrive\\couv.png");

    expect(resultat.ok && resultat.data.raison).toBe("ok");
    expect(coversRoot).not.toHaveBeenCalled();
  });

  it("signale_introuvable_quand_le_fichier_a_disparu", () => {
    existsSync.mockReturnValue(false);
    const resultat = couvertureModel.read("C:\\absent\\couv.png");
    expect(resultat.ok && resultat.data.raison).toBe("introuvable");
  });

  it("signale_invalide_sur_une_extension_non_image", () => {
    const resultat = couvertureModel.read("C:\\dossier\\fichier.txt");
    expect(resultat.ok && resultat.data.raison).toBe("invalide");
  });
});
