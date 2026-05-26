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
        "--hidden-import",
        "imagehash",
        "--hidden-import",
        "scipy",
        "--collect-submodules",
        "flask",
        "--collect-submodules",
        "pillow_heif",
        "--collect-submodules",
        "piexif",
        "--hidden-import",
        "cv2",
        "--collect-data",
        "cv2",
        # 专家/土豪模式依赖
        "--collect-submodules",
        "torch",
        "--collect-submodules",
        "torchvision",
        "--collect-submodules",
        "transformers",
        "--collect-submodules",
        "insightface",
        "--collect-submodules",
        "onnxruntime",
        "--collect-submodules",
        "pyiqa",
        "--collect-submodules",
        "timm",
        "--collect-submodules",
        "openai",
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

    # Tauri externalBin 会自动在 binaries/pianke-backend 后追加 target 后缀。
    # 因此这里必须产出 binaries/pianke-backend-<target>.exe，plain 名称不会被打包器识别。
    final_path = BIN_DIR / out_name
    # Windows 上旧 exe 可能被占用，先尝试删除再用重试机制复制
    if final_path.exists():
        try:
            final_path.unlink()
        except PermissionError:
            pass  # 被占用，下面 copy2 会重试
    for attempt in range(5):
        try:
            shutil.copy2(built, final_path)
            break
        except PermissionError:
            if attempt < 4:
                import time
                print(f"文件被占用，等待重试... ({attempt + 1}/5)")
                time.sleep(3)
            else:
                raise RuntimeError(
                    f"无法复制 sidecar 到 {final_path}，文件可能被其他进程占用。"
                    f"请关闭可能使用该文件的程序后重试。"
                )

    print(f"Sidecar ready: {final_path}")
    return final_path


if __name__ == "__main__":
    maybe_reexec_in_project_venv()
    raise SystemExit(0 if build_sidecar() else 1)
