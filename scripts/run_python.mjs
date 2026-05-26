import { spawnSync } from "node:child_process";

const script = process.argv[2];
const extra = process.argv.slice(3);

if (!script) {
  console.error("Usage: node scripts/run_python.mjs <script.py> [args...]");
  process.exit(2);
}

const env = { ...process.env };
const separator = process.platform === "win32" ? ";" : ":";
const pathEntries = [];
if (env.CARGO_HOME) {
  pathEntries.push(`${env.CARGO_HOME}/bin`);
}
if (env.USERPROFILE) {
  pathEntries.push(`${env.USERPROFILE}\\.cargo\\bin`);
}
if (env.HOME) {
  pathEntries.push(`${env.HOME}/.cargo/bin`);
}
const currentPath = env.PATH ?? env.Path ?? "";
if (pathEntries.length > 0) {
  env.PATH = `${pathEntries.join(separator)}${separator}${currentPath}`;
}
const candidates = [];

if (env.PIANKE_PYTHON) {
  candidates.push({ cmd: env.PIANKE_PYTHON, args: [] });
}
if (env.CONDA_PREFIX) {
  candidates.push({ cmd: `${env.CONDA_PREFIX}\\python.exe`, args: [] });
}


candidates.push(
  { cmd: "python", args: [] },
  { cmd: "python3", args: [] },
  { cmd: "python3.11", args: [] },
  { cmd: "py", args: ["-3"] }
);

function probe(candidate) {
  const result = spawnSync(candidate.cmd, [...candidate.args, "--version"], {
    cwd: process.cwd(),
    env,
    stdio: "ignore",
  });

  if (result.error) {
    return false;
  }

  return (result.status ?? 1) === 0;
}

for (const candidate of candidates) {
  if (!probe(candidate)) {
    continue;
  }

  const result = spawnSync(candidate.cmd, [...candidate.args, script, ...extra], {
    cwd: process.cwd(),
    env,
    stdio: "inherit",
  });

  if (result.error) {
    console.error(result.error.message);
    process.exit(1);
  }

  process.exit(result.status ?? 0);
}

console.error("No usable Python interpreter found (tried: PIANKE_PYTHON, CONDA_PREFIX\\python.exe, python, python3, python3.11, py -3).");
process.exit(1);
