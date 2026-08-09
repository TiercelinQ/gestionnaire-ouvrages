/**
 * Noms des canaux IPC. Convention `entite:action`.
 * Aucune chaîne de canal ne doit apparaître ailleurs dans le code.
 */
export const IPC = {
  // Session et application
  SESSION_STATUS: "session:status",
  SESSION_LOGIN: "session:login",
  SESSION_LOGOUT: "session:logout",
  APP_INFO: "app:info",

  // Ouvrages
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

  // Couvertures
  COUVERTURE_PICK: "couverture:pick",
  COUVERTURE_READ: "couverture:read",

  // Export
  EXPORT_CSV: "export:csv",

  // Préférences
  PREF_GET: "pref:get",
  PREF_SET: "pref:set",
  PREF_PICK_FOLDER: "pref:pickFolder",

  // Événement poussé du processus principal vers le rendu
  API_STATUS: "api:status",
} as const;
