from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SRC_TAURI = ROOT / "src-tauri"
BIN_DIR = SRC_TAURI / "binaries"
BUILD_DIR = ROOT / ".tauri-sidecar-build"
DIST_DIR = BUILD_DIR / "dist"
WORK_DIR = BUILD_DIR / "work"
SPEC_DIR = BUILD_DIR / "spec"
REEXEC_ENV = "PIANKE_TAURI_BUILD_REEXEC"


def preferred_python() -> Path | None:
    if os.name == "nt":
        candidate = ROOT / ".venv" / "Scripts" / "python.exe"
    else:
        candidate = ROOT / ".venv" / "bin" / "python"
    return candidate if candidate.exists() else None


def maybe_reexec_in_project_venv() -> None:
    if os.environ.get(REEXEC_ENV) == "1":
        return
    preferred = preferred_python()
    if not preferred:
        return
    if Path(sys.executable).resolve() == preferred.resolve():
        return

    env = os.environ.copy()
    env[REEXEC_ENV] = "1"
    print(f"Re-exec build with project venv: {preferred}")
    raise SystemExit(subprocess.call([str(preferred), __file__], cwd=ROOT, env=env))


def rust_host_target() -> str:
    output = subprocess.check_output(["rustc", "-vV"], text=True, cwd=ROOT)
    for line in output.splitlines():
        if line.startswith("host: "):
            return line.split("host: ", 1)[1].strip()
    raise RuntimeError("无法识别 rust host target")


def data_arg(source: Path, target: str) -> str:
    sep = ";" if os.name == "nt" else ":"
    return f"{source}{sep}{target}"


def ensure_pyinstaller() -> None:
    try:
        import PyInstaller  # noqa: F401
    except Exception as exc:
        raise RuntimeError(
            "缺少 PyInstaller。请先执行 `pip install -r requirements-desktop-build.txt`。"
        ) from exc


def build_sidecar() -> Path:
    ensure_pyinstaller()
    target = rust_host_target()
    is_win = os.name == "nt"
    suffix = ".exe" if is_win else ""
    out_name = f"pianke-backend-{target}{suffix}"

    shutil.rmtree(BUILD_DIR, ignore_errors=True)
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    SPEC_DIR.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name",
        "pianke-backend",
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(WORK_DIR),
        "--specpath",
        str(SPEC_DIR),
        "--paths",
        str(ROOT),
        "--add-data",
        data_arg(ROOT / "static", "static"),
        "--add-data",
        data_arg(ROOT / "assets", "assets"),
        "--collect-submodules",
        "pic_selecter",
        "--hidden-import",
        "pillow_heif",
        "--hidden-import",
        "piexif",
    ]
    if is_win:
        cmd.append("--noconsole")
    cmd.append(str(ROOT / "app.py"))

    print("Building Tauri sidecar:")
    print(" ".join(cmd))
    subprocess.check_call(cmd, cwd=ROOT)

    built = DIST_DIR / f"pianke-backend{suffix}"
    if not built.exists():
        raise RuntimeError(f"未找到打包产物：{built}")

    final_path = BIN_DIR / out_name
    shutil.copy2(built, final_path)
    print(f"Sidecar ready: {final_path}")
    return final_path


if __name__ == "__main__":
    maybe_reexec_in_project_venv()
    raise SystemExit(0 if build_sidecar() else 1)
