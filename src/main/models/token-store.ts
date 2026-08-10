import { app, safeStorage } from "electron";
import { readFileSync, writeFileSync, existsSync, rmSync } from "node:fs";
import { join } from "node:path";
import log from "electron-log/main";
import * as config from "../../shared/config";
import type { Utilisateur } from "../../shared/types";
import { ChiffrementIndisponibleError } from "./errors";

/** Session persisted locally. The token is worth thirty days of access: it is encrypted at rest. */
export interface SessionPersistee {
  jeton: string;
  expire_le: string;
  utilisateur: Utilisateur;
}

let cache: SessionPersistee | null = null;
let cacheCharge = false;

function fichier(): string {
  return join(app.getPath("userData"), config.SESSION_FILENAME);
}

function expiree(session: SessionPersistee): boolean {
  const echeance = Date.parse(session.expire_le);
  return Number.isNaN(echeance) || echeance <= Date.now();
}

/**
 * Reads the persisted session. Returns `null` if no session is stored, if the file is
 * unreadable, or if the remembered expiry date has passed.
 * The content is cached in memory to avoid one decryption per request.
 */
export function lireSession(): SessionPersistee | null {
  if (cacheCharge) return cache;
  cacheCharge = true;

  const chemin = fichier();
  if (!existsSync(chemin)) {
    cache = null;
    return null;
  }

  try {
    const chiffre = readFileSync(chemin);
    const session = JSON.parse(safeStorage.decryptString(chiffre)) as SessionPersistee;
    cache = expiree(session) ? null : session;
    if (!cache) {
      log.info("Session locale expirée, effacement");
      effacerSession();
    }
  } catch (err) {
    // File corrupted or encrypted by another Windows profile: restart from an empty session.
    log.error("Lecture de la session impossible", err);
    cache = null;
    effacerSession();
  }
  return cache;
}

/**
 * Encrypts then writes the session.
 * @throws {ChiffrementIndisponibleError} if the system provides no encryption -
 * the token is never written in clear text.
 */
export function ecrireSession(session: SessionPersistee): void {
  if (!safeStorage.isEncryptionAvailable()) {
    throw new ChiffrementIndisponibleError(
      "Le chiffrement du système n'est pas disponible : la session ne peut pas être conservée.",
    );
  }
  writeFileSync(fichier(), safeStorage.encryptString(JSON.stringify(session)));
  cache = session;
  cacheCharge = true;
}

/** Clears the local session, on sign-out or on a `401 session_expiree` response. */
export function effacerSession(): void {
  const chemin = fichier();
  try {
    if (existsSync(chemin)) rmSync(chemin);
  } catch (err) {
    log.error("Effacement de la session impossible", err);
  }
  cache = null;
  cacheCharge = true;
}

/** Current token, or `null`. Never logged nor passed to the renderer process. */
export function lireJeton(): string | null {
  return lireSession()?.jeton ?? null;
}
