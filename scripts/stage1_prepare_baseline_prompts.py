"""Prepare Stage 1 baseline prompt files without generating images."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ratio_dist.baselines.prompt_variants import build_baseline_prompt_sets
from ratio_dist.data.build_prompts import build_prompts
from ratio_dist.data.schemas import write_jsonl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-prompts", type=int, default=50)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--output-dir", default="data/prompts/stage1")
    parser.add_argument("--manifest", default="data/prompts/stage1/manifest.json")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    prompts = build_prompts(num_prompts=args.num_prompts, seed=args.seed)
    base_path = output_dir / "stage1_base_prompts.jsonl"
    write_jsonl(base_path, prompts)

    prompt_sets = build_baseline_prompt_sets(prompts)
    files = {"base": str(base_path)}
    for name, records in prompt_sets.items():
        path = output_dir / f"{name}_prompts.jsonl"
        write_jsonl(path, records)
        files[name] = str(path)

    manifest = {
        "status": "prompt_preparation_only",
        "stage": "stage1_exploratory_baseline_prompt_preparation",
        "formal_stage1_entry": False,
        "reason": "Stage 0 metric sanity must pass before formal Stage 1 conclusions.",
        "num_prompts": args.num_prompts,
        "seed": args.seed,
        "files": files,
        "baselines": ["sdxl_direct", "strong_prompt", "rejection_sampling_candidates"],
    }
    manifest_path = Path(args.manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote Stage 1 prompt manifest: {manifest_path}")


if __name__ == "__main__":
    main()
