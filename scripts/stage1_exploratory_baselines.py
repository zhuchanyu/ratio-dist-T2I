"""Generate Stage 1 baseline images without claiming gate-compliant results.

This script is intentionally conservative:
- By default, it refuses to run when Stage 0 has not allowed Stage 1.
- With --allow-gate-override, it runs an exploratory baseline image batch and
  records that the run is not a formal Stage 1 result.
- It does not implement RatioDistGraph guidance.
- It does not implement real detector/segmenter evaluation.
"""

import argparse
import datetime as _dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ratio_dist.baselines.prompt_variants import build_baseline_prompt_sets
from ratio_dist.data.build_prompts import build_prompts
from ratio_dist.data.schemas import write_jsonl
from ratio_dist.generation.generate_sdxl import run_generation
from scripts.make_contact_sheet import make_contact_sheet


def _stage1_allowed(report_path: Path) -> bool:
    if not report_path.exists():
        return False
    text = report_path.read_text(encoding="utf-8", errors="ignore")
    return "Allowed to enter Stage 1 based on this run: **YES**" in text


def _write_report(output_path, *, stage0_report, baselines, gate_allowed, override, num_prompts, samples):
    lines = [
        "# Stage 1 Exploratory Baseline Run",
        "",
        "## Status",
        "",
    ]
    if gate_allowed:
        lines.append("- Stage 0 report allowed Stage 1: YES")
    else:
        lines.append("- Stage 0 report allowed Stage 1: NO")
    lines.append(f"- Gate override used: {'YES' if override else 'NO'}")
    lines.append("")
    lines.append(
        "This run only generates baseline images. It does not provide formal Stage 1 conclusions "
        "unless Stage 0 metric sanity has passed with trusted detections."
    )
    lines.extend(
        [
            "",
            "## Inputs",
            "",
            f"- Stage 0 report checked: `{stage0_report}`",
            f"- Prompt count: {num_prompts}",
            f"- Rejection candidate samples per prompt: {samples}",
            "",
            "## Outputs",
            "",
        ]
    )
    for baseline in baselines:
        lines.extend(
            [
                f"### {baseline['name']}",
                "",
                f"- Prompt file: `{baseline['prompts']}`",
                f"- Generations: `{baseline['generations']}`",
                f"- Images: `{baseline['images']}`",
                f"- Contact sheet: `{baseline['contact_sheet']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Next Required Work",
            "",
            "- Inspect contact sheets and record qualitative failures.",
            "- Do not use stub detections for formal Stage 1 conclusions.",
            "- Add trusted manual_json or an external detector/segmenter before metric claims.",
            "- If Stage 0 metric sanity remains unpassed, report this as exploratory evidence only.",
            "",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _append_log(log_path, report_path, gate_allowed, override):
    timestamp = _dt.datetime.now().isoformat(timespec="seconds")
    text = [
        "",
        f"## {timestamp} Stage 1 exploratory baseline image generation",
        "",
        f"- Stage 0 gate allowed Stage 1: {'YES' if gate_allowed else 'NO'}",
        f"- Gate override used: {'YES' if override else 'NO'}",
        f"- Report: `{report_path}`",
        "- This run is image generation only and is not a formal Stage 1 metric conclusion unless Stage 0 metric sanity passes.",
        "",
    ]
    with Path(log_path).open("a", encoding="utf-8") as f:
        f.write("\n".join(text))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage0-report", default="reports/metric_sanity_report.md")
    parser.add_argument("--num-prompts", type=int, default=50)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--generation-mode", choices=["placeholder", "sdxl"], default="sdxl")
    parser.add_argument("--model-path", default=None)
    parser.add_argument("--rejection-samples", type=int, default=4)
    parser.add_argument("--allow-gate-override", action="store_true")
    parser.add_argument("--prompt-dir", default="data/prompts/stage1")
    parser.add_argument("--generated-dir", default="data/generated/stage1")
    parser.add_argument("--report", default="reports/stage1_exploratory_run_summary.md")
    parser.add_argument("--log", default="EXPERIMENT_LOG.md")
    args = parser.parse_args()

    stage0_report = Path(args.stage0_report)
    gate_allowed = _stage1_allowed(stage0_report)
    if not gate_allowed and not args.allow_gate_override:
        raise SystemExit(
            "Stage 0 report does not allow Stage 1. "
            "Use --allow-gate-override only for exploratory image generation, not formal Stage 1 conclusions."
        )

    prompts = build_prompts(num_prompts=args.num_prompts, seed=args.seed)
    prompt_dir = Path(args.prompt_dir)
    generated_dir = Path(args.generated_dir)
    prompt_dir.mkdir(parents=True, exist_ok=True)

    base_prompts = prompt_dir / "stage1_base_prompts.jsonl"
    direct_prompts = prompt_dir / "sdxl_direct_prompts.jsonl"
    strong_prompts = prompt_dir / "strong_prompt_prompts.jsonl"
    rejection_prompts = prompt_dir / "rejection_sampling_prompts.jsonl"

    write_jsonl(base_prompts, prompts)
    prompt_sets = build_baseline_prompt_sets(prompts)
    write_jsonl(direct_prompts, prompt_sets["sdxl_direct"])
    write_jsonl(strong_prompts, prompt_sets["strong_prompt"])
    write_jsonl(rejection_prompts, prompt_sets["rejection_sampling_candidates"])

    baseline_specs = [
        ("sdxl_direct", direct_prompts, 1),
        ("strong_prompt", strong_prompts, 1),
        ("rejection_sampling_candidates", rejection_prompts, args.rejection_samples),
    ]

    baselines = []
    for name, prompt_path, samples in baseline_specs:
        out_dir = generated_dir / name
        run_generation(
            prompts_path=prompt_path,
            output_dir=out_dir,
            num_images_per_prompt=samples,
            generation_mode=args.generation_mode,
            model_path=args.model_path,
            method_name=name if args.generation_mode == "sdxl" else f"{name}_placeholder",
        )
        contact_sheet = Path("reports") / f"stage1_{name}_contact_sheet.jpg"
        make_contact_sheet(out_dir / "images", contact_sheet)
        baselines.append(
            {
                "name": name,
                "prompts": str(prompt_path),
                "generations": str(out_dir / "generations.jsonl"),
                "images": str(out_dir / "images"),
                "contact_sheet": str(contact_sheet),
            }
        )

    report_path = Path(args.report)
    _write_report(
        report_path,
        stage0_report=stage0_report,
        baselines=baselines,
        gate_allowed=gate_allowed,
        override=args.allow_gate_override,
        num_prompts=args.num_prompts,
        samples=args.rejection_samples,
    )
    _append_log(args.log, report_path, gate_allowed, args.allow_gate_override)
    print(f"Wrote Stage 1 exploratory report: {report_path}")


if __name__ == "__main__":
    main()
