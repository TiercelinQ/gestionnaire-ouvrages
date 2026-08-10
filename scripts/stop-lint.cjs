// scripts/stop-lint.cjs - Stop hook guard: runs the lint only when a TypeScript file
// carries uncommitted changes. Without git, lint by default.
const { execSync } = require("node:child_process");

let changed = true;
try {
  changed = /\.tsx?(\s|$)/m.test(execSync("git status --porcelain", { encoding: "utf8" }));
} catch {
  /* no git repository, so lint */
}
if (changed) execSync("npm run lint", { stdio: "inherit" });
