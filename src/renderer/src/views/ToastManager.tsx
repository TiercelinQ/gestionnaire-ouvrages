import { useCallback, useMemo, useRef, useState, type ReactNode } from "react";
import { CircleCheck, CircleX, Info, TriangleAlert, X } from "lucide-react";
import type { IpcError, ToastType } from "../../../shared/types";
import { t } from "../i18n";
import { ToastContext, type Toast, type ToastApi } from "../hooks/useToast";

/** Display durations. A `danger` stays until it is explicitly dismissed. */
const DUREES: Record<ToastType, number | null> = {
  success: 4000,
  info: 4000,
  warning: 6000,
  danger: null,
};

const ICONES = {
  success: CircleCheck,
  info: Info,
  warning: TriangleAlert,
  danger: CircleX,
} as const;

/**
 * Toast queue. The only error feedback channel of the application:
 * no inline banner, no native dialog.
 */
export function ToastProvider({ children }: { children: ReactNode }): React.JSX.Element {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const compteur = useRef(0);

  const fermer = useCallback((id: number) => {
    setToasts((liste) => liste.filter((toast) => toast.id !== id));
  }, []);

  const toast = useCallback(
    (type: ToastType, message: string, description?: string) => {
      const id = ++compteur.current;
      setToasts((liste) => [...liste, { id, type, message, description }]);
      const duree = DUREES[type];
      if (duree !== null) window.setTimeout(() => fermer(id), duree);
    },
    [fermer],
  );

  const toastErreur = useCallback(
    (erreur: IpcError) => toast(erreur.type, erreur.message, erreur.description),
    [toast],
  );

  const api = useMemo<ToastApi>(
    () => ({ toast, toastErreur, fermer }),
    [toast, toastErreur, fermer],
  );

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div id="toast-container">
        {toasts.map((element) => {
          const Icone = ICONES[element.type];
          return (
            <div key={element.id} className={`toast toast-${element.type}`} role="status">
              <Icone
                className={`icon icon-md icon-${element.type}`}
                strokeWidth={1.75}
                aria-hidden="true"
              />
              <div className="toast-contenu">
                <p className="toast-message">{element.message}</p>
                {element.description ? (
                  <p className="toast-description">{element.description}</p>
                ) : null}
              </div>
              {DUREES[element.type] === null || element.type === "warning" ? (
                <button
                  type="button"
                  className="btn-ghost btn-icon"
                  onClick={() => fermer(element.id)}
                  title={t("action.fermer")}
                >
                  <X className="icon icon-sm" strokeWidth={1.75} aria-hidden="true" />
                </button>
              ) : null}
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}
