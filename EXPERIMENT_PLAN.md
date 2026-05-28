# RatioDistGraph MVP Experiment Plan

## 1. Paper Problem Definition

`RatioDistGraph` is defined as:

> Given a natural-language prompt containing explicit ratio or distance constraints, generate an image whose detected or segmented objects satisfy the specified geometric relation, without requiring manually provided boxes or layouts.

The three-stage execution version is strictly limited to two constraint types:

1. **Two-object size ratio**: `A is twice as large as B`.
2. **Boundary fraction**: `A is located one third from the left boundary`.

The current execution plan does not do count-only generation, generic left/right/above/below relation control, distance-ratio tasks, equal-spacing tasks, manually supplied box/layout control, or large-scale training.

Core paper claim:

> Explicit ratio and distance constraints can be represented as structured geometric constraints and used as diffusion-stage guidance, improving measurable constraint satisfaction over prompt-only, LLM-to-box, and layout-guided baselines.

## 2. Method Modules

### M1. Prompt-to-Constraint Parser

The MVP should use restricted templates first, not open-ended natural language. This keeps the initial experiment focused on size-ratio and boundary-fraction guidance instead of parser noise.

Example input:

```text
A red apple is twice as large as a blue cup.
```

Output: a typed constraint graph.

Later versions may use an LLM parser, but the MVP should start with template parser plus oracle graph.

### M2. Constraint Graph Builder

The graph contains:

- object nodes;
- optional anchor nodes;
- relation edges;
- numeric targets;
- tolerance values;
- measurement types.

### M3. Region Estimator During Diffusion

The training-free version estimates object regions from cross-attention maps:

- aggregate object-token attention maps;
- normalize or threshold into soft regions;
- compute soft area;
- compute centroid;
- compute pairwise distance.

If this is unstable, a later lightweight module may calibrate attention to masks, but the first version should not train a large model.

### M4. Size-Ratio and Boundary-Fraction Energy

The method computes geometric constraint energies from soft object regions.

### M5. Diffusion Guidance

The method applies constraint energy during denoising:

- early steps: coarse placement;
- middle steps: size-ratio or boundary-fraction correction;
- late steps: weak or no guidance to preserve image quality.

## 3. Constraint Graph Data Structure

Minimal typed graph example:

```json
{
  "objects": [
    {
      "id": "obj_a",
      "name": "apple",
      "attributes": ["red"],
      "token_span": [1, 3]
    },
    {
      "id": "obj_b",
      "name": "cup",
      "attributes": ["blue"],
      "token_span": [8, 10]
    }
  ],
  "relations": [
    {
      "type": "SIZE_RATIO",
      "subjects": ["obj_a", "obj_b"],
      "target": 2.0,
      "measurement": "soft_area",
      "tolerance": 0.25
    }
  ],
  "canvas": {
    "width": 1.0,
    "height": 1.0
  }
}
```

Supported execution-stage relation types:

```text
SIZE_RATIO(obj_a, obj_b, r)
BOUNDARY_FRACTION(obj_a, boundary, f, axis)
```

For the MVP, `BOUNDARY_FRACTION` should start with:

```text
BOUNDARY_FRACTION(obj, left, f, x-axis)
```

## 4. Size-Ratio and Boundary-Fraction Energy Definitions

Let the soft attention map for object `i` be `M_i(x, y)`.

```text
area_i = sum M_i
cx_i = sum x * M_i / sum M_i
cy_i = sum y * M_i / sum M_i
d(i, j) = sqrt((cx_i - cx_j)^2 + (cy_i - cy_j)^2)
```

### Size Ratio Energy

Target: `area_A / area_B = r`.

```text
E_size = (log((area_A + eps) / (area_B + eps)) - log(r))^2
```

### Boundary Fraction Energy

Target: object centroid at horizontal fraction `f`.

```text
E_boundary = (cx_A - f)^2
```

For vertical constraints, replace `cx_A` with `cy_A`.

### Total Energy

```text
E_total = sum_k w_k * E_k + lambda_sep * E_separation + lambda_quality * E_reg
```

For MVP, avoid complex regularization. First control guidance strength and step range to prevent image collapse.

## 5. Diffusion-Stage Guidance

Using Stable Diffusion or SDXL latent diffusion:

