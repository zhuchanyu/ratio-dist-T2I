# Server Generation Runbook

This runbook is for the next time a GPU server is available.

## Current Local Status

Prepared locally:

- Stage 1 baseline prompts:
  - `data/prompts/stage1/stage1_base_prompts.jsonl`
  - `data/prompts/stage1/sdxl_direct_prompts.jsonl`
  - `data/prompts/stage1/strong_prompt_prompts.jsonl`
  - `data/prompts/stage1/rejection_sampling_candidates_prompts.jsonl`
  - `data/prompts/stage1/manifest.json`
- Stage 0A server qualitative inspection:
  - `reports/stage0a_server_qualitative_scores.tsv`
  - `reports/stage0a_server_qualitative_summary.json`
  - `reports/stage0a_server_qualitative_inspection_report.md`

Formal Stage 1 remains blocked until Stage 0 metric sanity passes with trusted detections. The commands below are for exploratory image generation unless that gate has passed.

## Preflight

Run in the server project root:

```bash
pwd
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NO_CUDA')"
python -c "import diffusers, transformers, accelerate, safetensors, PIL; print('deps_ok')"
test -d /root/autodl-tmp/models/stable-diffusion-xl-base-1.0 && echo "model_ok"
```

## Stage 0A Real Generation Check

Use this only if Stage 0A images need to be regenerated.

```bash
OMP_NUM_THREADS=1 python scripts/stage0a_metric_sanity.py \
  --generation-mode sdxl \
  --detector-mode stub \
  --model-path /root/autodl-tmp/models/stable-diffusion-xl-base-1.0 \
  2>&1 | tee -a EXPERIMENT_LOG.md
```

Expected outputs:

- `data/generated/stage0a/generations.jsonl`
- `data/generated/stage0a/images/*.png`
- `reports/metric_sanity_report.md`

This does not pass Stage 1 readiness because detector mode is `stub`.

## Exploratory Stage 1 Baseline Image Generation

Run only after syncing the latest local code and prompt files to the server.

```bash
OMP_NUM_THREADS=1 python scripts/stage1_exploratory_baselines.py \
  --generation-mode sdxl \
  --model-path /root/autodl-tmp/models/stable-diffusion-xl-base-1.0 \
  --num-prompts 50 \
  --rejection-samples 4 \
  --allow-gate-override \
  2>&1 | tee -a EXPERIMENT_LOG.md
```

Expected outputs:

- `data/generated/stage1/sdxl_direct/generations.jsonl`
- `data/generated/stage1/sdxl_direct/images/*.png`
- `data/generated/stage1/strong_prompt/generations.jsonl`
- `data/generated/stage1/strong_prompt/images/*.png`
- `data/generated/stage1/rejection_sampling_candidates/generations.jsonl`
- `data/generated/stage1/rejection_sampling_candidates/images/*.png`
- `reports/stage1_sdxl_direct_contact_sheet.jpg`
- `reports/stage1_strong_prompt_contact_sheet.jpg`
- `reports/stage1_rejection_sampling_candidates_contact_sheet.jpg`
- `reports/stage1_exploratory_run_summary.md`

## Required Interpretation

If the command uses `--allow-gate-override`, the result is exploratory only.

Do not write:

```text
Stage 1 passed.
```

Write:

```text
Stage 1 exploratory baseline images were generated under gate override.
Formal Stage 1 remains blocked until Stage 0 metric sanity passes with trusted detections.
```

## After Images Are Generated

Inspect the contact sheets and create a qualitative TSV with columns:

```text
generation_id
prompt_id
task_type
image_path
prompt
score_0_1_2
failure_reason
```

Then summarize:

```bash
python scripts/summarize_qualitative_scores.py \
  --scores reports/<qualitative_scores>.tsv \
  --summary reports/<qualitative_summary>.json \
  --report reports/<qualitative_report>.md
```
