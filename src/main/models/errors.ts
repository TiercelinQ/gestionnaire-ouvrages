/** Named business errors. Raised by the models, caught by the controllers. */

/** The server answered with an application error code. */
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

/** The server could not be reached (network, DNS, timeout). */
export class ApiReseauError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ApiReseauError";
  }
}

/** The server answered, but the response is unusable (plain text 500, invalid JSON). */
export class ApiReponseIllisibleError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ApiReponseIllisibleError";
  }
}

/** No usable local session. */
export class SessionAbsenteError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "SessionAbsenteError";
  }
}

/** System encryption is unavailable: the token cannot be kept. */
export class ChiffrementIndisponibleError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ChiffrementIndisponibleError";
  }
}
