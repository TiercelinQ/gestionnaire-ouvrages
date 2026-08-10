/**
 * IPC channel names. Convention `entity:action`.
 * No channel string may appear anywhere else in the code.
 */
export const IPC = {
  // Session and application
  SESSION_STATUS: "session:status",
  SESSION_LOGIN: "session:login",
  SESSION_LOGOUT: "session:logout",
  APP_INFO: "app:info",

  // Books
  OUVRAGE_LIST: "ouvrage:list",
  OUVRAGE_GET: "ouvrage:get",
  OUVRAGE_CREATE: "ouvrage:create",
  OUVRAGE_UPDATE: "ouvrage:update",
  OUVRAGE_DELETE: "ouvrage:delete",
  OUVRAGE_RESTORE: "ouvrage:restore",
  OUVRAGE_HISTORY: "ouvrage:history",
  CORBEILLE_LIST: "corbeille:list",

  // Nomenclatures
  NOMENCLATURE_LIST: "nomenclature:list",
  NOMENCLATURE_CREATE: "nomenclature:create",
  NOMENCLATURE_UPDATE: "nomenclature:update",
  NOMENCLATURE_DELETE: "nomenclature:delete",

  // Covers
  COUVERTURE_PICK: "couverture:pick",
  COUVERTURE_READ: "couverture:read",

  // Export
  EXPORT_CSV: "export:csv",

  // Preferences
  PREF_GET: "pref:get",
  PREF_SET: "pref:set",
  PREF_PICK_FOLDER: "pref:pickFolder",

  // Event pushed from the main process to the renderer
  API_STATUS: "api:status",
} as const;
