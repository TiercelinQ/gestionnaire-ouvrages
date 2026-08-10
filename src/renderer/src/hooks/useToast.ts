import { createContext, useContext } from "react";
import type { IpcError, ToastType } from "../../../shared/types";

export interface Toast {
  id: number;
  type: ToastType;
  message: string;
  description?: string;
}

export interface ToastApi {
  /** Shows a toast. Business errors go through `toastErreur`. */
  toast(type: ToastType, message: string, description?: string): void;
  /** Shows the error as the API worded it: the message targets the end user. */
  toastErreur(erreur: IpcError): void;
  fermer(id: number): void;
}

export const ToastContext = createContext<ToastApi | null>(null);

/** Access to the toast queue. Must be called under `ToastProvider`. */
export function useToast(): ToastApi {
  const api = useContext(ToastContext);
  if (!api) throw new Error("useToast doit être utilisé à l'intérieur de ToastProvider.");
  return api;
}
