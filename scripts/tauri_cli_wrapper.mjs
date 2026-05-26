import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const tauriJs = path.join(root, "node_modules", "@tauri-apps", "cli", "tauri.js");

if (!existsSync(tauriJs)) {
  console.error("Cannot find @tauri-apps/cli. Please run npm ci first.");
  process.exit(1);
}

const env = { ...process.env };

if (env.CI === "1") {
  env.CI = "true";
}

const pathEntries = [];
if (env.CARGO_HOME) {
  pathEntries.push(path.join(env.CARGO_HOME, "bin"));
}
if (env.USERPROFILE) {
  pathEntries.push(path.join(env.USERPROFILE, ".cargo", "bin"));
}
if (env.HOME) {
  pathEntries.push(path.join(env.HOME, ".cargo", "bin"));
}

const separator = process.platform === "win32" ? ";" : ":";
const currentPath = env.PATH ?? env.Path ?? "";
const uniqueEntries = [];
for (const entry of pathEntries) {
  if (!entry) continue;
  if (!existsSync(entry)) continue;
  const lower = process.platform === "win32" ? entry.toLowerCase() : entry;
  if (uniqueEntries.some((v) => (process.platform === "win32" ? v.toLowerCase() : v) === lower)) continue;
  uniqueEntries.push(entry);
}

if (uniqueEntries.length > 0) {
  env.PATH = `${uniqueEntries.join(separator)}${separator}${currentPath}`;
}

const args = process.argv.slice(2);
const result = spawnSync(process.execPath, [tauriJs, ...args], {
  cwd: root,
  env,
  stdio: "inherit",
});

if (result.error) {
  console.error(result.error.message);
  process.exit(1);
}

process.exit(result.status ?? 0);
