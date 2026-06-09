#!/usr/bin/env python3
"""Analyze comma-based naming patterns in USDA-style food names."""

from __future__ import annotations

import argparse
import csv
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

DEFAULT_INPUT = Path(
    r"c:\Users\USERR\Documents\0. Mata Kuliah\8 -TA\Code\TugasAkhirDSS\A. Data\Data Processed\05_final_dataset.csv"
)


def normalize_segment(text: str) -> str:
    return " ".join(text.strip().lower().split())


def read_rows(input_csv: Path) -> List[dict]:
    with input_csv.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        raise ValueError("CSV tidak memiliki baris data.")
    return rows


def detect_name_column(fieldnames: Iterable[str]) -> str:
    names = list(fieldnames)
    if "food_name" in names:
        return "food_name"

    lowered = {c.lower(): c for c in names}
    for key in ("food_name", "name", "description"):
        if key in lowered:
            return lowered[key]

    for c in names:
        cl = c.lower()
        if "name" in cl or "food" in cl or "description" in cl:
            return c

    raise ValueError("Kolom nama makanan tidak ditemukan.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analisis pola koma nama makanan.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path CSV input")
    parser.add_argument("--outdir", type=Path, default=Path(__file__).parent / "output", help="Folder output")
    parser.add_argument("--topn", type=int, default=10, help="Jumlah top item per tabel")
    args = parser.parse_args()

    input_csv: Path = args.input
    outdir: Path = args.outdir
    topn: int = args.topn

    if not input_csv.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {input_csv}")

    rows = read_rows(input_csv)
    name_col = detect_name_column(rows[0].keys())
    group_col = "food_group" if "food_group" in rows[0] else None

    names: List[str] = []
    groups: List[str] = []

    for r in rows:
        raw_name = (r.get(name_col) or "").strip()
        if not raw_name:
            continue
        names.append(raw_name)
        groups.append((r.get(group_col) or "").strip() if group_col else "")

    total = len(names)
    if total == 0:
        raise ValueError("Tidak ada nama makanan valid untuk dianalisis.")

    comma_distribution: Counter = Counter()
    samples_by_comma: Dict[int, List[str]] = defaultdict(list)

    segments_by_position: Dict[int, List[str]] = defaultdict(list)
    last2_counter: Counter = Counter()
    last3_counter: Counter = Counter()

    # pyrefly: ignore [bad-assignment]
    group_stats: Dict[str, Dict[str, float]] = defaultdict(lambda: {"n": 0, "sum_comma": 0, "ge5": 0})

    for idx, name in enumerate(names):
        comma_count = name.count(",")
        comma_distribution[comma_count] += 1

        # Save up to 5 samples per comma count
        if len(samples_by_comma[comma_count]) < 5:
            samples_by_comma[comma_count].append(name)

        segments = [normalize_segment(s) for s in name.split(",")]

        for pos, seg in enumerate(segments[1:], start=1):
            if seg:
                segments_by_position[pos].append(seg)

        if len(segments) >= 3:
            last2_counter[" | ".join(segments[-2:])] += 1
        if len(segments) >= 4:
            last3_counter[" | ".join(segments[-3:])] += 1

        if group_col:
            g = groups[idx] or "(unknown)"
            group_stats[g]["n"] += 1
            group_stats[g]["sum_comma"] += comma_count
            if comma_count >= 5:
                group_stats[g]["ge5"] += 1

    # Reuse metric for last 2 segments
    eligible2 = 0
    reused2 = 0
    for name in names:
        segs = [normalize_segment(s) for s in name.split(",")]
        if len(segs) >= 3:
            eligible2 += 1
            key2 = " | ".join(segs[-2:])
            if last2_counter[key2] >= 5:
                reused2 += 1

    outdir.mkdir(parents=True, exist_ok=True)

    # Clean up old CSV analysis files if they exist to prevent clutter
    old_files = [
        "comma_distribution.csv",
        "top_segments_by_position.csv",
        "top_full_suffix_patterns.csv",
        "top_last2_patterns.csv",
        "top_last3_patterns.csv",
        "comma_count_samples.csv",
        "food_group_comma_stats.csv",
        "summary_report.txt"
    ]
    for filename in old_files:
        filepath = outdir / filename
        if filepath.exists():
            try:
                filepath.unlink()
            except Exception:
                pass

    # Build a single consolidated report
    report = []
    report.append("======================================================================")
    report.append("                  FOOD NAME COMMA ANALYSIS REPORT")
    report.append("======================================================================")
    report.append(f"Input file: {input_csv}")
    report.append(f"Total valid food names: {total}")
    report.append("")

    report.append("----------------------------------------------------------------------")
    report.append("1. COMMA DISTRIBUTION")
    report.append("----------------------------------------------------------------------")
    for k, v in sorted(comma_distribution.items(), key=lambda x: x[0]):
        report.append(f"- {k} koma: {v} ({v / total * 100:.2f}%)")
    report.append("")

    report.append("----------------------------------------------------------------------")
    report.append("2. TOP SEGMENTS BY POSITION AFTER BASE NAME")
    report.append("----------------------------------------------------------------------")
    for pos in sorted(segments_by_position)[:4]:  # Show top 4 positions
        counter = Counter(segments_by_position[pos])
        total_pos = sum(counter.values())
        report.append(f"[Posisi {pos} setelah Base Name] (Total segmen: {total_pos})")
        for seg, cnt in counter.most_common(5):  # top 5 per position
            report.append(f"  - {seg:25s}: {cnt:4d} ({cnt / total_pos * 100:.2f}%)")
    report.append("")

    report.append("----------------------------------------------------------------------")
    report.append("3. TOP LAST-2 & LAST-3 PATTERNS")
    report.append("----------------------------------------------------------------------")
    report.append(f"Pola 2 segmen terakhir yang dipakai ulang >= 5x: {reused2}/{eligible2} ({(reused2 / eligible2 * 100) if eligible2 else 0:.1f}%)")
    report.append("")
    report.append("[Top 10 Pola 2 Segmen Terakhir]")
    for pat, cnt in last2_counter.most_common(10):
        report.append(f"  - {pat:40s}: {cnt}x")
    report.append("")
    report.append("[Top 5 Pola 3 Segmen Terakhir]")
    for pat, cnt in last3_counter.most_common(5):
        report.append(f"  - {pat:40s}: {cnt}x")
    report.append("")

    if group_col:
        report.append("----------------------------------------------------------------------")
        report.append("4. FOOD GROUP STATS")
        report.append("----------------------------------------------------------------------")
        group_rows = []
        for g, stats in group_stats.items():
            n = int(stats["n"])
            mean_comma = (stats["sum_comma"] / n) if n else 0.0
            ge5_pct = (stats["ge5"] / n * 100) if n else 0.0
            group_rows.append((g, n, mean_comma, ge5_pct))

        group_rows.sort(key=lambda x: x[2], reverse=True)
        report.append(f"{'Food Group':40s} | {'N':5s} | {'Mean Comma':10s} | {'% Comma >= 5':12s}")
        report.append("-" * 75)
        for g, n, mean_c, ge5_p in group_rows[:15]:  # Top 15 food groups
            report.append(f"{g[:40]:40s} | {n:5d} | {mean_c:10.2f} | {ge5_p:11.1f}%")
        report.append("")

    report.append("----------------------------------------------------------------------")
    report.append("5. SAMPLES BY COMMA COUNT")
    report.append("----------------------------------------------------------------------")
    for comma_count in sorted(samples_by_comma):
        report.append(f"[{comma_count} Koma]")
        for sample in samples_by_comma[comma_count]:
            report.append(f"  - {sample}")
    report.append("")

    report_path = outdir / "comma_analysis_report.txt"
    report_path.write_text("\n".join(report), encoding="utf-8")

    print(f"[OK] Analisis selesai. File laporan tunggal berhasil disimpan ke:")
    print(f"     {report_path}")


if __name__ == "__main__":
    main()
