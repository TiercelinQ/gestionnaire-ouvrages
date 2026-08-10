import { app, BrowserWindow, nativeTheme, session } from "electron";
import { join } from "node:path";
import log from "electron-log/main";
import * as config from "../shared/config";
import { IPC } from "../shared/ipc-channels";
import type { Theme } from "../shared/types";
import { registerAllControllers } from "./controllers";
import { setupLogging } from "./logger";
import { apiClient } from "./models/api-client";
import * as preferencesModel from "./models/preferences.model";

setupLogging();

process.on("uncaughtException", (err) => {
  log.error("Exception non interceptée", err);
});

process.on("unhandledRejection", (raison) => {
  log.error("Promesse rejetée sans traitement", raison);
});

/**
 * Window background colours, the only place a hexadecimal is repeated outside tokens.css:
 * a `BrowserWindow` option cannot read a CSS variable. Sources: light and dark `--bg`.
 */
const FOND = { light: "#FFFFFF", dark: "#17181C" } as const;

let mainWindow: BrowserWindow | null = null;

function themeDemarrage(): Theme {
  const persiste = preferencesModel.getAll().theme;
  if (persiste) return persiste;
  return nativeTheme.shouldUseDarkColors ? "dark" : "light";
}

function urlRenderer(page: "index" | "splash"): { url?: string; fichier?: string } {
  const serveur = process.env.ELECTRON_RENDERER_URL;
  if (!app.isPackaged && serveur) return { url: `${serveur}/${page}.html` };
  return { fichier: join(__dirname, `../renderer/${page}.html`) };
}

/**
 * Splash window: the application icon and nothing else. Transparent and shadowless so no
 * frame shows around it, which also makes it theme-independent.
 */
function creerSplash(): BrowserWindow {
  const splash = new BrowserWindow({
    width: config.SPLASH_WIDTH,
    height: config.SPLASH_HEIGHT,
    frame: false,
    transparent: true,
    hasShadow: false,
    resizable: false,
    center: true,
    show: true,
    icon: join(__dirname, "../../resources/icon.png"),
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  const cible = urlRenderer("splash");
  if (cible.url) void splash.loadURL(cible.url);
  else void splash.loadFile(cible.fichier as string);

  return splash;
}

function creerFenetre(theme: Theme): BrowserWindow {
  const bounds = preferencesModel.getAll().windowBounds;

  const fenetre = new BrowserWindow({
    width: bounds?.width ?? config.WINDOW_DEFAULT_WIDTH,
    height: bounds?.height ?? config.WINDOW_DEFAULT_HEIGHT,
    x: bounds?.x,
    y: bounds?.y,
    minWidth: config.WINDOW_MIN_WIDTH,
    minHeight: config.WINDOW_MIN_HEIGHT,
    center: bounds?.x === undefined,
    show: false,
    backgroundColor: FOND[theme],
    autoHideMenuBar: true,
    title: config.APP_DISPLAY_NAME,
    icon: join(__dirname, "../../resources/icon.png"),
    webPreferences: {
      preload: join(__dirname, "../preload/index.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webSecurity: true,
    },
  });

  const cible = urlRenderer("index");
  if (cible.url) void fenetre.loadURL(cible.url);
  else void fenetre.loadFile(cible.fichier as string);

  fenetre.on("close", () => {
    const { width, height, x, y } = fenetre.getNormalBounds();
    preferencesModel.set("windowBounds", { width, height, x, y });
  });

  if (!app.isPackaged) fenetre.webContents.openDevTools({ mode: "detach" });

  return fenetre;
}

function verrouillerNavigation(): void {
  app.on("web-contents-created", (_evenement, contenu) => {
    contenu.on("will-navigate", (evenement) => evenement.preventDefault());
    contenu.setWindowOpenHandler(() => ({ action: "deny" }));
  });
}

// Single instance: the application writes an encrypted token and preferences.
if (!app.requestSingleInstanceLock()) {
  app.quit();
} else {
  app.on("second-instance", () => {
    if (!mainWindow) return;
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.focus();
  });

  verrouillerNavigation();

  void app.whenReady().then(() => {
    session.defaultSession.setPermissionRequestHandler((_contenu, _permission, callback) =>
      callback(false),
    );

    const theme = themeDemarrage();
    const splash = creerSplash();
    const affichageSplash = Date.now();

    registerAllControllers();
    mainWindow = creerFenetre(theme);

    // The model knows nothing of BrowserWindow: the composition root relays the state to the renderer.
    apiClient.setStatusListener((statut) => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send(IPC.API_STATUS, statut);
      }
    });

    mainWindow.once("ready-to-show", () => {
      const attente = Math.max(0, config.SPLASH_MIN_DURATION_MS - (Date.now() - affichageSplash));
      setTimeout(() => {
        if (!splash.isDestroyed()) splash.close();
        mainWindow?.show();
      }, attente);
    });

    log.info(`Démarrage ${config.APP_DISPLAY_NAME} v${app.getVersion()}`);

    app.on("activate", () => {
      if (BrowserWindow.getAllWindows().length === 0) mainWindow = creerFenetre(themeDemarrage());
    });
  });

  app.on("window-all-closed", () => {
    if (process.platform !== "darwin") app.quit();
  });
}
