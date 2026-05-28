"""Minimal manual_json metric test for Stage 0A.

This test constructs:
- one correct size-ratio case;
- one wrong size-ratio case;
- one correct boundary-fraction case;
- one wrong boundary-fraction case.

It does not run a real detector, attention extraction, guidance, Stage 1, or Stage 2.
"""

import json
import argparse
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ratio_dist.data.schemas import BOUNDARY_FRACTION, SIZE_RATIO, write_jsonl
from ratio_dist.evaluation.detect_segment import run_manual_json
from ratio_dist.evaluation.geometry_metrics import run_metrics
from ratio_dist.evaluation.make_metric_sanity_report import build_report


DEFAULT_FIXTURE = ROOT / "tests" / "fixtures" / "stage0a_manual_example_detections.jsonl"


def _size_prompt(prompt_id, target, obj_a, obj_b):
    return {
        "prompt_id": prompt_id,
        "prompt": "A synthetic size-ratio prompt for manual_json testing.",
        "task_type": SIZE_RATIO,
        "objects": [{"id": "obj_a", "name": obj_a}, {"id": "obj_b", "name": obj_b}],
        "constraint_graph": {
            "relations": [{"type": SIZE_RATIO, "subjects": ["obj_a", "obj_b"], "target": target}],
            "canvas": {"width": 1.0, "height": 1.0},
        },
    }


def _boundary_prompt(prompt_id, target, obj):
    return {
        "prompt_id": prompt_id,
        "prompt": "A synthetic boundary-fraction prompt for manual_json testing.",
        "task_type": BOUNDARY_FRACTION,
        "objects": [{"id": "obj_a", "name": obj}],
        "constraint_graph": {
            "relations": [{"type": BOUNDARY_FRACTION, "subjects": ["obj_a"], "target": target}],
            "canvas": {"width": 1.0, "height": 1.0},
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manual-json", default=str(DEFAULT_FIXTURE))
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        prompts_path = root / "prompts.jsonl"
        generations_path = root / "generations.jsonl"
        detections_path = root / "detections.jsonl"
        metrics_path = root / "metrics.jsonl"
        summary_path = root / "summary.json"
        report_path = root / "metric_sanity_report.md"

        prompts = [
            _size_prompt("size_ratio_000", 0.5, "ball", "cup"),
            _size_prompt("size_ratio_001", 0.5, "vase", "orange"),
            _boundary_prompt("boundary_fraction_000", 0.25, "orange"),
            _boundary_prompt("boundary_fraction_001", 2.0 / 3.0, "clock"),
        ]
        generations = [
            {"generation_id": p["prompt_id"] + "_sample_00", "prompt_id": p["prompt_id"], "prompt": p["prompt"], "image_path": "dummy.ppm", "method": "test"}
            for p in prompts
        ]

        write_jsonl(prompts_path, prompts)
        write_jsonl(generations_path, generations)
        run_manual_json(args.manual_json, detections_path)
        metrics, summary = run_metrics(prompts_path, generations_path, detections_path, metrics_path, summary_path)
        build_report(prompts_path, generations_path, detections_path, metrics_path, summary_path, report_path)

        by_id = {m["prompt_id"]: m for m in metrics}
        assert by_id["size_ratio_000"]["size_ratio_success_0_25"] is True
        assert by_id["size_ratio_001"]["size_ratio_success_0_25"] is False
        assert by_id["boundary_fraction_000"]["boundary_success_0_08"] is True
        assert by_id["boundary_fraction_001"]["boundary_success_0_08"] is False

        report = report_path.read_text(encoding="utf-8")
        assert "Detector modes: manual_json" in report
        assert "Allowed to enter Stage 1 based on this run: **NO**" in report
        assert "not all human_verified or external_detector" in report
        assert summary["image_level_detection_coverage"] == 1.0
        assert summary["object_level_detection_coverage"] == 1.0

        expanded_generations_path = root / "generations_20.jsonl"
        expanded_metrics_path = root / "metrics_20.jsonl"
        expanded_summary_path = root / "summary_20.json"
        expanded_report_path = root / "metric_sanity_report_20.md"
        expanded_generations = list(generations)
        for idx in range(16):
            prompt = prompts[idx % len(prompts)]
            expanded_generations.append(
                {
                    "generation_id": "missing_%02d_sample_00" % idx,
                    "prompt_id": prompt["prompt_id"],
                    "prompt": prompt["prompt"],
                    "image_path": "missing_%02d.ppm" % idx,
                    "method": "test",
                }
            )
        write_jsonl(expanded_generations_path, expanded_generations)
        expanded_metrics, expanded_summary = run_metrics(
            prompts_path,
            expanded_generations_path,
            detections_path,
            expanded_metrics_path,
            expanded_summary_path,
        )
        build_report(
            prompts_path,
            expanded_generations_path,
            detections_path,
            expanded_metrics_path,
            expanded_summary_path,
            expanded_report_path,
        )
        expanded_report = expanded_report_path.read_text(encoding="utf-8")
        assert expanded_summary["generation_count"] == 20
        assert expanded_summary["detection_record_count"] == 4
        assert expanded_summary["image_level_detection_coverage"] == 0.2
        assert expanded_summary["missing_detection_count"] == 16
        assert "Image-level detection coverage: 0.2" in expanded_report
        assert "Missing detection count: 16" in expanded_report
        assert "Image-level detection coverage is below 1.0." in expanded_report

        print("manual_json Stage 0A metric test passed")
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
