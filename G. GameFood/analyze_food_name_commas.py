#!/usr/bin/env python3
"""Analyze comma-based naming patterns in USDA-style food names."""

from __future__ import annotations

import argparse
import csv
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


def write_csv(path: Path, headers: List[str], rows: Iterable[Iterable]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analisis pola koma nama makanan.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path CSV input")
    parser.add_argument("--outdir", type=Path, default=Path(__file__).parent / "output", help="Folder output")
    parser.add_argument("--topn", type=int, default=20, help="Jumlah top item per tabel")
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
    full_suffix_counter: Counter = Counter()
    last2_counter: Counter = Counter()
    last3_counter: Counter = Counter()

    # pyrefly: ignore [bad-assignment]
    group_stats: Dict[str, Dict[str, float]] = defaultdict(lambda: {"n": 0, "sum_comma": 0, "ge5": 0})

    for idx, name in enumerate(names):
        comma_count = name.count(",")
        comma_distribution[comma_count] += 1

        if len(samples_by_comma[comma_count]) < 8:
            samples_by_comma[comma_count].append(name)

        segments = [normalize_segment(s) for s in name.split(",")]

        for pos, seg in enumerate(segments[1:], start=1):
            if seg:
                segments_by_position[pos].append(seg)

        if len(segments) >= 2:
            full_suffix_counter[" | ".join(segments[1:])] += 1
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

    write_csv(
        outdir / "comma_distribution.csv",
        ["comma_count", "count", "percentage"],
        (
            (k, v, round(v / total * 100, 4))
            for k, v in sorted(comma_distribution.items(), key=lambda x: x[0])
        ),
    )

    segment_rows: List[Tuple[int, str, int, float]] = []
    for pos in sorted(segments_by_position):
        counter = Counter(segments_by_position[pos])
        total_pos = sum(counter.values())
        for seg, cnt in counter.most_common(topn):
            segment_rows.append((pos, seg, cnt, round(cnt / total_pos * 100, 4)))

    write_csv(
        outdir / "top_segments_by_position.csv",
        ["position_after_base", "segment", "count", "percentage_at_position"],
        segment_rows,
    )

    write_csv(
        outdir / "top_full_suffix_patterns.csv",
        ["pattern", "count"],
        full_suffix_counter.most_common(topn),
    )

    write_csv(
        outdir / "top_last2_patterns.csv",
        ["last2_pattern", "count"],
        last2_counter.most_common(topn),
    )

    write_csv(
        outdir / "top_last3_patterns.csv",
        ["last3_pattern", "count"],
        last3_counter.most_common(topn),
    )

    sample_rows = []
    for comma_count in sorted(samples_by_comma):
        for sample in samples_by_comma[comma_count]:
            sample_rows.append((comma_count, sample))

    write_csv(
        outdir / "comma_count_samples.csv",
        ["comma_count", "food_name_sample"],
        sample_rows,
    )

    if group_col:
        group_rows = []
        for g, stats in group_stats.items():
            n = int(stats["n"])
            mean_comma = (stats["sum_comma"] / n) if n else 0.0
            ge5_pct = (stats["ge5"] / n * 100) if n else 0.0
            group_rows.append((g, n, round(mean_comma, 4), round(ge5_pct, 4)))

        group_rows.sort(key=lambda x: x[2], reverse=True)
        write_csv(
            outdir / "food_group_comma_stats.csv",
            ["food_group", "n", "mean_comma", "pct_comma_ge_5"],
            group_rows,
        )

    report_lines = [
        "FOOD NAME COMMA ANALYSIS REPORT",
        "=" * 40,
        f"Input file: {input_csv}",
        f"Total valid food names: {total}",
        "",
        "Distribusi jumlah koma:",
    ]

    for k, v in sorted(comma_distribution.items(), key=lambda x: x[0]):
        report_lines.append(f"- {k} koma: {v} ({v / total * 100:.2f}%)")

    report_lines.extend(
        [
            "",
            "Temuan pola:",
            "- Segmen setelah koma menunjukkan descriptor berulang (state/proses/salt/grade).",
            f"- Last-2 pattern reused >=5x: {reused2}/{eligible2} ({(reused2 / eligible2 * 100) if eligible2 else 0:.1f}%).",
            "- Ini menunjukkan penggunaan koma bersifat terstruktur, bukan random.",
            "",
            "Top 10 pola 2 segmen terakhir:",
        ]
    )

    for pat, cnt in last2_counter.most_common(10):
        report_lines.append(f"- {pat}: {cnt}x")

    summary_path = outdir / "summary_report.txt"
    summary_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"[OK] Analisis selesai. Output folder: {outdir}")
    print(f"[OK] Ringkasan: {summary_path}")


if __name__ == "__main__":
    main()
