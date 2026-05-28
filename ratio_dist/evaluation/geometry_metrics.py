"""Task-specific geometric metrics for Stage 0A."""

import argparse
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Optional, Tuple

from ratio_dist.data.schemas import BOUNDARY_FRACTION, SIZE_RATIO, read_jsonl, write_jsonl


def box_area(box):
    return max(0.0, box["x2"] - box["x1"]) * max(0.0, box["y2"] - box["y1"])


def box_centroid(box):
    return ((box["x1"] + box["x2"]) / 2.0, (box["y1"] + box["y2"]) / 2.0)


def _find_detection(detections, object_id):
    for detection in detections:
        if detection.get("object_id") == object_id:
            return detection
    return None


def _required_object_ids(prompt):
    return [obj["id"] for obj in prompt.get("objects", [])]


def _empty_metric(generation, prompt, reason):
    required = _required_object_ids(prompt)
    return {
        "generation_id": generation["generation_id"],
        "prompt_id": prompt["prompt_id"],
        "task_type": prompt["task_type"],
        "detector_mode": "missing",
        "detection_missing": reason == "detection_missing",
        "all_required_detected": False,
        "required_object_count": len(required),
        "detected_required_object_count": 0,
        "missing_required_objects": required,
        "missing_reason": reason,
    }


def compute_record(prompt: dict, generation: dict, detection_record: dict) -> dict:
    relation = prompt["constraint_graph"]["relations"][0]
    detections = detection_record["detections"]
    required = _required_object_ids(prompt)
    missing_required = [object_id for object_id in required if _find_detection(detections, object_id) is None]
    metric = {
        "generation_id": generation["generation_id"],
        "prompt_id": prompt["prompt_id"],
        "task_type": prompt["task_type"],
        "detector_mode": detection_record.get("detector_mode", "unknown"),
        "detection_missing": False,
        "all_required_detected": not missing_required,
        "required_object_count": len(required),
        "detected_required_object_count": len(required) - len(missing_required),
        "missing_required_objects": missing_required,
    }

    if missing_required:
        if prompt["task_type"] == SIZE_RATIO:
            metric["size_ratio_err"] = None
        elif prompt["task_type"] == BOUNDARY_FRACTION:
            metric["boundary_err"] = None
        return metric

    if prompt["task_type"] == SIZE_RATIO:
        det_a = _find_detection(detections, "obj_a")
        det_b = _find_detection(detections, "obj_b")
        area_a = float(det_a.get("mask_area") or box_area(det_a["box"]))
        area_b = float(det_b.get("mask_area") or box_area(det_b["box"]))
        target = float(relation["target"])
        err = abs(math.log(((area_a + 1e-8) / (area_b + 1e-8)) / target))
        metric.update(
            {
                "area_a": area_a,
                "area_b": area_b,
                "target_ratio": target,
                "observed_ratio": area_a / max(area_b, 1e-8),
                "size_ratio_err": err,
                "size_ratio_success_0_25": err < 0.25,
                "size_ratio_success_0_5": err < 0.5,
            }
        )
    elif prompt["task_type"] == BOUNDARY_FRACTION:
        det_a = _find_detection(detections, "obj_a")
        cx, cy = box_centroid(det_a["box"])
        target = float(relation["target"])
        err = abs(cx - target)
        metric.update(
            {
                "centroid_x": cx,
                "centroid_y": cy,
                "target_fraction": target,
                "boundary_err": err,
                "boundary_success_0_08": err < 0.08,
                "boundary_success_0_12": err < 0.12,
            }
        )
    return metric


