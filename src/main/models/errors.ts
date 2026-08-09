/** Erreurs métier nommées. Levées par les modèles, interceptées par les contrôleurs. */

/** Le serveur a répondu avec un code d'erreur applicatif. */
export class ApiHttpError extends Error {
  constructor(
    message: string,
    readonly statut: number,
    readonly code: string,
    readonly champ: string | null = null,
  ) {
    super(message);
    this.name = "ApiHttpError";
  }
}

/** Le serveur n'a pas pu être joint (réseau, DNS, délai dépassé). */
export class ApiReseauError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ApiReseauError";
  }
}

/** Le serveur a répondu, mais la réponse n'est pas exploitable (500 en texte brut, JSON invalide). */
export class ApiReponseIllisibleError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ApiReponseIllisibleError";
  }
}

/** Aucune session locale exploitable. */
export class SessionAbsenteError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "SessionAbsenteError";
  }
}

/** Le chiffrement du système n'est pas disponible : le jeton ne peut pas être conservé. */
export class ChiffrementIndisponibleError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ChiffrementIndisponibleError";
  }
}
