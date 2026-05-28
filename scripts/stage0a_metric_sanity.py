"""Run Stage 0A metric sanity pipeline.

This script intentionally does not implement attention extraction, guidance,
rejection sampling, prompt-engineering baselines, or later stages.
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ratio_dist.data.build_prompts import build_prompts
from ratio_dist.data.schemas import write_jsonl
from ratio_dist.evaluation.detect_segment import run_manual_json, run_stub
from ratio_dist.evaluation.geometry_metrics import run_metrics
from ratio_dist.evaluation.make_metric_sanity_report import build_report
from ratio_dist.generation.generate_sdxl import run_generation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/stage0a_metric_sanity.yaml", help="Reserved for run documentation; argparse values are authoritative in Stage 0A.")
    parser.add_argument("--num-prompts", type=int, default=20)
    parser.add_argument("--num-images-per-prompt", type=int, default=1)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--generation-mode", choices=["placeholder", "sdxl"], default="placeholder")
    parser.add_argument("--model-path", default=None)
    parser.add_argument("--detector-mode", choices=["stub", "manual_json"], default="stub")
    parser.add_argument("--manual-detections", default=None)
    parser.add_argument("--prompts-path", default="data/prompts/stage0a_sanity_prompts.jsonl")
    parser.add_argument("--generated-dir", default="data/generated/stage0a")
    parser.add_argument("--detections-path", default="data/detections/stage0a/detections.jsonl")
    parser.add_argument("--metrics-path", default="data/results/stage0a/metrics.jsonl")
    parser.add_argument("--summary-path", default="data/results/stage0a/summary.json")
    parser.add_argument("--report-path", default="reports/metric_sanity_report.md")
    args = parser.parse_args()

    prompts = build_prompts(num_prompts=args.num_prompts, seed=args.seed)
    write_jsonl(args.prompts_path, prompts)
    print(f"[stage0a] Wrote prompts: {args.prompts_path}")

    try:
        run_generation(
            prompts_path=args.prompts_path,
            output_dir=args.generated_dir,
            num_images_per_prompt=args.num_images_per_prompt,
            generation_mode=args.generation_mode,
            model_path=args.model_path,
        )
    except RuntimeError as exc:
        print(f"[stage0a] Generation failed: {exc}", file=sys.stderr)
        raise SystemExit(2)
    generations_path = str(Path(args.generated_dir) / "generations.jsonl")
    print(f"[stage0a] Wrote generations: {generations_path}")

    if args.detector_mode == "stub":
        run_stub(args.prompts_path, generations_path, args.detections_path)
    else:
        if not args.manual_detections:
            print("[stage0a] --manual-detections is required with --detector-mode manual_json", file=sys.stderr)
            raise SystemExit(2)
        run_manual_json(args.manual_detections, args.detections_path)
    print(f"[stage0a] Wrote detections: {args.detections_path}")

    run_metrics(args.prompts_path, generations_path, args.detections_path, args.metrics_path, args.summary_path)
    print(f"[stage0a] Wrote metrics: {args.metrics_path}")

    build_report(
        args.prompts_path,
        generations_path,
        args.detections_path,
        args.metrics_path,
        args.summary_path,
        args.report_path,
    )
    print(f"[stage0a] Wrote report: {args.report_path}")


if __name__ == "__main__":
    main()
