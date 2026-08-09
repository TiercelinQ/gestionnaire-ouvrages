import { contextBridge, ipcRenderer } from "electron";
import { IPC } from "../shared/ipc-channels";
import type {
  ApiStatus,
  Identifiants,
  NomenclatureInput,
  OuvrageInput,
  OuvrageListe,
  OuvrageUpdateInput,
  RessourceNomenclature,
  WindowApi,
} from "../shared/types";

/**
 * Surface exposée au processus de rendu.
 *
 * Uniquement des fonctions nommées, une par canal déclaré. Ni `ipcRenderer` brut,
 * ni `require`, ni primitive Node. Aucune logique : le preload ne fait que transmettre.
 */
const api: WindowApi = {
  sessionStatus: () => ipcRenderer.invoke(IPC.SESSION_STATUS),
  sessionLogin: (identifiants: Identifiants) => ipcRenderer.invoke(IPC.SESSION_LOGIN, identifiants),
  sessionLogout: () => ipcRenderer.invoke(IPC.SESSION_LOGOUT),
  appInfo: () => ipcRenderer.invoke(IPC.APP_INFO),

  ouvrageList: () => ipcRenderer.invoke(IPC.OUVRAGE_LIST),
  ouvrageGet: (id: number) => ipcRenderer.invoke(IPC.OUVRAGE_GET, id),
  ouvrageCreate: (input: OuvrageInput) => ipcRenderer.invoke(IPC.OUVRAGE_CREATE, input),
  ouvrageUpdate: (id: number, input: OuvrageUpdateInput) =>
    ipcRenderer.invoke(IPC.OUVRAGE_UPDATE, id, input),
  ouvrageDelete: (id: number, version: number) => ipcRenderer.invoke(IPC.OUVRAGE_DELETE, id, version),
  ouvrageRestore: (id: number) => ipcRenderer.invoke(IPC.OUVRAGE_RESTORE, id),
  ouvrageHistory: (id: number) => ipcRenderer.invoke(IPC.OUVRAGE_HISTORY, id),
  corbeilleList: () => ipcRenderer.invoke(IPC.CORBEILLE_LIST),

  nomenclatureList: () => ipcRenderer.invoke(IPC.NOMENCLATURE_LIST),
  nomenclatureCreate: (ressource: RessourceNomenclature, input: NomenclatureInput) =>
    ipcRenderer.invoke(IPC.NOMENCLATURE_CREATE, ressource, input),
  nomenclatureUpdate: (ressource: RessourceNomenclature, id: number, input: NomenclatureInput) =>
    ipcRenderer.invoke(IPC.NOMENCLATURE_UPDATE, ressource, id, input),
  nomenclatureDelete: (ressource: RessourceNomenclature, id: number) =>
    ipcRenderer.invoke(IPC.NOMENCLATURE_DELETE, ressource, id),

  couverturePick: () => ipcRenderer.invoke(IPC.COUVERTURE_PICK),
  couvertureRead: (chemin: string | null) => ipcRenderer.invoke(IPC.COUVERTURE_READ, chemin),

  exportCsv: (lignes: OuvrageListe[]) => ipcRenderer.invoke(IPC.EXPORT_CSV, lignes),

  getPreferences: () => ipcRenderer.invoke(IPC.PREF_GET),
  setPreference: (cle, valeur) => ipcRenderer.invoke(IPC.PREF_SET, cle, valeur),
  pickCoversFolder: () => ipcRenderer.invoke(IPC.PREF_PICK_FOLDER),

  // L'objet événement n'est jamais transmis au rendu : seule la donnée passe.
  onApiStatus: (callback: (statut: ApiStatus) => void) => {
    const ecouteur = (_evenement: Electron.IpcRendererEvent, statut: ApiStatus): void =>
      callback(statut);
    ipcRenderer.on(IPC.API_STATUS, ecouteur);
    return () => {
      ipcRenderer.removeListener(IPC.API_STATUS, ecouteur);
    };
  },
};

contextBridge.exposeInMainWorld("api", api);
