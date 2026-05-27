"""创建质量筛选实验 worktree。

用法:
    python scripts/setup_worktrees.py              # 创建全部 3 个
    python scripts/setup_worktrees.py --only A      # 只创建 Worktree A
    python scripts/setup_worktrees.py --only B,C    # 创建 B 和 C

每个 worktree 在 experiments/ 目录下，基于当前分支创建独立实验分支。
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

# Windows 控制台 UTF-8 编码修复
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    os.environ["PYTHONIOENCODING"] = "utf-8"

ROOT = Path(__file__).resolve().parent.parent

WORKTREES = {
    "A": {
        "branch": "wt-maniqa-norm",
        "dir": "experiments/wt-maniqa-norm",
        "desc": "MANIQA 替代 NIMA + 批次归一化",
    },
    "B": {
        "branch": "wt-wavelet-noise",
        "dir": "experiments/wt-wavelet-noise",
        "desc": "小波锐度 + PCA 噪声检测",
    },
    "C": {
        "branch": "wt-u2net-saliency",
        "dir": "experiments/wt-u2net-saliency",
        "desc": "U²-Net 显著性检测",
    },
}


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, cwd=ROOT, capture_output=True, text=True)


def setup_one(key: str) -> None:
    wt = WORKTREES[key]
    branch = wt["branch"]
    wt_dir = ROOT / wt["dir"]

    if wt_dir.exists():
        print(f"  [SKIP] Worktree {key} ({branch}) 已存在: {wt_dir}")
        return

    print(f"  [CREATE] Worktree {key}: {wt['desc']}")
    print(f"           分支: {branch}")
    print(f"           目录: {wt_dir}")

    # 创建分支
    try:
        run(["git", "branch", branch])
    except subprocess.CalledProcessError:
        # 分支已存在，不报错
        pass

    # 创建 worktree
    run(["git", "worktree", "add", str(wt_dir), branch])
    print(f"           ✓ 创建成功")


def main() -> None:
    parser = argparse.ArgumentParser(description="创建质量筛选实验 worktree")
    parser.add_argument(
        "--only",
        nargs="?",
        default=None,
        help="只创建指定的 worktree，如 --only A 或 --only A,B,C",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  片刻 — 质量筛选算法实验 Worktree 创建")
    print("=" * 60)

    if args.only:
        keys = [k.strip() for k in args.only.split(",")]
    else:
        keys = list(WORKTREES.keys())

    for key in keys:
        if key not in WORKTREES:
            print(f"  [ERROR] 未知 worktree: {key}（可选: A, B, C）")
            sys.exit(1)

    print()
    for key in keys:
        setup_one(key)
        print()

    print("=" * 60)
    print("  完成！进入 worktree:")
    for key in keys:
        wt = WORKTREES[key]
        print(f"    cd {ROOT / wt['dir']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
