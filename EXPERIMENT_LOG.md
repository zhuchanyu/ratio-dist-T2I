# RatioDistGraph Experiment Log

## 2026-05-28 Stage 0A-real Environment Gate

### Objective

Run the RatioDistGraph experiment according to `EXPERIMENT_PLAN.md`, with the current priority on Stage 0A-real: real SDXL image generation and corresponding experiment records.

No stage gate may be skipped. Placeholder or stub outputs must not be used as real experimental results.

### Commands Executed

```powershell
Get-Content -Path EXPERIMENT_PLAN.md -TotalCount 220
```

Result: loaded the root experiment plan and confirmed the current execution plan is limited to Stage 0A/0B/1/2 gates, with Stage 0A requiring real SDXL generation before any downstream real metric sanity conclusion.

```powershell
Get-ChildItem -Force
```

Result: inspected project root. Relevant files/directories present: `EXPERIMENT_PLAN.md`, `configs/`, `ratio_dist/`, `scripts/`, `tests/`, `data/`, `reports/`.

```powershell
Select-String -Path configs\*.yaml,EXPERIMENT_PLAN.md,experiments\*.md -Pattern 'model-path|model_path|stable-diffusion-xl|SDXL|sdxl|diffusers|cuda'
```

Result: found SDXL references in the experiment plan, but no configured local SDXL model path.

```powershell
D:\Users\1\Anaconda3\envs\cv1_py310\python.exe -c "<initial environment check command>"
```

Result: command failed due to a PowerShell quoting issue in the inline Python string. This did not run any experiment and produced no project output.

```powershell
Get-ChildItem -Force models,D:\models,D:\AI\models,D:\AI\aris-test\models -ErrorAction SilentlyContinue | Select-Object Mode,Length,FullName
```

Result: no usable local SDXL model directory was found in the checked candidate paths.

```powershell
Get-Content -Path configs\stage0a_metric_sanity.yaml
```

Result: current config uses `generation_mode: placeholder` and `detector_mode: stub`; this config is suitable only for pipeline validation, not Stage 0A-real.

```powershell
Get-Content -Path .gitignore
```

Result: large output directories and model/cache directories are ignored, including `data/generated/`, `data/detections/`, `data/results/`, `reports/`, `models/`, `checkpoints/`, and HuggingFace/cache directories.

```powershell
D:\Users\1\Anaconda3\envs\cv1_py310\python.exe -c "import sys, importlib.util; print('python_executable=' + sys.executable); print('python_version=' + sys.version.replace(chr(10),' ')); torch_spec=importlib.util.find_spec('torch'); diffusers_spec=importlib.util.find_spec('diffusers'); transformers_spec=importlib.util.find_spec('transformers'); accelerate_spec=importlib.util.find_spec('accelerate'); safetensors_spec=importlib.util.find_spec('safetensors'); print('torch_spec=' + str(torch_spec is not None)); print('diffusers_spec=' + str(diffusers_spec is not None)); print('transformers_spec=' + str(transformers_spec is not None)); print('accelerate_spec=' + str(accelerate_spec is not None)); print('safetensors_spec=' + str(safetensors_spec is not None)); torch=__import__('torch') if torch_spec else None; print('torch_version=' + (str(torch.__version__) if torch else 'MISSING')); print('cuda_available=' + (str(torch.cuda.is_available()) if torch else 'UNKNOWN')); print('cuda_device_count=' + (str(torch.cuda.device_count()) if torch else 'UNKNOWN')); print('cuda_device_name=' + (torch.cuda.get_device_name(0) if torch and torch.cuda.is_available() else 'NONE'))"
```

Result:

```text
python_executable=D:\Users\1\Anaconda3\envs\cv1_py310\python.exe
python_version=3.10.20 | packaged by Anaconda, Inc. | (main, Mar 11 2026, 17:42:35) [MSC v.1942 64 bit (AMD64)]
torch_spec=True
diffusers_spec=False
transformers_spec=False
accelerate_spec=False
safetensors_spec=False
torch_version=2.11.0+cpu
cuda_available=False
cuda_device_count=0
cuda_device_name=NONE
```

```powershell
Get-ChildItem -Force D:\AI\aris-test\models,D:\models,D:\AI\models -ErrorAction SilentlyContinue | Select-Object Mode,Length,FullName
```

Result: no usable local SDXL model path was found in the checked candidate directories.

```powershell
Test-Path EXPERIMENT_LOG.md; if (Test-Path EXPERIMENT_LOG.md) { Get-Content -Path EXPERIMENT_LOG.md -TotalCount 80 }
```

Result: `EXPERIMENT_LOG.md` did not exist before this run.

