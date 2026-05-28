"""Generate Stage 0A metric sanity report."""

import argparse
import json
from pathlib import Path

from ratio_dist.data.schemas import read_jsonl


def build_report(
    prompts_path,
    generations_path,
    detections_path,
    metrics_path,
    summary_path,
    output_path,
):
    prompts = read_jsonl(prompts_path)
    generations = read_jsonl(generations_path)
    detections = read_jsonl(detections_path)
    metrics = read_jsonl(metrics_path)
    summary = json.loads(Path(summary_path).read_text(encoding="utf-8"))
    detector_modes = sorted({d.get("detector_mode", "unknown") for d in detections})
    verification_statuses = sorted({d.get("verification_status", "not_applicable") for d in detections})
    generation_methods = sorted({g.get("method", "unknown") for g in generations})
    stage1_allowed = "NO"
    reasons = []

    if "stub" in detector_modes:
        reasons.append("Detector mode is stub; Stage 1 conclusions require real detector/segmenter or manual_json detections.")
    if "manual_json" in detector_modes:
        trusted_statuses = {"human_verified", "external_detector"}
        untrusted = [status for status in verification_statuses if status not in trusted_statuses]
        if untrusted:
            reasons.append(
                "Manual JSON detections are not all human_verified or external_detector; "
                "format-only manual_json is not sufficient for Stage 1."
            )
    if summary.get("image_level_detection_coverage", 0.0) < 1.0:
        reasons.append("Image-level detection coverage is below 1.0.")
    if summary.get("object_level_detection_coverage", 0.0) < 1.0:
        reasons.append("Object-level detection coverage is below 1.0.")
    if summary.get("size_ratio_count", 0) == 0:
        reasons.append("No valid size-ratio metrics were computed.")
    if summary.get("boundary_count", 0) == 0:
        reasons.append("No valid boundary metrics were computed.")
    if not reasons:
        stage1_allowed = "YES"

    lines = [
        "# Stage 0A Metric Sanity Report",
        "",
        "## Scope",
        "",
        "This report covers Stage 0A only: prompt generation, direct image generation, detector/segmenter interface, geometric metric computation, and metric sanity reporting.",
        "",
        "It does not include attention extraction, attention reliability, rejection sampling, prompt engineering baselines, guidance, distance ratio, equal spacing, LLM parsing, or layout-control baselines.",
        "",
        "## Inputs and Outputs",
        "",
        f"- Prompts: `{prompts_path}`",
        f"- Generations: `{generations_path}`",
        f"- Detections: `{detections_path}`",
        f"- Metrics: `{metrics_path}`",
        f"- Summary: `{summary_path}`",
        "",
        "## Run Summary",
        "",
        f"- Prompt count: {len(prompts)}",
        f"- Generated image count: {len(generations)}",
        f"- Generation count: {summary.get('generation_count')}",
        f"- Detection record count: {summary.get('detection_record_count')}",
        f"- Metric record count: {len(metrics)}",
        f"- Generation methods: {', '.join(generation_methods)}",
        f"- Detector modes: {', '.join(detector_modes)}",
        f"- Verification statuses: {', '.join(verification_statuses)}",
        "",
        "## Metric Summary",
        "",
        f"- Image-level detection coverage: {summary.get('image_level_detection_coverage')}",
        f"- Object-level detection coverage: {summary.get('object_level_detection_coverage')}",
        f"- Missing detection count: {summary.get('missing_detection_count')}",
        f"- Missing required object count: {summary.get('missing_required_object_count')}",
        f"- Detection rate (legacy object-level alias): {summary.get('detection_rate')}",
        f"- Size-ratio samples: {summary.get('size_ratio_count')}",
        f"- Mean SizeRatioErr: {summary.get('size_ratio_err_mean')}",
        f"- SizeRatioSuccess@0.25: {summary.get('size_ratio_success_0_25')}",
        f"- SizeRatioSuccess@0.5: {summary.get('size_ratio_success_0_5')}",
        f"- Boundary samples: {summary.get('boundary_count')}",
        f"- Mean BoundaryErr: {summary.get('boundary_err_mean')}",
        f"- BoundarySuccess@0.08: {summary.get('boundary_success_0_08')}",
        f"- BoundarySuccess@0.12: {summary.get('boundary_success_0_12')}",
        "",
        "## Stage 1 Readiness",
        "",
        f"- Allowed to enter Stage 1 based on this run: **{stage1_allowed}**",
        "",
    ]
    if reasons:
        lines.extend(["Reasons:", ""])
        lines.extend(f"- {reason}" for reason in reasons)
        lines.append("")
    lines.extend(
        [
            "## Notes",
            "",
            "- Stub detections are only for pipeline validation.",
            "- Manual JSON detections must be marked human_verified or external_detector before they can support Stage 1.",
            "- A real detector/segmenter or manually verified detection JSON is required before making research claims.",
            "- Custom metrics are task-specific geometric scores, not authoritative metrics.",
        ]
    )
    text = "\n".join(lines) + "\n"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", default="data/prompts/stage0a_sanity_prompts.jsonl")
    parser.add_argument("--generations", default="data/generated/stage0a/generations.jsonl")
    parser.add_argument("--detections", default="data/detections/stage0a/detections.jsonl")
    parser.add_argument("--metrics", default="data/results/stage0a/metrics.jsonl")
    parser.add_argument("--summary", default="data/results/stage0a/summary.json")
    parser.add_argument("--output", default="reports/metric_sanity_report.md")
    args = parser.parse_args()
    build_report(args.prompts, args.generations, args.detections, args.metrics, args.summary, args.output)
    print(f"Wrote report to {args.output}")


if __name__ == "__main__":
    main()
