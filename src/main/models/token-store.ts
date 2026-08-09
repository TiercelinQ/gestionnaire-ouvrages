import { app, safeStorage } from "electron";
import { readFileSync, writeFileSync, existsSync, rmSync } from "node:fs";
import { join } from "node:path";
import log from "electron-log/main";
import * as config from "../../shared/config";
import type { Utilisateur } from "../../shared/types";
import { ChiffrementIndisponibleError } from "./errors";

/** Session persistée localement. Le jeton vaut trente jours d'accès : il est chiffré au repos. */
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
 * Lit la session persistée. Renvoie `null` si aucune session n'est stockée,
 * si le fichier est illisible, ou si la date d'expiration mémorisée est dépassée.
 * Le contenu est mis en cache mémoire pour éviter un déchiffrement par requête.
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
    // Fichier corrompu ou chiffré par un autre profil Windows : on repart d'une session vide.
    log.error("Lecture de la session impossible", err);
    cache = null;
    effacerSession();
  }
  return cache;
}

/**
 * Chiffre puis écrit la session.
 * @throws {ChiffrementIndisponibleError} si le système ne fournit pas de chiffrement —
 * le jeton n'est jamais écrit en clair.
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

/** Efface la session locale, sur déconnexion ou sur réponse `401 session_expiree`. */
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

/** Jeton courant, ou `null`. Jamais journalisé ni transmis au processus de rendu. */
export function lireJeton(): string | null {
  return lireSession()?.jeton ?? null;
}
