import { createContext, useContext } from "react";
import type { IpcError, ToastType } from "../../../shared/types";

export interface Toast {
  id: number;
  type: ToastType;
  message: string;
  description?: string;
}

export interface ToastApi {
  /** Affiche un toast. Les erreurs métier passent par `toastErreur`. */
  toast(type: ToastType, message: string, description?: string): void;
  /** Affiche l'erreur telle que l'API l'a rédigée : le message est destiné à l'utilisateur final. */
  toastErreur(erreur: IpcError): void;
  fermer(id: number): void;
}

export const ToastContext = createContext<ToastApi | null>(null);

/** Accès à la file de toasts. Doit être appelé sous `ToastProvider`. */
export function useToast(): ToastApi {
  const api = useContext(ToastContext);
  if (!api) throw new Error("useToast doit être utilisé à l'intérieur de ToastProvider.");
  return api;
}