def summarize(metrics):
    size = [m for m in metrics if m["task_type"] == SIZE_RATIO and m.get("size_ratio_err") is not None]
    boundary = [m for m in metrics if m["task_type"] == BOUNDARY_FRACTION and m.get("boundary_err") is not None]
    generation_count = len(metrics)
    detection_record_count = sum(1 for m in metrics if not m.get("detection_missing"))
    detected_generation_count = sum(1 for m in metrics if not m.get("detection_missing"))
    total_required_object_count = sum(m.get("required_object_count", 0) for m in metrics)
    detected_required_object_count = sum(m.get("detected_required_object_count", 0) for m in metrics)
    missing_detection_count = sum(1 for m in metrics if m.get("detection_missing"))
    missing_required_object_count = total_required_object_count - detected_required_object_count
    return {
        "num_images": generation_count,
        "generation_count": generation_count,
        "detection_record_count": detection_record_count,
        "detected_generation_count": detected_generation_count,
        "image_level_detection_coverage": detected_generation_count / max(1, generation_count),
        "total_required_object_count": total_required_object_count,
        "detected_required_object_count": detected_required_object_count,
        "object_level_detection_coverage": detected_required_object_count / max(1, total_required_object_count),
        "missing_detection_count": missing_detection_count,
        "missing_required_object_count": missing_required_object_count,
        "detection_rate": detected_required_object_count / max(1, total_required_object_count),
        "size_ratio_count": len(size),
        "size_ratio_err_mean": mean([m["size_ratio_err"] for m in size]) if size else None,
        "size_ratio_success_0_25": mean([1.0 if m["size_ratio_success_0_25"] else 0.0 for m in size]) if size else None,
        "size_ratio_success_0_5": mean([1.0 if m["size_ratio_success_0_5"] else 0.0 for m in size]) if size else None,
        "boundary_count": len(boundary),
        "boundary_err_mean": mean([m["boundary_err"] for m in boundary]) if boundary else None,
        "boundary_success_0_08": mean([1.0 if m["boundary_success_0_08"] else 0.0 for m in boundary]) if boundary else None,
        "boundary_success_0_12": mean([1.0 if m["boundary_success_0_12"] else 0.0 for m in boundary]) if boundary else None,
    }


def run_metrics(prompts_path, generations_path, detections_path, output_path, summary_path):
    prompts = {p["prompt_id"]: p for p in read_jsonl(prompts_path)}
    generations = read_jsonl(generations_path)
    detections = read_jsonl(detections_path)
    generation_ids = {generation["generation_id"] for generation in generations}
    detection_by_generation_id = {}
    unknown_detection_generation_ids = []
    duplicate_detection_generation_ids = []
    for detection in detections:
        generation_id = detection["generation_id"]
        if generation_id not in generation_ids:
            unknown_detection_generation_ids.append(generation_id)
            continue
        if generation_id in detection_by_generation_id:
            duplicate_detection_generation_ids.append(generation_id)
        detection_by_generation_id[generation_id] = detection
    if unknown_detection_generation_ids:
        raise ValueError(
            "Detections contain generation_id values not present in generations.jsonl: "
            + ", ".join(sorted(unknown_detection_generation_ids))
        )
    if duplicate_detection_generation_ids:
        raise ValueError(
            "Detections contain duplicate generation_id values: "
            + ", ".join(sorted(set(duplicate_detection_generation_ids)))
        )

    metrics = []
    for generation in generations:
        prompt = prompts[generation["prompt_id"]]
        detection = detection_by_generation_id.get(generation["generation_id"])
        if detection is None:
            metrics.append(_empty_metric(generation, prompt, "detection_missing"))
        else:
            metrics.append(compute_record(prompt, generation, detection))
    summary = summarize(metrics)
    write_jsonl(output_path, metrics)
    summary_path = Path(summary_path)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return metrics, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", required=True)
    parser.add_argument("--generations", required=True)
    parser.add_argument("--detections", required=True)
    parser.add_argument("--output", default="data/results/stage0a/metrics.jsonl")
    parser.add_argument("--summary", default="data/results/stage0a/summary.json")
    args = parser.parse_args()
    metrics, summary = run_metrics(args.prompts, args.generations, args.detections, args.output, args.summary)
    print(f"Wrote {len(metrics)} metric records to {args.output}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
