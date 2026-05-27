"""清理质量筛选实验 worktree。

用法:
    python scripts/cleanup_worktrees.py             # 删除全部 3 个
    python scripts/cleanup_worktrees.py --only A     # 只删除 Worktree A
    python scripts/cleanup_worktrees.py --dry-run    # 预览不执行
"""
import argparse
import os
import shutil
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
    },
    "B": {
        "branch": "wt-wavelet-noise",
        "dir": "experiments/wt-wavelet-noise",
    },
    "C": {
        "branch": "wt-u2net-saliency",
        "dir": "experiments/wt-u2net-saliency",
    },
}


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, cwd=ROOT, capture_output=True, text=True)


def cleanup_one(key: str, dry_run: bool) -> None:
    wt = WORKTREES[key]
    branch = wt["branch"]
    wt_dir = ROOT / wt["dir"]

    if not wt_dir.exists():
        print(f"  [SKIP] Worktree {key} ({branch}) 不存在")
        # 尝试删除孤立分支
        try:
            if dry_run:
                print(f"         [dry-run] git branch -D {branch}")
            else:
                run(["git", "branch", "-D", branch])
                print(f"         已删除孤立分支 {branch}")
        except subprocess.CalledProcessError:
            pass
        return

    print(f"  [REMOVE] Worktree {key}: {branch}")
    print(f"           目录: {wt_dir}")

    if dry_run:
        print(f"         [dry-run] 删除目录 {wt_dir}")
        print(f"         [dry-run] git branch -D {branch}")
        return

    # 先移除 worktree
    try:
        run(["git", "worktree", "remove", str(wt_dir)])
    except subprocess.CalledProcessError:
        # worktree 可能已被移除，直接删目录
        pass

    # 删除目录（如果还在）
    if wt_dir.exists():
        shutil.rmtree(wt_dir)

    # 删除分支
    try:
        run(["git", "branch", "-D", branch])
    except subprocess.CalledProcessError:
        pass

    print(f"           ✓ 已清理")


def main() -> None:
    parser = argparse.ArgumentParser(description="清理质量筛选实验 worktree")
    parser.add_argument(
        "--only",
        nargs="?",
        default=None,
        help="只删除指定的 worktree，如 --only A 或 --only A,B,C",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览操作，不实际执行",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  片刻 — 质量筛选算法实验 Worktree 清理")
    if args.dry_run:
        print("  [DRY RUN] 仅预览，不执行")
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
        cleanup_one(key, args.dry_run)
        print()

    # 清理空的 experiments 目录
    exp_dir = ROOT / "experiments"
    if exp_dir.exists() and not any(exp_dir.iterdir()):
        if not args.dry_run:
            exp_dir.rmdir()
            print(f"  已删除空目录: {exp_dir}")
        else:
            print(f"  [dry-run] 将删除空目录: {exp_dir}")

    print("=" * 60)
    print("  完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
