from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BIN_DIR = ROOT / "src-tauri" / "binaries"
LEGACY_BUILD_DIR = BIN_DIR / ".build"


def rust_host_target() -> str:
    output = subprocess.check_output(["rustc", "-vV"], text=True, cwd=ROOT)
    for line in output.splitlines():
        if line.startswith("host: "):
            return line.split("host: ", 1)[1].strip()
    raise RuntimeError("无法识别 rust host target")


def main() -> None:
    if LEGACY_BUILD_DIR.exists():
        shutil.rmtree(LEGACY_BUILD_DIR, ignore_errors=True)
        print(f"Removed legacy watched build dir: {LEGACY_BUILD_DIR}")

    target = rust_host_target()
    suffix = ".exe" if os.name == "nt" else ""
    stub = BIN_DIR / f"pianke-backend-{target}{suffix}"
    if stub.exists():
        print(f"Stub already exists: {stub}")
        return

    BIN_DIR.mkdir(parents=True, exist_ok=True)
    stub.write_bytes(b"pianke sidecar stub\n")
    print(f"Created sidecar stub: {stub}")


if __name__ == "__main__":
    main()
