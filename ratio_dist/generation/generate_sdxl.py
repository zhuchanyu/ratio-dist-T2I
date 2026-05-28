"""Stage 0A image generation entrypoint.

Default mode is placeholder so the local pipeline can run without downloading SDXL.
Use --generation-mode sdxl only when a local model and GPU are available.
"""

import argparse
import sys
from pathlib import Path

from ratio_dist.data.schemas import read_jsonl, validate_prompt_record, write_jsonl


def _write_placeholder_ppm(path: Path, width: int = 256, height: int = 256) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="ascii") as f:
        f.write(f"P3\n{width} {height}\n255\n")
        for y in range(height):
            for x in range(width):
                r = int(255 * x / max(1, width - 1))
                g = int(255 * y / max(1, height - 1))
                b = 180
                f.write(f"{r} {g} {b} ")
            f.write("\n")


def generate_placeholder(prompts, output_dir, num_images_per_prompt):
    records = []
    image_dir = output_dir / "images"
    for prompt in prompts:
        validate_prompt_record(prompt)
        for sample_idx in range(num_images_per_prompt):
            generation_id = f"{prompt['prompt_id']}_sample_{sample_idx:02d}"
            image_path = image_dir / f"{generation_id}.ppm"
            _write_placeholder_ppm(image_path)
            records.append(
                {
                    "generation_id": generation_id,
                    "prompt_id": prompt["prompt_id"],
                    "prompt": prompt["prompt"],
                    "task_type": prompt["task_type"],
                    "method": "sdxl_direct_placeholder",
                    "image_path": str(image_path),
                    "sample_idx": sample_idx,
                    "status": "placeholder_image",
                }
            )
    return records


def generate_sdxl_no_download(prompts, output_dir, num_images_per_prompt, model_path=None):
    try:
        import torch  # type: ignore
        from diffusers import StableDiffusionXLPipeline  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "SDXL generation requested, but required packages are unavailable. "
            "Install torch and diffusers, or rerun with --generation-mode placeholder. "
            f"Original error: {exc}"
        ) from exc

    if not torch.cuda.is_available():
        raise RuntimeError("SDXL generation requested, but no CUDA GPU is available. Rerun with --generation-mode placeholder.")
    if not model_path:
        raise RuntimeError(
            "SDXL generation requested, but --model-path was not provided. "
            "This script will not auto-download SDXL. Provide a local model path or use --generation-mode placeholder."
        )
    path = Path(model_path)
    if not path.exists():
        raise RuntimeError(f"Local model path does not exist: {model_path}. This script will not auto-download models.")

    pipe = StableDiffusionXLPipeline.from_pretrained(str(path), local_files_only=True)
    pipe = pipe.to("cuda")
    records = []
    image_dir = output_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    for prompt in prompts:
        validate_prompt_record(prompt)
        for sample_idx in range(num_images_per_prompt):
            generation_id = f"{prompt['prompt_id']}_sample_{sample_idx:02d}"
            image = pipe(prompt["prompt"], num_inference_steps=30).images[0]
            image_path = image_dir / f"{generation_id}.png"
            image.save(image_path)
            records.append(
                {
                    "generation_id": generation_id,
                    "prompt_id": prompt["prompt_id"],
                    "prompt": prompt["prompt"],
                    "task_type": prompt["task_type"],
                    "method": "sdxl_direct",
                    "image_path": str(image_path),
                    "sample_idx": sample_idx,
                    "status": "generated",
                }
            )
    return records


def run_generation(
    prompts_path,
    output_dir,
    num_images_per_prompt=1,
    generation_mode="placeholder",
    model_path=None,
):
    prompts = read_jsonl(prompts_path)
    output_dir = Path(output_dir)
    if generation_mode == "placeholder":
        records = generate_placeholder(prompts, output_dir, num_images_per_prompt)
    elif generation_mode == "sdxl":
        records = generate_sdxl_no_download(prompts, output_dir, num_images_per_prompt, model_path)
    else:
        raise ValueError(f"Unsupported generation_mode: {generation_mode}")
    write_jsonl(output_dir / "generations.jsonl", records)
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", required=True)
    parser.add_argument("--output-dir", default="data/generated/stage0a")
    parser.add_argument("--num-images-per-prompt", type=int, default=1)
    parser.add_argument("--generation-mode", choices=["placeholder", "sdxl"], default="placeholder")
    parser.add_argument("--model-path", default=None)
    args = parser.parse_args()
    try:
        records = run_generation(
            args.prompts,
            args.output_dir,
            args.num_images_per_prompt,
            args.generation_mode,
            args.model_path,
        )
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
    print(f"Wrote {len(records)} generation records to {Path(args.output_dir) / 'generations.jsonl'}")


if __name__ == "__main__":
    main()
