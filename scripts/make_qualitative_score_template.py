"""Create a TSV template for human qualitative inspection."""

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ratio_dist.data.schemas import read_jsonl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", default="data/prompts/stage0a_sanity_prompts.jsonl")
    parser.add_argument("--generations", default="data/generated/stage0a/generations.jsonl")
    parser.add_argument("--output", default="reports/stage0a_qualitative_scores_template.tsv")
    args = parser.parse_args()

    prompts = {record["prompt_id"]: record for record in read_jsonl(args.prompts)}
    generations = read_jsonl(args.generations)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "generation_id",
                "prompt_id",
                "task_type",
                "image_path",
                "prompt",
                "score_0_1_2",
                "failure_reason",
            ],
            delimiter="\t",
        )
        writer.writeheader()
        for generation in generations:
            prompt = prompts[generation["prompt_id"]]
            writer.writerow(
                {
                    "generation_id": generation["generation_id"],
                    "prompt_id": generation["prompt_id"],
                    "task_type": generation["task_type"],
                    "image_path": generation["image_path"],
                    "prompt": prompt["prompt"],
                    "score_0_1_2": "",
                    "failure_reason": "",
                }
            )
    print(f"Wrote qualitative score template: {output}")


if __name__ == "__main__":
    main()
