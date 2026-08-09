// scripts/stop-lint.cjs - garde du hook Stop : lance le lint seulement si un fichier
// TypeScript porte des modifications non commitées. Sans git, on lint par défaut.
const { execSync } = require("node:child_process");

let changed = true;
try {
  changed = /\.tsx?(\s|$)/m.test(execSync("git status --porcelain", { encoding: "utf8" }));
} catch {
  /* pas de dépôt git → on lint */
}
if (changed) execSync("npm run lint", { stdio: "inherit" });
