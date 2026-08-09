import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./styles/tokens.css";
import "./styles/styles.css";

const racine = document.getElementById("root");
if (!racine) throw new Error("Élément racine introuvable dans index.html.");

createRoot(racine).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
