"""Detector/segmenter interface for Stage 0A.

The default stub mode emits deterministic boxes so the pipeline can run locally.
Real detector integration is intentionally not implemented in Stage 0A.

Manual JSON detection format, one JSON object per line:

{
  "generation_id": "size_ratio_000_sample_00",
  "prompt_id": "size_ratio_000",
  "image_path": "data/generated/stage0a/images/size_ratio_000_sample_00.ppm",
  "detector_mode": "manual_json",
  "verification_status": "unverified",
  "detections": [
    {
      "object_id": "obj_a",
      "name": "apple",
      "box": {"x1": 0.1, "y1": 0.2, "x2": 0.5, "y2": 0.6},
      "mask_area": 0.16,
      "confidence": 1.0,
      "source": "manual_json"
    }
  ]
}

Allowed verification_status values:
- "unverified": format-only manual JSON; never enough for Stage 1.
- "human_verified": manually checked boxes/masks.
- "external_detector": output from an external real detector/segmenter.
"""

import argparse
import math
from pathlib import Path

from ratio_dist.data.schemas import BOUNDARY_FRACTION, SIZE_RATIO, read_jsonl, write_jsonl


TRUSTED_MANUAL_STATUSES = {"human_verified", "external_detector"}


def _box(cx: float, cy: float, w: float, h: float) -> dict:
    x1 = max(0.0, cx - w / 2.0)
    y1 = max(0.0, cy - h / 2.0)
    x2 = min(1.0, cx + w / 2.0)
    y2 = min(1.0, cy + h / 2.0)
    return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}


def _stub_detections_for_prompt(prompt):
    relation = prompt["constraint_graph"]["relations"][0]
    detections = []
    if prompt["task_type"] == SIZE_RATIO:
        target = float(relation["target"])
        # Deliberately imperfect stub boxes: enough to test metric plumbing, not method quality.
        base_area = 0.08
        area_a = min(0.22, max(0.03, base_area * math.sqrt(target)))
        area_b = min(0.18, max(0.03, base_area / math.sqrt(target)))
        side_a = math.sqrt(area_a)
        side_b = math.sqrt(area_b)
        specs = [
            (prompt["objects"][0], _box(0.38, 0.52, side_a, side_a)),
            (prompt["objects"][1], _box(0.66, 0.52, side_b, side_b)),
        ]
    elif prompt["task_type"] == BOUNDARY_FRACTION:
        target = float(relation["target"])
        specs = [(prompt["objects"][0], _box(target + 0.05, 0.5, 0.22, 0.22))]
    else:
        specs = []

    for obj, box in specs:
        detections.append(
            {
                "object_id": obj["id"],
                "name": obj["name"],
                "box": box,
                "mask_area": (box["x2"] - box["x1"]) * (box["y2"] - box["y1"]),
                "confidence": 1.0,
                "source": "stub",
            }
        )
    return detections


def run_stub(prompts_path, generations_path, output_path):
    prompts = {p["prompt_id"]: p for p in read_jsonl(prompts_path)}
    generations = read_jsonl(generations_path)
    records = []
    for generation in generations:
        prompt = prompts[generation["prompt_id"]]
        records.append(
            {
                "generation_id": generation["generation_id"],
                "prompt_id": generation["prompt_id"],
                "image_path": generation["image_path"],
                "detector_mode": "stub",
                "detections": _stub_detections_for_prompt(prompt),
            }
        )
    write_jsonl(output_path, records)
    return records


def _validate_box(box, context):
    required = ["x1", "y1", "x2", "y2"]
    missing = [key for key in required if key not in box]
    if missing:
        raise ValueError(f"{context}: box missing keys {missing}")
    values = [float(box[key]) for key in required]
    if not all(0.0 <= value <= 1.0 for value in values):
        raise ValueError(f"{context}: box coordinates must be normalized to [0, 1]")
    if values[0] >= values[2] or values[1] >= values[3]:
        raise ValueError(f"{context}: invalid box ordering; expected x1 < x2 and y1 < y2")


def validate_manual_json_records(records):
    allowed_statuses = TRUSTED_MANUAL_STATUSES | {"unverified"}
    for idx, record in enumerate(records):
        context = f"manual_json record {idx}"
        for key in ["generation_id", "prompt_id", "detections"]:
            if key not in record:
                raise ValueError(f"{context}: missing required key {key}")
        record["detector_mode"] = "manual_json"
        record.setdefault("verification_status", "unverified")
        if record["verification_status"] not in allowed_statuses:
            raise ValueError(f"{context}: invalid verification_status {record['verification_status']}")
        if not isinstance(record["detections"], list):
            raise ValueError(f"{context}: detections must be a list")
        for det_idx, detection in enumerate(record["detections"]):
            det_context = f"{context} detection {det_idx}"
            for key in ["object_id", "name", "box"]:
                if key not in detection:
                    raise ValueError(f"{det_context}: missing required key {key}")
            _validate_box(detection["box"], det_context)
            detection.setdefault("source", "manual_json")
            detection.setdefault("confidence", 1.0)
            if "mask_area" in detection:
                mask_area = float(detection["mask_area"])
                if mask_area < 0.0 or mask_area > 1.0:
                    raise ValueError(f"{det_context}: mask_area must be normalized to [0, 1]")
    return records


def run_manual_json(manual_path, output_path):
    records = read_jsonl(manual_path)
    records = validate_manual_json_records(records)
    write_jsonl(output_path, records)
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", required=True)
    parser.add_argument("--generations", required=True)
    parser.add_argument("--output", default="data/detections/stage0a/detections.jsonl")
    parser.add_argument("--detector-mode", choices=["stub", "manual_json"], default="stub")
    parser.add_argument("--manual-json", default=None)
    args = parser.parse_args()
    if args.detector_mode == "stub":
        records = run_stub(args.prompts, args.generations, args.output)
    else:
        if not args.manual_json:
            raise SystemExit("--manual-json is required with --detector-mode manual_json")
        records = run_manual_json(args.manual_json, args.output)
    print(f"Wrote {len(records)} detection records to {args.output}")


if __name__ == "__main__":
    main()
