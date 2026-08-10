/**
 * Constants shared by the three processes.
 * No colour here: visual values live in tokens.css.
 */

// --- Application ---
export const APP_NAME = "GestionnaireOuvrage";
export const APP_DISPLAY_NAME = "Gestionnaire Ouvrage";
export const APP_VERSION = "1.1.0";

// --- API (production environment, see docs/specs/01-scoping.md) ---
export const API_BASE_URL = "https://gestionnaire-ouvrages-api.qtiercelin-apps.workers.dev";
export const API_PREFIX = "/v1";
export const API_APP_ID = "electron";
export const API_TIMEOUT_MS = 20_000;

// --- Files under app.getPath("userData") ---
export const PREFERENCES_FILENAME = "preferences.json";
export const SESSION_FILENAME = "session.bin";

// --- Window ---
export const WINDOW_MIN_WIDTH = 1024;
export const WINDOW_MIN_HEIGHT = 768;
export const WINDOW_DEFAULT_WIDTH = 1280;
export const WINDOW_DEFAULT_HEIGHT = 800;

// --- Splash: square window sized on the icon, its only content (mirrors --splash-icon-size) ---
export const SPLASH_WIDTH = 256;
export const SPLASH_HEIGHT = 256;
export const SPLASH_MIN_DURATION_MS = 1200;

// --- Toasts (docs/specs/03-surfaces.md) ---
export const TOAST_POSITION = "bottom-center";

// --- Virtualised table: fixed row height, the premise of the virtualisation ---
export const ROW_HEIGHT = 36;
export const ROW_OVERSCAN = 8;

// --- Logging ---
export const LOG_LEVEL = "info";
export const LOG_MAX_BYTES = 1_000_000;

// --- Image extensions accepted for covers ---
export const IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp"] as const;
