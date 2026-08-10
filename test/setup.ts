import "@testing-library/jest-dom/vitest";
import { afterEach, vi } from "vitest";
import { cleanup } from "@testing-library/react";
import type { WindowApi } from "../src/shared/types";

// Without Vitest globals, the automatic Testing Library cleanup is not wired: renders
// would pile up in the same document from one test to the next.
afterEach(cleanup);

/** Mocked `window.api`: no test touches the network or the disk. */
const api: WindowApi = {
  sessionStatus: vi.fn().mockResolvedValue({ ok: true, data: { authentifie: true } }),
  sessionLogin: vi.fn(),
  sessionLogout: vi.fn(),
  appInfo: vi.fn().mockResolvedValue({ ok: true, data: { nom: "Test", version: "1.0.0" } }),

  ouvrageList: vi.fn().mockResolvedValue({ ok: true, data: [] }),
  ouvrageGet: vi.fn(),
  ouvrageCreate: vi.fn(),
  ouvrageUpdate: vi.fn(),
  ouvrageDelete: vi.fn(),
  ouvrageRestore: vi.fn(),
  ouvrageHistory: vi.fn().mockResolvedValue({ ok: true, data: [] }),
  corbeilleList: vi.fn().mockResolvedValue({ ok: true, data: [] }),

  nomenclatureList: vi.fn().mockResolvedValue({
    ok: true,
    data: {
      categories: [],
      genres: [],
      sous_genres: [],
      illustrations: [],
      localisations: [],
      periodes: [],
      reliures: [],
    },
  }),
  nomenclatureCreate: vi.fn(),
  nomenclatureUpdate: vi.fn(),
  nomenclatureDelete: vi.fn(),

  couverturePick: vi.fn(),
  couvertureRead: vi.fn().mockResolvedValue({ ok: true, data: { dataUrl: null, raison: "vide" } }),

  exportCsv: vi.fn(),

  getPreferences: vi
    .fn()
    .mockResolvedValue({ ok: true, data: { theme: null, coversRoot: null, windowBounds: null } }),
  setPreference: vi.fn(),
  pickCoversFolder: vi.fn(),

  onApiStatus: vi.fn().mockReturnValue(() => undefined),
};

globalThis.window.api = api;

// jsdom implements neither matchMedia nor ResizeObserver, both used by the interface.
globalThis.window.matchMedia = vi.fn().mockReturnValue({
  matches: false,
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
});

globalThis.ResizeObserver = class {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
} as unknown as typeof ResizeObserver;
