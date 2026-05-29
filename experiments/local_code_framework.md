# Local Code Framework

This document records what can be done locally without a GPU and without making formal Stage 1 claims.

## Current Boundary

Local CPU-side work can prepare and analyze experiments, but it cannot produce real SDXL images unless a CUDA GPU and local SDXL model are available.

Formal Stage 1 remains blocked until Stage 0 metric sanity passes with trusted detections.

## Local Tasks

### 1. Prepare Stage 1 Baseline Prompts

```bash
python scripts/stage1_prepare_baseline_prompts.py \
  --num-prompts 50 \
  --seed 17
```

Outputs:

- `data/prompts/stage1/stage1_base_prompts.jsonl`
- `data/prompts/stage1/sdxl_direct_prompts.jsonl`
- `data/prompts/stage1/strong_prompt_prompts.jsonl`
- `data/prompts/stage1/rejection_sampling_candidates_prompts.jsonl`
- `data/prompts/stage1/manifest.json`

These files define baseline runs only. They do not generate images.

### 2. Create a Human Qualitative Score Template

```bash
python scripts/make_qualitative_score_template.py \
  --prompts data/prompts/stage0a_sanity_prompts.jsonl \
  --generations data/generated/stage0a/generations.jsonl \
  --output reports/stage0a_qualitative_scores_template.tsv
```

Fill `score_0_1_2` and `failure_reason` manually:

- `0`: does not satisfy the prompt;
- `1`: weakly satisfies the prompt;
- `2`: clearly satisfies the prompt.

### 3. Summarize Human Scores

```bash
python scripts/summarize_qualitative_scores.py \
  --scores reports/stage0a_qualitative_scores_template.tsv \
  --summary reports/stage0a_qualitative_summary.json \
  --report reports/stage0a_qualitative_inspection_report.md
```

This produces a qualitative report only. It does not replace trusted detector/segmenter metrics.

### 4. Server-Side Exploratory Image Generation

After syncing the code to a GPU server:

```bash
OMP_NUM_THREADS=1 python scripts/stage1_exploratory_baselines.py \
  --generation-mode sdxl \
  --model-path /root/autodl-tmp/models/stable-diffusion-xl-base-1.0 \
  --num-prompts 50 \
  --rejection-samples 4 \
  --allow-gate-override \
  2>&1 | tee -a EXPERIMENT_LOG.md
```

This creates exploratory images and contact sheets, but it is not a formal Stage 1 result unless Stage 0 metric sanity passes.
