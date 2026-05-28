# Gap Review: Numerical-Spatial Control for Diffusion Text-to-Image

This document records a strict reviewer-style assessment of the research gaps summarized in `notes/literature_matrix.md`.

## Verdict

**Verdict: weak promising**

The direction has potential, but only if it is narrowed to a genuinely underexplored research problem. A generic pipeline that combines prompt parsing, layout generation, ControlNet/GLIGEN-style conditioning, and detector/VLM feedback would likely be judged as incremental engineering.

The work should not be framed as a broad system for all numerical and spatial control. It should focus on the parts that are least covered by existing work and can be evaluated rigorously.

## Most Promising Research Directions

### 1. Ratio and Distance Control

This is the strongest gap. Existing work is relatively dense around object counting and simple relative positions such as left/right/above/below. Ratio and distance constraints remain less developed:

- size or area ratio: "A is half the size of B"
- spatial fraction: "one third from the left"
- relative distance: "A is twice as far from B as C"
- equal spacing: "three objects are evenly spaced"
- distance-to-boundary constraints

This direction is more defensible than another count-control paper.

### 2. Composable Numeric-Spatial Constraints

Real prompts often combine constraints:

- object count
- size ratio
- relative position
- distance
- containment or between relations

The research question should be about joint constraint satisfaction, conflict handling, and how performance degrades as constraints are composed. A paper-level contribution requires more than applying several single-constraint modules independently.

### 3. Constraint Graph Guided Diffusion Without Manual Boxes

Many strong layout-to-image methods assume user-provided boxes, masks, or layouts. A more distinctive direction is:

1. parse natural language into a structured numeric-spatial constraint graph;
2. infer soft layout or attention constraints from that graph;
3. guide diffusion-stage generation without requiring manually provided boxes.

This direction is promising only if the constraint graph is more than an LLM-generated JSON wrapper. It must be formalized, evaluated, and shown to improve generation beyond strong baselines.

## Likely Reviewer Criticisms

Reviewers are likely to challenge the project on the following points:

1. **Parser novelty**

   Is the natural-language-to-constraint parser just prompt engineering with an LLM? If so, it is not a strong technical contribution.

2. **Constraint graph value**

   Why is a constraint graph better than directly asking an LLM to produce boxes, masks, or layout coordinates?

3. **Overlap with existing guidance methods**

   Is the diffusion-stage guidance meaningfully different from MAC, GLIGEN, ObjectDiffusion, ControlNet, or existing attention-guidance methods?

4. **Metric leakage**

   If detector/VLM signals are used for guidance and similar detector/VLM signals are used for evaluation, the reported improvements may be circular.

5. **Rejection sampling concern**

   If the method works mainly by generating many images and selecting the best one, it is not demonstrating real controllability.

6. **Ground truth ambiguity**

   Ratio and distance constraints need clear definitions. Reviewers will ask whether "half the size" is measured by bounding-box area, segmentation mask area, perceived object size, or another metric.

7. **Failure attribution**

   In complex prompts, failures may come from parsing, constraint conflict, weak diffusion guidance, base-model limitations, or evaluation errors. The paper must separate these causes.

8. **Generalization**

   Does the method work beyond COCO-style common objects? Does it generalize to unseen categories, unseen number ranges, unseen relation types, and more complex compositions?

9. **Image quality tradeoff**

   If constraint satisfaction improves while image quality or prompt fidelity collapses, the method will not be convincing.

## Required Key Experiments

The project should not be treated as paper-ready without the following experiments.

### Single-Constraint Evaluation

Evaluate each constraint type separately:

- count accuracy
- ratio error
- distance error
- relative-position accuracy

This is necessary to show where the method actually helps.

### Compositional Constraint Evaluation

Evaluate prompts containing multiple simultaneous constraints:

- two constraints
- three constraints
- four or more constraints

Report joint satisfaction rate, not only per-constraint averages.

### Parser Evaluation

Create or annotate a set of prompts with ground-truth constraint graphs.

Report:

- node/object extraction accuracy
- relation extraction accuracy
- numeric value extraction accuracy
- constraint graph precision/recall
- error categories

Without parser evaluation, the method will look like an opaque system.

### Guidance Ablation

