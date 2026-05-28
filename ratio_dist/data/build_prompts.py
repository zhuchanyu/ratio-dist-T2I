"""Build Stage 0A sanity prompts for size ratio and boundary fraction."""

import argparse
import random
from pathlib import Path

from ratio_dist.data.schemas import BOUNDARY_FRACTION, SIZE_RATIO, write_jsonl


OBJECTS = [
    "apple",
    "orange",
    "cup",
    "bottle",
    "chair",
    "ball",
    "book",
    "bowl",
    "vase",
    "clock",
]

COLORS = ["red", "blue", "green", "yellow", "white", "black"]
RATIOS = [(0.5, "half"), (2.0, "twice"), (3.0, "three times")]
FRACTIONS = [(0.25, "one quarter"), (1.0 / 3.0, "one third"), (0.5, "one half"), (2.0 / 3.0, "two thirds")]


def _size_ratio_prompt(idx: int, rng: random.Random) -> dict:
    obj_a, obj_b = rng.sample(OBJECTS, 2)
    color_a, color_b = rng.sample(COLORS, 2)
    ratio, ratio_word = rng.choice(RATIOS)
    prompt = f"A {color_a} {obj_a} is {ratio_word} as large as a {color_b} {obj_b}, on a plain background."
    prompt_id = f"size_ratio_{idx:03d}"
    return {
        "prompt_id": prompt_id,
        "prompt": prompt,
        "task_type": SIZE_RATIO,
        "objects": [
            {"id": "obj_a", "name": obj_a, "attributes": [color_a]},
            {"id": "obj_b", "name": obj_b, "attributes": [color_b]},
        ],
        "constraint_graph": {
            "objects": ["obj_a", "obj_b"],
            "relations": [
                {
                    "type": SIZE_RATIO,
                    "subjects": ["obj_a", "obj_b"],
                    "target": ratio,
                    "measurement": "box_or_mask_area",
                    "tolerance": 0.5,
                }
            ],
            "canvas": {"width": 1.0, "height": 1.0},
        },
    }


def _boundary_prompt(idx: int, rng: random.Random) -> dict:
    obj = rng.choice(OBJECTS)
    color = rng.choice(COLORS)
    fraction, fraction_word = rng.choice(FRACTIONS)
    prompt = f"A {color} {obj} is located {fraction_word} from the left boundary of the image."
    prompt_id = f"boundary_fraction_{idx:03d}"
    return {
        "prompt_id": prompt_id,
        "prompt": prompt,
        "task_type": BOUNDARY_FRACTION,
        "objects": [{"id": "obj_a", "name": obj, "attributes": [color]}],
        "constraint_graph": {
            "objects": ["obj_a"],
            "relations": [
                {
                    "type": BOUNDARY_FRACTION,
                    "subjects": ["obj_a"],
                    "boundary": "left",
                    "axis": "x",
                    "target": fraction,
                    "measurement": "box_or_mask_centroid",
                    "tolerance": 0.12,
                }
            ],
            "canvas": {"width": 1.0, "height": 1.0},
        },
    }


def build_prompts(num_prompts=20, seed=7):
    if num_prompts < 2:
        raise ValueError("num_prompts must be at least 2")
    if num_prompts > 50:
        raise ValueError("Stage 0A is limited to at most 50 prompts")
    rng = random.Random(seed)
    n_size = num_prompts // 2
    n_boundary = num_prompts - n_size
    records = []
    records.extend(_size_ratio_prompt(i, rng) for i in range(n_size))
    records.extend(_boundary_prompt(i, rng) for i in range(n_boundary))
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/prompts/stage0a_sanity_prompts.jsonl")
    parser.add_argument("--num-prompts", type=int, default=20)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    records = build_prompts(num_prompts=args.num_prompts, seed=args.seed)
    write_jsonl(Path(args.output), records)
    print(f"Wrote {len(records)} prompts to {args.output}")


if __name__ == "__main__":
    main()