1. Predict noise normally: `eps_theta(z_t, prompt)`.
2. Extract cross-attention maps.
3. Aggregate object-token attention.
4. Compute soft area, centroid, and pairwise distances.
5. Compute `E_total`.
6. Update latent:

```text
z_t <- z_t - eta_t * grad_z E_total
```

Guidance schedule for a 50-step sampler:

```text
steps 0-15: object separation + boundary coarse guidance
steps 15-35: size-ratio or boundary-fraction guidance
steps 35-50: guidance off or very weak
```

Record:

- guidance strength;
- guidance step range;
- runtime overhead;
- failures caused by excessive guidance.

## 6. Dataset Construction

Build `RatioDistBench-MVP`.

Use common, detector-friendly object categories:

```text
apple, orange, cup, bottle, chair, table, car, bicycle, dog, cat,
ball, book, backpack, bowl, vase, clock, laptop, pizza, teddy bear, suitcase
```

Avoid visually ambiguous object pairs when possible. Use different object categories or clear colors to reduce identity confusion.

Execution benchmark target:

- size ratio prompts;
- boundary fraction prompts;
- 50 prompts total for Stage 1;
- multiple generated images per prompt.

Each item stores:

```json
{
  "prompt": "...",
  "constraint_graph": {},
  "task_type": "SIZE_RATIO",
  "target_value": 2.0,
  "objects": ["apple", "cup"],
  "split": "test_in_domain"
}
```

Splits:

- in-domain objects;
- unseen object combinations;
- unseen ratios;
- unseen boundary fractions.

## 7. Benchmark Prompt Templates

### Benchmark Usage Strategy

This project should not use only a custom dataset.

Existing benchmarks should be used for comparability and auxiliary evaluation, including:

- GenEval;
- T2I-CompBench Spatial;
- VISOR/SR2D;
- GeckoNum;
- CLIPScore or ImageReward.

These benchmarks are useful for connecting the project to prior T2I evaluation, checking object existence, coarse spatial relations, numerical prompt following, general prompt-image alignment, and image preference. However, they cannot directly and sufficiently evaluate size ratio, distance ratio, equal spacing, or boundary fraction. In the current three-stage execution plan, only size ratio and boundary fraction are implemented, but the broader RatioDistGraph problem should still state that existing benchmarks do not sufficiently cover continuous geometric constraints.

`RatioDistBench-MVP` is therefore a supplementary benchmark. Its role is to fill the missing continuous-geometric-constraint evaluation for size ratio and boundary fraction in the first execution version, not to replace existing benchmarks.

The first-stage custom dataset should contain only 50 prompts:

- 25 size-ratio prompts;
- 25 boundary-fraction prompts.

If existing benchmarks contain reusable prompts or subtasks, those prompts should be reused or minimally rewritten where possible instead of creating everything from scratch.

The custom benchmark must publicly report:

- prompt templates;
- object categories;
- ratio and fraction values;
- evaluation scripts;
- human validation protocol.

In paper writing, do not claim that the custom benchmark replaces existing benchmarks. It should be described only as a supplement to existing benchmarks for continuous geometric constraints.

### Two-Object Size Ratio

```text
A {color1} {obj1} is {ratio_word} as large as a {color2} {obj2}, on a plain background.
A {obj1} is {ratio_word} the size of a {obj2}, centered in a simple scene.
```

Ratio values:

```text
1/2, 1/3, 2, 3
```

### Boundary Fraction

```text
A {obj1} is located one third from the left boundary of the image.
A {obj1} is positioned two thirds from the left side of the image.
```

Fraction values:

```text
1/4, 1/3, 1/2, 2/3, 3/4
```

## 8. Baselines

Must-run MVP baselines:

1. **SDXL direct prompt**.
2. **Strong prompt engineering**.
3. **LLM prompt rewrite**, without box output.
4. **LLM-to-box + GLIGEN/ObjectDiffusion-style baseline**, if feasible.
5. **MAC or another training-free layout guidance method**, if runnable.
6. **Rejection sampling**, generating `N` candidates and selecting the best by evaluator.
7. **Oracle layout upper bound**, using ideal boxes to estimate ceiling performance.

