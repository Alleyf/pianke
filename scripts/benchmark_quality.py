"""质量评估基准测试脚本。

对指定文件夹跑质量评估，输出结构化 JSON 报告。
在各 worktree 中运行，对比不同算法的效果。

用法:
    python scripts/benchmark_quality.py <照片文件夹> --label baseline
    python scripts/benchmark_quality.py <照片文件夹> --label maniqa-norm --engine expert
    python scripts/benchmark_quality.py <照片文件夹> --label wavelet-noise --engine fast

输出: experiments/results/{label}.json
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import numpy as np

# 确保项目根目录在 sys.path（worktree 中也能 import pic_selecter）
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from PIL import Image

from pic_selecter.quality import QualityInfo, analyze_image

logger = logging.getLogger("benchmark")


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".heic", ".heif"}


def load_image(path: Path) -> Image.Image | None:
    """加载图片，支持 HEIC。"""
    try:
        return Image.open(path)
    except Exception:
        pass
    try:
        import pillow_heif
        if path.suffix.lower() in {".heic", ".heif"}:
            pillow_heif.register_heif_opener()
            return Image.open(path)
    except ImportError:
        pass
    return None


def analyze_one(path: Path, engine: str, strength: str) -> dict | None:
    """分析单张照片，返回结果 dict。"""
    img = load_image(path)
    if img is None:
        return None

    file_size = path.stat().st_size

    try:
        if engine == "fast":
            from pic_selecter.fast_quality import analyze_image_fast
            qi = analyze_image_fast(img, file_size, strength=strength)
        else:
            qi = analyze_image(img, file_size, strength=strength, face_aware=False)
        return {
            "path": str(path.relative_to(path.parent.parent if path.parent.name == "experiments" else path.parent)),
            "name": path.name,
            "file_size": file_size,
            "width": qi.width,
            "height": qi.height,
            "quality_score": qi.quality_score,
            "blur_score": qi.blur_score,
            "brightness_mean": qi.brightness_mean,
            "contrast_score": qi.contrast_score,
            "entropy": qi.entropy,
            "flags": qi.flags,
            "auto_reject": qi.auto_reject,
            "reject_reason": qi.reject_reason,
            "salient_sharpness": qi.salient_sharpness,
            "aesthetic_score": qi.aesthetic_score,
            "musiq_score": qi.musiq_score,
            "clipiqa_score": qi.clipiqa_score,
            "maniqa_score": getattr(qi, "maniqa_score", None),
            "noise_level": getattr(qi, "noise_level", None),
            "wavelet_sharpness": getattr(qi, "wavelet_sharpness", None),
            "blur_combined": qi.blur_combined,
            "composition": qi.composition,
        }
    except Exception as e:
        logger.warning(f"分析失败 {path.name}: {e}")
        return {
            "path": str(path),
            "name": path.name,
            "file_size": file_size,
            "error": str(e),
            "auto_reject": False,
            "flags": [],
            "quality_score": 0.0,
        }


def compute_stats(results: list[dict]) -> dict:
    """计算整体统计。"""
    valid = [r for r in results if r is not None]
    if not valid:
        return {}

    total = len(valid)
    rejected = sum(1 for r in valid if r.get("auto_reject"))
    errored = sum(1 for r in valid if "error" in r)

    scores = [r["quality_score"] for r in valid if "error" not in r]
    flag_counts: dict[str, int] = {}
    reason_counts: dict[str, int] = {}
    for r in valid:
        for f in r.get("flags", []):
            flag_counts[f] = flag_counts.get(f, 0) + 1
        reason = r.get("reject_reason")
        if reason:
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

    blur_scores = [r["blur_score"] for r in valid if r.get("blur_score") is not None]
    aesthetic_scores = [r["aesthetic_score"] for r in valid if r.get("aesthetic_score") is not None]
    musiq_scores = [r["musiq_score"] for r in valid if r.get("musiq_score") is not None]
    clipiqa_scores = [r["clipiqa_score"] for r in valid if r.get("clipiqa_score") is not None]

    def dist_summary(vals: list[float]) -> dict | None:
        if not vals:
            return None
        a = np.array(vals)
        return {
            "count": len(vals),
            "mean": round(float(a.mean()), 3),
            "std": round(float(a.std()), 3),
            "min": round(float(a.min()), 3),
            "max": round(float(a.max()), 3),
            "p10": round(float(np.percentile(a, 10)), 3),
            "p25": round(float(np.percentile(a, 25)), 3),
            "p50": round(float(np.percentile(a, 50)), 3),
            "p75": round(float(np.percentile(a, 75)), 3),
            "p90": round(float(np.percentile(a, 90)), 3),
        }

    return {
        "total": total,
        "rejected": rejected,
        "rejected_pct": round(rejected / total * 100, 1),
        "errored": errored,
        "quality_score": dist_summary(scores),
        "blur_score": dist_summary(blur_scores),
        "aesthetic_score": dist_summary(aesthetic_scores),
        "musiq_score": dist_summary(musiq_scores),
        "clipiqa_score": dist_summary(clipiqa_scores),
        "flag_distribution": dict(sorted(flag_counts.items(), key=lambda x: -x[1])),
        "reject_reason_distribution": dict(sorted(reason_counts.items(), key=lambda x: -x[1])),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="质量评估基准测试")
    parser.add_argument("folder", type=Path, help="照片文件夹路径")
    parser.add_argument(
        "--label", default="benchmark",
        help="实验标签，用于输出文件名（默认: benchmark）",
    )
    parser.add_argument(
        "--engine", choices=["fast", "expert"], default="fast",
        help="评估引擎（默认: fast）",
    )
    parser.add_argument(
        "--strength", choices=["standard", "advanced"], default="advanced",
        help="评估力度（默认: advanced）",
    )
    parser.add_argument(
        "--output", type=Path, default=None,
        help="输出文件路径（默认: experiments/results/{label}.json）",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if not args.folder.exists():
        print(f"错误: 文件夹不存在: {args.folder}", file=sys.stderr)
        sys.exit(1)

    photos = sorted(args.folder.glob("*"))
    photos = [p for p in photos if p.suffix.lower() in IMAGE_EXTS]

    if not photos:
        print(f"错误: 文件夹中没有图片: {args.folder}", file=sys.stderr)
        sys.exit(1)

    print(f"照片文件夹: {args.folder}")
    print(f"图片数量: {len(photos)}")
    print(f"引擎: {args.engine}")
    print(f"力度: {args.strength}")
    print()

    results = []
    t0 = time.time()
    for i, path in enumerate(photos):
        if (i + 1) % 50 == 0 or i == 0:
            elapsed = time.time() - t0
            speed = (i + 1) / elapsed if elapsed > 0 else float("inf")
            remaining = (len(photos) - i - 1) / speed if speed > 0 else 0
            print(f"  [{i+1}/{len(photos)}] {speed:.1f} 张/秒, 剩余约 {remaining:.0f}s")
        result = analyze_one(path, args.engine, args.strength)
        if result:
            results.append(result)

    elapsed = time.time() - t0
    print(f"\n完成: {len(results)}/{len(photos)} 张, 耗时 {elapsed:.1f}s ({len(results)/elapsed:.1f} 张/秒)")

    stats = compute_stats(results)
    report = {
        "label": args.label,
        "engine": args.engine,
        "strength": args.strength,
        "folder": str(args.folder),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "elapsed_seconds": round(elapsed, 2),
        "photos_per_second": round(len(results) / elapsed, 1) if elapsed > 0 else 0,
        "stats": stats,
        "photos": results,
    }

    output = args.output or (ROOT / "experiments" / "results" / f"{args.label}.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\n报告已保存: {output}")

    # 打印摘要
    s = stats
    if s:
        print(f"\n{'='*50}")
        print(f"  摘要 ({args.label})")
        print(f"  总张数: {s['total']}")
        print(f"  自动淘汰: {s['rejected']} ({s['rejected_pct']}%)")
        print(f"  分析错误: {s['errored']}")
        qs = s.get("quality_score")
        if qs:
            print(f"  quality_score: mean={qs['mean']}, p10={qs['p10']}, p50={qs['p50']}, p90={qs['p90']}")
        blur = s.get("blur_score")
        if blur:
            print(f"  blur_score: mean={blur['mean']}, p10={blur['p10']}, p50={blur['p50']}, p90={blur['p90']}")
        print(f"  flags: {s.get('flag_distribution', {})}")
        print(f"{'='*50}")


if __name__ == "__main__":
    main()
