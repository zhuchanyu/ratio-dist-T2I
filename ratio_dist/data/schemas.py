"""Minimal schema helpers for Stage 0A JSONL records."""

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Union


SIZE_RATIO = "SIZE_RATIO"
BOUNDARY_FRACTION = "BOUNDARY_FRACTION"


PathLike = Union[str, Path]


def read_jsonl(path: PathLike) -> List[Dict[str, Any]]:
    records = []  # type: List[Dict[str, Any]]
    with Path(path).open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_jsonl(path: PathLike, records: Iterable[Dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def validate_prompt_record(record: Dict[str, Any]) -> None:
    required = ["prompt_id", "prompt", "task_type", "objects", "constraint_graph"]
    missing = [key for key in required if key not in record]
    if missing:
        raise ValueError(f"Prompt {record.get('prompt_id', '<unknown>')} missing keys: {missing}")
    if record["task_type"] not in {SIZE_RATIO, BOUNDARY_FRACTION}:
        raise ValueError(f"Unsupported task_type for Stage 0A: {record['task_type']}")
    if not record["objects"]:
        raise ValueError(f"Prompt {record['prompt_id']} has no objects")


def validate_generation_record(record: Dict[str, Any]) -> None:
    required = ["generation_id", "prompt_id", "prompt", "image_path", "method"]
    missing = [key for key in required if key not in record]
    if missing:
        raise ValueError(f"Generation missing keys: {missing}")


def validate_detection_record(record: Dict[str, Any]) -> None:
    required = ["generation_id", "prompt_id", "detections"]
    missing = [key for key in required if key not in record]
    if missing:
        raise ValueError(f"Detection missing keys: {missing}")
