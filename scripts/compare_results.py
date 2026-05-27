"""对比多个质量评估实验结果。

读取 experiments/results/*.json，生成对比表格和 COMPARISON.md。

用法:
    python scripts/compare_results.py
    python scripts/compare_results.py --results experiments/results
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "experiments" / "results"


def load_results(results_dir: Path) -> dict[str, dict]:
    """加载所有 JSON 报告。"""
    reports = {}
    for f in sorted(results_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            label = data.get("label", f.stem)
            reports[label] = data
        except (json.JSONDecodeError, OSError) as e:
            print(f"  [WARN] 无法读取 {f}: {e}")
    return reports


def compare(reports: dict[str, dict]) -> str:
    """生成 Markdown 对比报告。"""
    if not reports:
        return "# 对比报告\n\n没有找到任何实验结果。"

    lines = []
    lines.append("# 质量筛选算法实验对比报告\n")
    lines.append(f"共 {len(reports)} 个实验结果\n")

    # 基本信息表
    lines.append("## 实验基本信息\n")
    lines.append("| 实验 | 引擎 | 力度 | 照片数 | 耗时 | 速度 |")
    lines.append("|------|------|------|--------|------|------|")
    for label, data in reports.items():
        engine = data.get("engine", "?")
        strength = data.get("strength", "?")
        stats = data.get("stats", {})
        total = stats.get("total", "?")
        elapsed = data.get("elapsed_seconds", "?")
        speed = data.get("photos_per_second", "?")
        lines.append(f"| {label} | {engine} | {strength} | {total} | {elapsed}s | {speed} 张/秒 |")
    lines.append("")

    # 核心指标对比
    lines.append("## 核心指标对比\n")
    lines.append("| 实验 | 总张数 | 淘汰数 | 淘汰率 | 错误数 | quality p10 | quality p50 | quality p90 |")
    lines.append("|------|--------|--------|--------|--------|-------------|-------------|-------------|")
    for label, data in reports.items():
        s = data.get("stats", {})
        total = s.get("total", 0)
        rejected = s.get("rejected", 0)
        pct = s.get("rejected_pct", "?")
        errored = s.get("errored", 0)
        qs = s.get("quality_score", {}) or {}
        p10 = qs.get("p10", "?")
        p50 = qs.get("p50", "?")
        p90 = qs.get("p90", "?")
        lines.append(f"| {label} | {total} | {rejected} | {pct}% | {errored} | {p10} | {p50} | {p90} |")
    lines.append("")

    # 锐度分布
    lines.append("## 锐度分布 (blur_score)\n")
    lines.append("| 实验 | 均值 | 标准差 | p10 | p25 | p50 | p75 | p90 |")
    lines.append("|------|------|--------|-----|-----|-----|-----|-----|")
    for label, data in reports.items():
        blur = (data.get("stats", {}) or {}).get("blur_score", {}) or {}
        lines.append(
            f"| {label} | {blur.get('mean', '?')} | {blur.get('std', '?')} | "
            f"{blur.get('p10', '?')} | {blur.get('p25', '?')} | "
            f"{blur.get('p50', '?')} | {blur.get('p75', '?')} | {blur.get('p90', '?')} |"
        )
    lines.append("")

    # 美学分数分布
    lines.append("## 美学分数分布\n")

    # 检查各实验使用的美学模型
    all_models = set()
    for data in reports.values():
        s = data.get("stats", {}) or {}
        for key in ("aesthetic_score", "musiq_score", "clipiqa_score", "maniqa_score"):
            if s.get(key):
                all_models.add(key)

    if all_models:
        lines.append("| 实验 |")
        for m in sorted(all_models):
            lines.append(f" {m} 均值 | {m} p50 |")
        lines.append("|------|")
        for m in sorted(all_models):
            lines.append(f" -------- | -------- |")
        line = "".join(lines[-2:])  # header + separator

        for label, data in reports.items():
            s = data.get("stats", {}) or {}
            row = f"| {label}|"
            for m in sorted(all_models):
                d = s.get(m, {}) or {}
                row += f" {d.get('mean', '?')} | {d.get('p50', '?')} |"
            lines.append(row)
    else:
        lines.append("_无美学分数数据（极速模式无美学模型）_\n")
    lines.append("")

    # Flag 分布对比
    lines.append("## Flag 分布对比\n")
    all_flags = set()
    for data in reports.items():
        pass
    for data in reports.values():
        s = data.get("stats", {}) or {}
        for f in s.get("flag_distribution", {}):
            all_flags.add(f)

    if all_flags:
        lines.append("| 实验 |")
        for f in sorted(all_flags):
            lines.append(f" {f} |")
        lines.append("|------|")
        lines.append("|".join(f" ------" for _ in all_flags) + "|\n")

        for label, data in reports.items():
            fd = (data.get("stats", {}) or {}).get("flag_distribution", {})
            row = f"| {label}|"
            for f in sorted(all_flags):
                row += f" {fd.get(f, 0)} |"
            lines.append(row)
    lines.append("")

    # 拒片原因分布
    lines.append("## 拒片原因分布\n")
    all_reasons = set()
    for data in reports.values():
        s = data.get("stats", {}) or {}
        for r in s.get("reject_reason_distribution", {}):
            all_reasons.add(r)

    if all_reasons:
        lines.append("| 实验 |")
        for r in sorted(all_reasons):
            lines.append(f" {r} |")
        lines.append("|------|")
        lines.append("|".join(f" ------" for _ in all_reasons) + "|\n")

        for label, data in reports.items():
            rd = (data.get("stats", {}) or {}).get("reject_reason_distribution", {})
            row = f"| {label}|"
            for r in sorted(all_reasons):
                row += f" {rd.get(r, 0)} |"
            lines.append(row)
    lines.append("")

    # 各实验详细照片列表对比
    lines.append("## 照片级对比（仅展示判定不一致的照片）\n")
    if len(reports) >= 2:
        # 取第一个实验为基准
        first_label = next(iter(reports))
        first_data = reports[first_label]
        first_photos = {p["name"]: p for p in first_data.get("photos", [])}

        lines.append(f"以 **{first_label}** 为基准，对比其他实验的判定差异：\n")

        for label, data in reports.items():
            if label == first_label:
                continue
            other_photos = {p["name"]: p for p in data.get("photos", [])}
            common = set(first_photos.keys()) & set(other_photos.keys())

            disagreements = []
            for name in sorted(common):
                f = first_photos[name]
                o = other_photos[name]
                f_reject = f.get("auto_reject", False)
                o_reject = o.get("auto_reject", False)
                if f_reject != o_reject:
                    disagreements.append((name, f_reject, o_reject, f.get("quality_score", "?"), o.get("quality_score", "?")))

            if disagreements:
                lines.append(f"### {first_label} vs {label}：{len(disagreements)} 张判定不同\n")
                lines.append("| 照片 | {first_label} 淘汰 | {label} 淘汰 | {first_label} 分数 | {label} 分数 |")
                lines.append("|------|-----------|-----------|-------------|-------------|")
                for name, f_r, o_r, f_s, o_s in disagreements:
                    lines.append(f"| {name} | {'✓' if f_r else '✗'} | {'✓' if o_r else '✗'} | {f_s} | {o_s} |")
                lines.append("")
            else:
                lines.append(f"**{first_label} vs {label}**：所有照片判定一致\n")

    lines.append("---\n")
    lines.append("*由 compare_results.py 自动生成*\n")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="对比质量评估实验结果")
    parser.add_argument(
        "--results", type=Path, default=RESULTS_DIR,
        help="结果目录（默认: experiments/results）",
    )
    args = parser.parse_args()

    if not args.results.exists():
        print(f"错误: 结果目录不存在: {args.results}", file=sys.stderr)
        sys.exit(1)

    reports = load_results(args.results)
    if not reports:
        print(f"在 {args.results} 中没有找到 JSON 报告文件", file=sys.stderr)
        sys.exit(1)

    print(f"加载了 {len(reports)} 个实验结果: {', '.join(reports.keys())}")

    md = compare(reports)
    output = args.results.parent / "COMPARISON.md"
    output.write_text(md, encoding="utf-8")
    print(f"对比报告已保存: {output}")
    print()
    print("摘要：")
    for label, data in reports.items():
        s = data.get("stats", {})
        print(f"  {label}: {s.get('rejected', 0)}/{s.get('total', 0)} 淘汰 ({s.get('rejected_pct', '?')}%)")


if __name__ == "__main__":
    main()