Ablate the core components:

- base diffusion model only
- prompt engineering only
- parser only
- parser plus inferred layout
- parser plus diffusion guidance
- full method

If the full method does not clearly outperform these variants, the contribution is weak.

### Metric Separation

Any model used for guidance should be separated from the model used for evaluation.

For example:

- detector/VLM used during guidance should not be the same evaluator reported as the main metric;
- automatic metrics should be validated against human judgments on a sample.

### OOD Generalization

Test on:

- unseen object categories
- unseen number ranges
- unseen ratio values
- unseen distance values
- unseen relation combinations

This is critical if the contribution claims general numeric-spatial understanding rather than dataset-specific tuning.

### Human Evaluation

At least a sampled human evaluation is needed to validate:

- count correctness
- perceived ratio correctness
- perceived distance correctness
- spatial relation correctness
- image quality and prompt fidelity

### Failure Analysis

Failures must be categorized into:

- parsing failure
- impossible or conflicting constraint
- diffusion guidance failure
- base model generation failure
- evaluator failure

## Required Baselines

The following baselines are important for a credible paper.

1. **Base T2I model**

   Stable Diffusion, SDXL, or another clearly specified diffusion model.

2. **Prompt engineering baseline**

   Strong manually designed prompts without structural guidance.

3. **LLM-to-layout or LLM-to-box baseline**

   Ask an LLM to produce boxes/layouts directly, then use a layout-conditioned generator.

4. **GLIGEN or ObjectDiffusion-style box-conditioned baseline**

   Required if the proposed method uses inferred boxes or grounding.

5. **ControlNet or T2I-Adapter-style conditioning baseline**

   Required if the method uses layout, mask, or spatial-map conditioning.

6. **MAC or another training-free layout-guidance baseline**

   Required if the method claims training-free diffusion-stage guidance.

7. **Count-focused baseline**

   At least one or two of CountGen, YOLO-Count, D2D, CountLoop, or similar count-control methods.

8. **Spatial-relation baseline**

   CoMPaSS, SR4G, or another spatial-relation-specific method.

9. **Rejection sampling baseline**

   Generate multiple candidates and select the best with an evaluator. This is necessary to show that the method is better than brute-force selection.

## Risk Conditions

If the following results cannot be achieved, the direction should not continue as a method paper.

1. **No clear gain on ratio or distance**

   If the method cannot significantly improve ratio and distance constraints over SDXL plus prompt engineering, the central gap is not supported.

2. **No gain in joint constraint satisfaction**

   If only individual metrics improve but joint satisfaction does not, the compositional-constraint claim fails.

3. **Weakness against box-conditioned baselines**

   If the method is much worse than GLIGEN/ObjectDiffusion-style methods and cannot justify why no-manual-box control is valuable, the method will look weak.

4. **Parser bottleneck**

   If constraint graph parsing is unreliable, the full system will not be credible.

5. **Improvement mainly from sampling or filtering**

   If the improvement comes mostly from generating many candidates and selecting the best, the method is closer to search than controllable generation.

6. **Automatic metrics not supported by human evaluation**

   If human judgments do not agree with detector/VLM-based metrics, the evidence is not reliable.

7. **Image quality collapse**

   If constraint satisfaction improves while image quality, object fidelity, or prompt fidelity degrades substantially, the result is not convincing.

8. **Only works on cherry-picked prompts**

   If the method fails on a broad benchmark or does not generalize to unseen categories and relation compositions, it is not suitable for a publishable method paper.

## Reviewer-Style Conclusion

**weak promising**

The project is not yet strong as a broad "numerical and spatial control" system. It becomes promising only if narrowed to underexplored constraints, especially ratio and distance, and if it demonstrates reliable compositional numeric-spatial constraint satisfaction without manually provided boxes.

The strongest paper framing is:

> Diffusion text-to-image models still lack reliable control over compositional numeric-spatial constraints, especially ratio and distance relations. We propose a structured constraint graph and diffusion-stage guidance method to improve joint constraint satisfaction without manually provided layouts.

If the method cannot outperform strong baselines on ratio, distance, and joint constraint satisfaction, the project should be reframed as an evaluation/benchmark study or stopped before large implementation effort.

