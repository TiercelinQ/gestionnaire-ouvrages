import log from "electron-log/main";
import * as config from "../shared/config";

/** Application logging. Single configuration point for the transports. */
export function setupLogging(): void {
  log.initialize();
  log.transports.file.level = debugActif() ? "debug" : config.LOG_LEVEL;
  log.transports.file.maxSize = config.LOG_MAX_BYTES;
  // Console echo in debug only: in production the application runs windowed.
  log.transports.console.level = debugActif() ? "debug" : false;
}

function debugActif(): boolean {
  const cle = `${config.APP_NAME.toUpperCase().replace(/[^A-Z0-9]/g, "_")}_DEBUG`;
  return process.env[cle] === "1";
}
