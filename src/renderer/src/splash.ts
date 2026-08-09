// Applique le thème résolu par le processus principal, transmis en paramètre d'URL.
// Aucune autre logique : le splash s'affiche puis se ferme.
const theme = new URLSearchParams(window.location.search).get("theme");
document.documentElement.dataset.theme = theme === "dark" ? "dark" : "light";