CountGen, D2D, and YOLO-Count are not central for this MVP because the MVP is not count-only. Mention them as related work; compare only if adding count later.

## 9. Evaluation Protocol

The evaluation must separate existing metrics from task-specific geometric metrics. The task-specific metrics are necessary because existing metrics do not directly evaluate size-ratio or boundary-fraction control.

### 9.0 Constraint Scoring Functions: Source and Role

The project must clearly distinguish **guidance scoring functions** from **evaluation scoring functions**.

The guidance energy used by RatioDistGraph is a custom task-specific geometric energy. It is part of the proposed method, not an existing authoritative metric. Its role is to provide a controllable signal during diffusion denoising for constraints such as size ratio and boundary fraction.

The evaluation metrics such as `SizeRatioErr` and `BoundaryErr` are also task-specific geometric metrics. They are necessary for this project because existing T2I metrics do not directly measure these constraints, but they are not authoritative metrics by themselves. They must be reported together with existing metrics such as GenEval, T2I-CompBench Spatial, VISOR/SR2D, GeckoNum, CLIPScore, or ImageReward.

Both guidance and evaluation scoring functions are based on basic geometric quantities:

- mask or box area;
- object centroid;
- pairwise distance;
- normalized image coordinate.

The components used to obtain or report these quantities must be explicitly sourced:

- detectors and segmenters should cite the existing tools used to obtain boxes or masks;
- CLIPScore and ImageReward should cite the existing metrics or implementations used;
- any VLM, detector, or segmentation component must be treated as an external measurement tool, not as a new metric contribution unless separately validated.

The guidance signal and evaluation signal must be separated to avoid metric leakage. For example, if guidance uses cross-attention maps, evaluation should use an independent detector/segmenter. If any detector or VLM is used during guidance, evaluation must use a different model family plus human validation.

Human validation is required. A sampled set of generated images must be judged by humans to check whether the custom task-specific scoring functions agree with human perception of size ratio, boundary position, and visual plausibility.

Do not call these custom scoring functions authoritative metrics. They are task-specific geometric scoring functions that need sanity checks and human validation.

### 9.1 Existing Metrics

Existing metrics should be reported to connect the work to prior T2I evaluation, but they cannot independently support the main RatioDistGraph claim.

| Metric / Benchmark | What It Can Evaluate | What It Cannot Evaluate |
|---|---|---|
| **GenEval** | Object existence, counting-like object presence, color, position, and attribute binding under compositional prompts | Precise size ratio and boundary fraction |
| **T2I-CompBench Spatial** | Spatial compositionality and coarse spatial relation following | Continuous geometric ratios and boundary fractions |
| **VISOR / SR2D** | Spatial relation correctness for relations such as left/right/above/below or relation-specific spatial prompts | Fine-grained size-ratio or boundary-fraction claims |
| **GeckoNum** | Numerical reasoning in T2I, especially number-related prompt following and counting/quantity cases | Geometry-grounded size-ratio and boundary-fraction control unless extended with custom tasks |
| **CLIPScore / ImageReward** | General text-image alignment, preference, and image-prompt compatibility | Whether the generated image satisfies exact geometric constraints |

These existing metrics should be used as secondary evidence:

- to verify that image quality and general text-image alignment do not collapse;
- to compare with prior work where applicable;
- to show that improvements are not limited to custom metrics.

They should not be presented as sufficient evidence for size-ratio or boundary-fraction success.

### 9.2 Task-Specific Geometric Metrics

The following are custom task-specific metrics. They must be reported as such and validated by metric sanity checks and human validation.

Use an evaluation model independent from guidance. If guidance uses attention maps or an internal model signal, evaluation should use a separate detector/segmenter such as GroundingDINO + SAM or another independent open-vocabulary detection/segmentation pipeline.

**Object Detection Success**

```text
DetRate = percentage of required objects detected
```

Only compute geometric metrics when required objects are detected.

**SizeRatioErr**

Using segmentation mask area or box area:

```text
SizeRatioErr = |log((area_A / area_B) / r_target)|
SizeRatioSuccess@tau = SizeRatioErr < tau
```

Report multiple thresholds, such as:

```text
tau = 0.25, 0.5
```

**BoundaryErr**

```text
BoundaryErr = |cx_A - f_target|
BoundarySuccess@tau = BoundaryErr < tau
```