### Output Files

- Created: `EXPERIMENT_LOG.md`
- Not created: Stage 0A-real generated images
- Not created: Stage 0A-real detections
- Not created: Stage 0A-real metrics
- Not created: Stage 0A-real `metric_sanity_report.md`

Existing stub/manual-json outputs, if present from earlier development, are not counted as Stage 0A-real results.

### Gate Decision

Stage 0A-real is blocked.

Reasons:

1. CUDA is unavailable in the checked Python environment.
2. Installed PyTorch is CPU-only: `torch_version=2.11.0+cpu`.
3. Required SDXL generation packages are missing:
   - `diffusers`: missing
   - `transformers`: missing
   - `accelerate`: missing
   - `safetensors`: missing
4. No local SDXL model path is configured in `configs/stage0a_metric_sanity.yaml`.
5. No usable local SDXL model directory was found in the checked candidate paths.

Because Stage 0A-real cannot produce real SDXL images, the experiment must stop here. Stage 1 must not be entered.

### Next Required Conditions

To continue Stage 0A-real, prepare an environment with:

1. NVIDIA GPU available to PyTorch.
2. CUDA-enabled PyTorch build.
3. Required generation packages installed.
4. A local SDXL model path. The pipeline must not auto-download the model during the experiment.

Example preparation commands, to run in the intended GPU environment:

```powershell
D:\Users\1\Anaconda3\envs\cv1_py310\python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
D:\Users\1\Anaconda3\envs\cv1_py310\python.exe -m pip install diffusers transformers accelerate safetensors pillow
```

Place or point to a local SDXL model directory, for example:

```text
D:\models\stable-diffusion-xl-base-1.0
```

After those conditions are met, the intended Stage 0A-real generation command is:

```powershell
D:\Users\1\Anaconda3\envs\cv1_py310\python.exe scripts\stage0a_metric_sanity.py --generation-mode sdxl --detector-mode stub --model-path <LOCAL_SDXL_MODEL_PATH>
```

This command would only validate real SDXL image generation plus stub detection. It still would not allow Stage 1, because `detector-mode=stub` is never Stage-1-ready.

For a real Stage 0A metric sanity run, SDXL images must then be paired with human-verified or external-detector detections converted to the existing `manual_json` schema:

```powershell
D:\Users\1\Anaconda3\envs\cv1_py310\python.exe scripts\stage0a_metric_sanity.py --generation-mode sdxl --detector-mode manual_json --model-path <LOCAL_SDXL_MODEL_PATH> --manual-detections-path <DETECTIONS_JSONL>
```

Stage 1 may be considered only if the report shows trusted detections and sufficient image-level and object-level detection coverage.

## 2026-05-29 Stage 1 Exploratory Script Preparation

### Objective

Prepare a server-side Stage 1 exploratory baseline image-generation script after the user requested continuing beyond Stage 0A.

This preparation does not mark Stage 1 as gate-compliant. The experiment plan still says Stage 1 results cannot be trusted unless Stage 0 metric sanity passes with trusted detections.

### Files Changed

- `ratio_dist/generation/generate_sdxl.py`
  - Added an optional `method_name` argument so generated records can distinguish `sdxl_direct`, `strong_prompt`, and `rejection_sampling_candidates`.
- `scripts/make_contact_sheet.py`
  - Added a utility to create image-grid contact sheets from generated images.
- `scripts/stage1_exploratory_baselines.py`
  - Added an exploratory baseline runner for:
    - SDXL direct;
    - strong prompt engineering;
    - rejection-sampling candidate generation.
  - The script refuses to run by default if Stage 0 does not allow Stage 1.
  - It can run only with `--allow-gate-override`, and then records that the run is exploratory rather than a formal Stage 1 result.

### Validation Command

```powershell
D:\Users\1\Anaconda3\envs\cv1_py310\python.exe -m py_compile ratio_dist\generation\generate_sdxl.py scripts\make_contact_sheet.py scripts\stage1_exploratory_baselines.py
```

Result: syntax check passed.

### Stage Conclusion

Stage 1 formal entry remains blocked because Stage 0 metric sanity has not passed with trusted detections.

The new script is intended only to generate exploratory baseline images on the GPU server, making it easier to visually inspect whether direct prompting, stronger prompting, and rejection candidate sampling expose a baseline weakness.

## 2026-05-29 Local Code Framework Preparation

### Objective

Build the local CPU-side experiment framework so experiment setup, prompt preparation, qualitative inspection, and report generation can proceed without a GPU.

This does not implement real detector/segmenter, attention extraction, RatioDistGraph guidance, or formal Stage 1 evaluation.

### Files Changed

