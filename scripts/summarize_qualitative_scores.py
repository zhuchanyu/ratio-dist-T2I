"""Summarize human qualitative inspection scores."""

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def _load_rows(path):
    rows = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for idx, row in enumerate(reader, start=2):
            raw_score = (row.get("score_0_1_2") or "").strip()
            if raw_score == "":
                continue
            try:
                score = int(raw_score)
            except ValueError as exc:
                raise ValueError(f"Line {idx}: score_0_1_2 must be 0, 1, or 2") from exc
            if score not in {0, 1, 2}:
                raise ValueError(f"Line {idx}: score_0_1_2 must be 0, 1, or 2")
            row["score"] = score
            rows.append(row)
    return rows


def _summarize(rows):
    by_task = defaultdict(list)
    for row in rows:
        by_task[row["task_type"]].append(row)

    task_summary = {}
    for task_type, task_rows in sorted(by_task.items()):
        counts = Counter(row["score"] for row in task_rows)
        total = len(task_rows)
        task_summary[task_type] = {
            "count": total,
            "score_0": counts.get(0, 0),
            "score_1": counts.get(1, 0),
            "score_2": counts.get(2, 0),
            "mean_score": sum(row["score"] for row in task_rows) / max(1, total),
            "success_score_ge_1": sum(1 for row in task_rows if row["score"] >= 1) / max(1, total),
            "success_score_2": sum(1 for row in task_rows if row["score"] == 2) / max(1, total),
        }

    total = len(rows)
    return {
        "status": "human_qualitative_summary",
        "score_definition": {
            "0": "does not satisfy the prompt",
            "1": "weakly satisfies the prompt",
            "2": "clearly satisfies the prompt",
        },
        "total_scored": total,
        "overall": {
            "score_0": sum(1 for row in rows if row["score"] == 0),
            "score_1": sum(1 for row in rows if row["score"] == 1),
            "score_2": sum(1 for row in rows if row["score"] == 2),
            "mean_score": sum(row["score"] for row in rows) / max(1, total),
            "success_score_ge_1": sum(1 for row in rows if row["score"] >= 1) / max(1, total),
            "success_score_2": sum(1 for row in rows if row["score"] == 2) / max(1, total),
        },
        "by_task": task_summary,
    }


def _write_report(path, rows, summary):
    lines = [
        "# Qualitative Inspection Report",
        "",
        "## Status",
        "",
        "This report summarizes human qualitative scores. It is not a replacement for trusted detector/segmenter metrics.",
        "",
        "## Score Definition",
        "",
        "- 0 = does not satisfy the prompt",
        "- 1 = weakly satisfies the prompt",
        "- 2 = clearly satisfies the prompt",
        "",
        "## Summary",
        "",
        f"- Total scored images: {summary['total_scored']}",
        f"- Overall mean score: {summary['overall']['mean_score']:.3f}",
        f"- Overall success score >= 1: {summary['overall']['success_score_ge_1']:.3f}",
        f"- Overall success score == 2: {summary['overall']['success_score_2']:.3f}",
        "",
        "## By Task",
        "",
        "| Task | Count | Score 0 | Score 1 | Score 2 | Mean | Success >=1 | Success ==2 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for task_type, values in summary["by_task"].items():
        lines.append(
            f"| {task_type} | {values['count']} | {values['score_0']} | {values['score_1']} | "
            f"{values['score_2']} | {values['mean_score']:.3f} | "
            f"{values['success_score_ge_1']:.3f} | {values['success_score_2']:.3f} |"
        )
    lines.extend(["", "## Per-Image Notes", ""])
    for row in rows:
        reason = (row.get("failure_reason") or "").strip()
        if reason:
            lines.append(f"- `{row['generation_id']}` score={row['score']}: {reason}")
        else:
            lines.append(f"- `{row['generation_id']}` score={row['score']}")
    lines.append("")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", required=True)
    parser.add_argument("--summary", default="reports/qualitative_summary.json")
    parser.add_argument("--report", default="reports/qualitative_inspection_report.md")
    args = parser.parse_args()

    rows = _load_rows(args.scores)
    summary = _summarize(rows)
    Path(args.summary).parent.mkdir(parents=True, exist_ok=True)
    Path(args.summary).write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_report(args.report, rows, summary)
    print(f"Wrote qualitative summary: {args.summary}")
    print(f"Wrote qualitative report: {args.report}")


if __name__ == "__main__":
    main()