Example thresholds:

```text
tau = 0.08, 0.12 normalized image width
```

**Joint Success**

For prompts with multiple constraints:

```text
JointSuccess = all required objects detected and all constraints satisfied
```

### 9.3 Human Validation

Human validation is required because the custom geometric metrics depend on detector/segmenter quality and may not match human perception.

Use a sampled subset of generated images and ask annotators to judge:

- whether all required objects are present;
- whether the size ratio is approximately correct;
- whether the boundary-fraction placement is approximately correct;
- whether the image remains visually plausible.

Use human validation to estimate agreement with:

- box-area based metrics;
- mask-area based metrics;
- centroid-distance metrics;
- detector success/failure.

If human judgments disagree strongly with custom metrics, the task-specific metrics must be revised before making paper-level claims.

### 9.4 Metric Sanity Check

Before main experiments, run a metric sanity check.

Check:

- whether the detector finds the intended object categories reliably;
- whether segmentation masks are stable across simple images;
- whether box area and mask area produce similar ratio rankings;
- whether centroid estimates are stable under minor generation variation;
- whether small objects are systematically missed;
- whether object identity swaps affect metric computation;
- whether detector confidence thresholds change success rates substantially.

Compare:

- box-area ratio versus mask-area ratio;
- box-centroid distance versus mask-centroid distance;
- detector/segmenter outputs versus human spot checks.

If metric instability is high, simplify object categories, prompt templates, or evaluation thresholds before running full experiments.

### 9.5 Metric Leakage Control

Guidance and evaluation signals must be separated.

Rules:

- If guidance uses cross-attention maps, evaluation must use an independent detector/segmenter.
- If a detector or VLM is used in any guidance variant, the main reported evaluation must use a different model family plus human validation.
- Rejection sampling must be reported separately from true guidance.
- Do not use the same model both to optimize the image and to claim success.

This separation is necessary to avoid metric leakage.

## 10. Ablation Study

Must-run ablations:

1. **No guidance**: base SDXL.
2. **Prompt rewrite only**.
3. **Oracle graph vs automatic parser**.
4. **Ratio energy only**.
5. **Distance energy only**.
6. **No step scheduling**.
7. **Early-only / middle-only / late-only guidance**.
8. **Different guidance strengths**.
9. **Attention area vs detector area for analysis**.
10. **Oracle layout upper bound**.

Nice-to-have:

- soft mask from attention versus cross-attention centroid only;
- different base models;
- object category OOD;
- unseen ratio values.

## 11. Failure Case Taxonomy

1. **Parser failure**: wrong object, wrong ratio, wrong relation.
2. **Object missing**: one or more required objects are not generated.
3. **Object identity swap**: objects or attributes are confused.
4. **Region estimation failure**: attention map does not correspond to object region.
5. **Ratio failure**: objects detected but size ratio is wrong.
6. **Distance failure**: objects detected but centroids do not satisfy distance relation.
7. **Boundary failure**: object appears, but location fraction is wrong.
8. **Constraint conflict**: prompt constraints cannot be jointly satisfied.
9. **Guidance overdrive**: geometry improves but image becomes distorted.
10. **Evaluator failure**: detector/segmenter misses or mis-segments correct objects.
11. **Sampling variance**: some seeds succeed while others fail.
12. **Quality-fidelity tradeoff**: image quality or object realism drops.

## 12. Three-Stage Execution Plan

The first execution version is limited to:

1. **Boundary fraction**.
2. **Two-object size ratio**.

Do not add new tasks in this execution version.

### Stage 0: Metric and Attention Sanity Check

Goal:

- verify whether detector/segmenter metrics are reliable enough for boundary fraction and size ratio evaluation;
- verify whether cross-attention centroid and cross-attention area correlate with real box/mask centroid and area;
- decide whether attention-based guidance is viable before running baselines or implementing guidance.

Runs:

- create a small sanity set using only boundary fraction and two-object size ratio prompts;
- generate images with SDXL direct prompt;
- run an independent detector/segmenter to obtain boxes and masks;
- compare box area, mask area, box centroid, and mask centroid;
- extract cross-attention maps for object tokens;
- compare attention centroid with box/mask centroid;
- compare attention area with box/mask area;
- manually inspect a sampled subset.