- `ratio_dist/baselines/__init__.py`
- `ratio_dist/baselines/prompt_variants.py`
  - Added reusable baseline prompt variants:
    - SDXL direct;
    - strong prompt;
    - rejection-sampling candidate prompts.
- `scripts/stage1_prepare_baseline_prompts.py`
  - Added a local CPU script to prepare Stage 1 baseline prompt JSONL files and a manifest without generating images.
- `scripts/make_qualitative_score_template.py`
  - Added a local CPU script to create a TSV template for human qualitative scoring.
- `scripts/summarize_qualitative_scores.py`
  - Added a local CPU script to summarize human qualitative scores into JSON and Markdown.
- `scripts/stage1_exploratory_baselines.py`
  - Updated to reuse the shared baseline prompt-variant module.
- `experiments/local_code_framework.md`
  - Added local workflow documentation.

### Validation Commands

```powershell
D:\Users\1\Anaconda3\envs\cv1_py310\python.exe -m py_compile ratio_dist\baselines\prompt_variants.py scripts\stage1_prepare_baseline_prompts.py scripts\make_qualitative_score_template.py scripts\summarize_qualitative_scores.py scripts\stage1_exploratory_baselines.py scripts\make_contact_sheet.py
```

Result: syntax check passed.

```powershell
D:\Users\1\Anaconda3\envs\cv1_py310\python.exe scripts\stage1_prepare_baseline_prompts.py --num-prompts 10 --seed 17 --output-dir outputs\framework_check\prompts --manifest outputs\framework_check\prompts\manifest.json
```

Result: prompt preparation smoke test passed.

```powershell
D:\Users\1\Anaconda3\envs\cv1_py310\python.exe scripts\make_qualitative_score_template.py --prompts data\prompts\stage0a_sanity_prompts.jsonl --generations data\generated\stage0a\generations.jsonl --output outputs\framework_check\stage0a_qualitative_scores_template.tsv
```

Result: qualitative score template smoke test passed.

```powershell
D:\Users\1\Anaconda3\envs\cv1_py310\python.exe scripts\summarize_qualitative_scores.py --scores outputs\framework_check\stage0a_qualitative_scores_template.tsv --summary outputs\framework_check\qualitative_summary.json --report outputs\framework_check\qualitative_report.md
```

Result: qualitative summary/report smoke test passed with an empty score template.

### Stage Conclusion

Local framework is ready for prompt preparation and human qualitative reporting. Formal Stage 1 remains blocked until Stage 0 metric sanity passes with trusted detections.

## 2026-05-29 Local Prompt and Qualitative Report Completion

### Objective

Continue local work until the next required GPU image-generation step.

### Commands Executed

```powershell
D:\Users\1\Anaconda3\envs\cv1_py310\python.exe scripts\stage1_prepare_baseline_prompts.py --num-prompts 50 --seed 17
```

Result: generated Stage 1 baseline prompt files locally.

```powershell
D:\Users\1\Anaconda3\envs\cv1_py310\python.exe scripts\summarize_qualitative_scores.py --scores reports\stage0a_server_qualitative_scores.tsv --summary reports\stage0a_server_qualitative_summary.json --report reports\stage0a_server_qualitative_inspection_report.md
```

Result: summarized the user's human qualitative inspection of 20 Stage 0A server-generated SDXL images.

### Files Created

- `data/prompts/stage1/stage1_base_prompts.jsonl`
- `data/prompts/stage1/sdxl_direct_prompts.jsonl`
- `data/prompts/stage1/strong_prompt_prompts.jsonl`
- `data/prompts/stage1/rejection_sampling_candidates_prompts.jsonl`
- `data/prompts/stage1/manifest.json`
- `reports/stage0a_server_qualitative_scores.tsv`
- `reports/stage0a_server_qualitative_summary.json`
- `reports/stage0a_server_qualitative_inspection_report.md`
- `experiments/server_generation_runbook.md`

### Qualitative Result

The human qualitative inspection contains 20 scored images:

- total scored: 20
- score 0: 20
- score 1: 0
- score 2: 0
- overall success score >= 1: 0.0
- size-ratio score >= 1: 0.0
- boundary-fraction score >= 1: 0.0

This supports the observation that SDXL direct failed on the sampled Stage 0A prompts under human inspection, but it is still qualitative evidence and does not replace trusted detector/segmenter metric sanity.

### Stage Conclusion

Local preparation is complete until the next GPU image-generation step.

The next GPU step is exploratory Stage 1 baseline image generation using `experiments/server_generation_runbook.md`.

Formal Stage 1 remains blocked until Stage 0 metric sanity passes with trusted detections.