Outputs:

- `metric_sanity_report.md`
- `attention_reliability_report.md`

Decision gates:

- If detector/segmenter metrics are unstable, do not enter Stage 1. Fix object categories, prompt templates, detector thresholds, or metric definitions first.
- If cross-attention centroid is not correlated with box/mask centroid, do not use attention-based boundary-fraction guidance.
- If cross-attention area is not correlated with box/mask area, do not use attention-based size-ratio guidance.
- If attention reliability is insufficient, switch to a benchmark/evaluation route or consider a lightweight attention-to-mask calibration module before method development.

### Stage 1: Baseline Gap Verification

Goal:

- use only 50 prompts to verify that boundary fraction and size ratio are real baseline weaknesses;
- compare only the minimum baseline set before implementing RatioDistGraph guidance.

Prompt scope:

- boundary fraction prompts;
- two-object size ratio prompts.

Baselines:

- SDXL direct;
- strong prompt engineering;
- rejection sampling.

Runs:

- 50 prompts total;
- generate multiple samples per prompt for each baseline;
- evaluate detection rate, `BoundaryErr`, `BoundarySuccess`, `SizeRatioErr`, and `SizeRatioSuccess`;
- include human spot-checks for a sampled subset.

Output:

- `baseline_gap_report.md`

Decision gates:

- If boundary fraction and size ratio are not clear weaknesses for the baselines, do not enter Stage 2.
- If strong prompt engineering or rejection sampling already solves the tasks well, stop method development and reframe the work.
- If metric sanity from Stage 0 is not passed, Stage 1 results cannot be trusted and should not be used to justify Stage 2.

### Stage 2: RatioDistGraph Guidance Pilot

Goal:

- implement RatioDistGraph guidance only after Stage 0 and Stage 1 pass;
- implement only boundary fraction guidance and size ratio guidance.

Allowed guidance:

- boundary fraction guidance based on object centroid;
- size ratio guidance based on object area;
- training-free guidance first;
- lightweight calibration module only if Stage 0 shows attention is insufficient but detector/segmenter metrics are reliable.

Runs:

- oracle graph plus boundary-fraction guidance;
- oracle graph plus size-ratio guidance;
- template parser plus guidance only after oracle graph succeeds;
- guidance strength sweep;
- guidance step-range sweep;
- compare against Stage 1 baselines.

Output:

- `guidance_pilot_report.md`

Decision gates:

- Enter Stage 2 only if metric sanity passes and baseline gap is clear.
- If attention reliability is insufficient, do not run attention-based size-ratio guidance. Either switch to benchmark/evaluation route or add a lightweight calibration module.
- Continue only if guidance improves `BoundaryErr` or `SizeRatioErr` over Stage 1 baselines without lowering detection rate or causing visible image-quality collapse.
- If improvements mainly come from rejection sampling or evaluator selection, the method-paper route is weak.

## 13. Minimal Runnable Version

The first runnable version should implement only:

1. **Boundary fraction**.
2. **Two-object size ratio**.

Initial restrictions:

- template parser only;
- no LLM parser;
- oracle graph first;
- SDXL direct, strong prompt engineering, and rejection sampling baselines only;
- no large-scale training;
- no distance-ratio task;
- no equal-spacing task;
- 50 prompts total;
- generated images with multiple samples per prompt;
- evaluate only detection rate, `BoundaryErr`, `BoundarySuccess`, `SizeRatioErr`, and `SizeRatioSuccess`;
- create `metric_sanity_report.md`, `attention_reliability_report.md`, `baseline_gap_report.md`, and `guidance_pilot_report.md` as the execution outputs.

Minimum success standard:

- metric sanity passes before baseline conclusions are trusted;
- boundary fraction and size ratio are clear weaknesses for SDXL direct, strong prompt engineering, and rejection sampling;
- attention reliability is sufficient for the specific guidance signal being used, or a lightweight calibration route is justified;
- boundary fraction error or size-ratio error improves over baselines;
- required-object detection rate does not significantly drop;
- sample images do not show severe distortion.

If these conditions fail, do not expand the project. Reframe as a benchmark/evaluation study or stop method development until the failed stage is fixed.
