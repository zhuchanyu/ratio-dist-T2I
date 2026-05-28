# Idea Candidates: Numeric-Spatial Control for Diffusion Text-to-Image

This document records three paper-level candidate research directions generated from `notes/literature_matrix.md` and `notes/gap_review.md`.

The retained scope is intentionally narrow:

1. ratio and distance control;
2. composable numeric-spatial constraints;
3. constraint graph guided diffusion without manually provided boxes.

It deliberately avoids:

- generic large systems;
- pure object counting;
- ordinary left/right/above/below spatial relation control;
- methods that require manually provided boxes/layouts as the main setting;
- simple LLM-to-JSON plus ControlNet engineering pipelines.

## Candidate 1: RatioDistGraph

### Paper Title

**RatioDistGraph: Constraint-Graph Guided Diffusion for Ratio and Distance Control in Text-to-Image Generation**

### Problem Statement

Current diffusion text-to-image models have relatively dense recent work around object counting and simple directional relations. However, they remain weak on ratio and distance relations, such as:

- "the cup is half the size of the bottle";
- "three objects are evenly spaced";
- "the cat is one third from the left boundary";
- "A is twice as far from B as from C".

The problem is not merely generating a visually plausible image. The problem is generating an image that satisfies measurable geometric constraints expressed in natural language.

### Difference from CountGen, CoMPaSS, MAC, ObjectDiffusion, D2D, and CountLoop

- **CountGen / YOLO-Count / D2D / CountLoop** mainly target object counting and do not systematically handle ratio and distance.
- **CoMPaSS** improves spatial relation understanding, but focuses more on ordinary spatial relations rather than continuous geometric constraints.
- **MAC** requires explicit layout or box constraints and focuses on layout-to-image generation, not natural-language ratio/distance parsing.
- **ObjectDiffusion** is box-conditioned and requires grounding inputs. It does not solve natural-language ratio/distance control.

### Core Method

Build a `numeric-spatial constraint graph`:

- nodes: objects, image boundaries, reference regions;
- edges: size-ratio, area-ratio, relative-distance, boundary-distance, equal-spacing, between;
- values: ratios, distances, normalized coordinates, tolerance intervals.

The method should not directly generate fixed boxes. Instead, it should construct a soft spatial energy from the graph and guide diffusion denoising:

- early denoising: coarse object placement;
- middle denoising: ratio and distance correction;
- late denoising: weak guidance to preserve image quality.

The key technical component is a differentiable or approximately differentiable constraint energy over object attention, masks, centroids, or inferred object regions.

### Why This Is Not Prompt Engineering

The contribution is not better wording. The contribution is turning ratio and distance language into explicit measurable constraints and optimizing those constraints during diffusion generation.

Prompt engineering must be included as a baseline and should be expected to fail on continuous geometric constraints.

### Why This Is Not Simple Engineering Composition

This is not "LLM outputs JSON, then ControlNet generates an image." The proposal requires:

- a formal constraint graph;
- explicit ratio/distance energy;
- diffusion-stage guidance;
- ratio/distance metrics;
- oracle-graph versus automatic-graph analysis.

### Training Requirement

Prefer **training-free** as the first route.

Use SDXL or Stable Diffusion as the base generator. The parser may start with rules or LLM assistance, but it must be evaluated separately.

If training-free guidance is unstable, train a lightweight calibration module that maps attention or masks to object regions. Avoid full T2I model training as the first step.

### Required Data

- A synthetic prompt benchmark for ratio, distance, equal spacing, and boundary-position constraints.
- A small manually verified set of ground-truth constraint graphs.
- Generated image evaluation using detector/segmenter outputs, with guidance and evaluation models separated.
- Optional reuse of GeckoNum, LayoutBench, or T2I-CompBench subsets, but a new ratio/distance subset is necessary.

### Required Baselines

- SDXL direct prompt.
- Strong prompt engineering.
- LLM-to-box plus GLIGEN/ObjectDiffusion.
- MAC or another training-free layout guidance method.
- ControlNet or layout-conditioning baseline.
- Rejection sampling.
- CountGen/YOLO-Count/D2D only as secondary references for count-related subcases.

### Required Ablations

- No constraint graph.
- Prompt rewrite only.
- Discrete layout only, without continuous ratio/distance energy.
- Ratio-only guidance.
- Distance-only guidance.
- Early-step guidance versus all-step guidance.
- Different tolerance margins.
- Separate guidance model and evaluation model.
- Oracle graph versus automatic graph.

### Maximum Risk

The largest risk is that object attention or inferred masks may not correspond reliably to real object regions. If the region estimate is unstable, the ratio/distance energy will be unstable.

Another major risk is mismatch between detector-based metrics and human perception of size or distance.

### Potential Venue Level If Successful

If the method significantly improves ratio, distance, and combined numeric-spatial constraints over SDXL, MAC, LLM-to-box, and ObjectDiffusion-style baselines, it could be a main-conference submission to CVPR, ICCV, ECCV, NeurIPS, or ICLR depending on execution quality.

### Fallback If Experiments Fail

Downgrade to a workshop or evaluation paper:

**RatioDistBench: A Benchmark for Ratio and Distance Control in Diffusion Text-to-Image Generation**

This fallback would focus on showing that current diffusion and layout-control methods fail on ratio, distance, equal-spacing, and boundary-fraction constraints.

## Candidate 2: CompCon-T2I

### Paper Title

**CompCon-T2I: Compositional Numeric-Spatial Constraint Satisfaction for Diffusion Text-to-Image Models**

### Problem Statement

Existing methods usually handle one kind of constraint at a time: object count, box grounding, or simple spatial relation. Real prompts often combine multiple constraints:

- "three cups are evenly spaced";
- "the left cup is half the size of the right cup";
- "the middle cup is between the other two";
- "the distance from A to B is twice the distance from A to C".

The central problem is multi-constraint joint satisfaction, not improvement on isolated metrics.

### Difference from CountGen, CoMPaSS, MAC, ObjectDiffusion, D2D, and CountLoop

- **CountGen / D2D / YOLO-Count** optimize count but do not handle multi-relation compositions.
- **CoMPaSS** improves spatial relations but is not a numeric-spatial compositional constraint framework.
- **MAC / ObjectDiffusion** use layout or box conditions and mainly evaluate layout fidelity rather than constraint composition.
- **CountLoop** uses VLM feedback loops, but its mechanism is more black-box and less focused on interpretable constraint satisfaction.

### Core Method

Define a compositional constraint program:

- object set;
- constraint set;
- constraint type;
- constraint value;
- constraint tolerance;
- satisfaction score.

Constraint types include:

- count;
- size ratio;
- distance ratio;
- relative position;
- between;
- equal spacing.

The method uses constraint scheduling:

1. object existence/count;
2. coarse position;
3. ratio and distance;
4. final image-quality preservation.

It also includes a conflict detector for impossible or mutually inconsistent prompts.

### Why This Is Not Prompt Engineering

The focus is not wording. The contribution is measuring and optimizing joint constraint satisfaction and analyzing how performance degrades as constraints are composed.

### Why This Is Not Simple Engineering Composition

The method should not simply combine a count module, a layout module, and a detector. It must define:

- a unified compositional objective;
- a constraint scheduling strategy;
- conflict handling;
- joint satisfaction metrics.

### Training Requirement

Start with a training-free method.

If needed, train a lightweight constraint scheduler or relation scorer. Avoid training a full T2I model as the main contribution.

### Required Data

- A compositional numeric-spatial benchmark.
- Prompts grouped by number of constraints: 1, 2, 3, and 4 or more.
- Oracle constraint graphs.
- Labels for satisfiable versus conflicting prompts.
- Human validation subset.

### Required Baselines

- SDXL.
- Prompt engineering.
- LLM-to-layout plus GLIGEN/ObjectDiffusion.
- MAC.
- CoMPaSS.
- CountLoop.
- Rejection sampling.
- A simple chained baseline: count method plus layout method plus detector feedback.

### Required Ablations

- No constraint scheduling.
- No conflict detection.
- Single-constraint objective versus joint objective.
- Count-first, layout-first, and ratio-first scheduling.
- Automatic graph versus oracle graph.
- Performance degradation as constraint count increases.
- Detector-only evaluation versus human validation.

### Maximum Risk

The main risk is that the work may look like benchmark plus objective aggregation. If the scheduling and conflict handling do not produce clear gains, reviewers may see it as an engineering evaluation rather than a method paper.

Another risk is that multi-constraint prompts are too hard for all methods, making it difficult to show a strong positive result.

### Potential Venue Level If Successful

If the method clearly improves joint constraint satisfaction and provides strong analysis of compositional degradation, it could target CVPR, ICCV, ECCV, NeurIPS Datasets and Benchmarks, or ICLR depending on method strength.

### Fallback If Experiments Fail

Downgrade to a benchmark/evaluation paper:

**A Compositional Numeric-Spatial Benchmark for Text-to-Image Generation**

The fallback contribution would be a systematic study of how existing T2I methods degrade as numeric-spatial constraints are composed.

## Candidate 3: NoBox-NSG

### Paper Title

**NoBox-NSG: Natural-Language Numeric-Spatial Graph Guidance for Diffusion Generation without Manual Layouts**

### Problem Statement

Strong layout-control methods often assume user-provided boxes, masks, or layouts. Real users provide natural language. The core question is how to transform natural-language numeric-spatial constraints into an executable representation and guide diffusion generation without manually supplied layouts.

### Difference from CountGen, CoMPaSS, MAC, ObjectDiffusion, D2D, and CountLoop

- **ObjectDiffusion / GLIGEN-style methods** require box or grounding inputs.
- **MAC** requires layout or box constraints.
- **CountGen / D2D / YOLO-Count** mainly cover object counting.
- **CoMPaSS** improves spatial language understanding but does not build an explicit numeric-spatial graph.
- **CountLoop** uses VLM planning and feedback, which can be expensive and black-box. This proposal emphasizes structured constraints and explainable constraint-level evaluation.

### Core Method

Build a no-manual-box numeric-spatial graph pipeline:

1. define a restricted constraint ontology rather than arbitrary JSON;
2. parse prompts into typed graph nodes and edges;
3. convert the graph into a soft layout distribution rather than hard user-provided boxes;
4. use graph-to-attention priors during early denoising;
5. use constraint energy during middle denoising;
6. output per-constraint satisfaction and failure explanations.

### Why This Is Not Prompt Engineering

The method does not merely rewrite the text prompt. It creates a typed graph, soft layout prior, and diffusion-stage energy. The parser, graph, and guidance modules must be evaluated separately.

### Why This Is Not Simple Engineering Composition

This proposal must avoid becoming "LLM -> JSON -> ControlNet." It must show:

- a task-specific graph schema;
- soft layout rather than manually supplied boxes;
- diffusion guidance that does not rely only on existing ControlNet inputs;
- constraint-specific energy functions;
- oracle graph versus automatic graph comparison.

### Training Requirement

Two possible routes:

- **training-free**: rule/LLM-assisted parser plus SDXL guidance;
- **light training**: graph-to-attention prior or graph-to-soft-layout predictor trained on synthetic constraint data.

The recommended initial route is training-free. If attention priors are unstable, add the light-trained prior.

### Required Data

- Prompt-to-graph dataset covering ratio, distance, relative position, and count.
- Synthetic prompts plus manual verification.
- Image-generation evaluation set.
- OOD prompts with unseen objects, numbers, relation types, and relation combinations.

### Required Baselines

- SDXL direct.
- Prompt engineering.
- LLM prompt rewriting.
- LLM-to-box plus GLIGEN/ObjectDiffusion.
- MAC with LLM-generated layouts.
- ControlNet with LLM-generated layout maps.
- CountLoop or another VLM planner if available.
- Rejection sampling.

### Required Ablations

- Oracle graph versus automatic graph.
- Hard boxes versus soft layout distributions.
- No graph-to-attention prior.
- No ratio/distance energy.
- No constraint satisfaction trace.
- Different parser schemas.
- Training-free versus light-trained prior.
- Failure attribution by parser, guidance, and evaluator.

### Maximum Risk

This is the candidate most likely to be criticized as an engineering system. If the parser depends heavily on an LLM and the guidance resembles box generation, reviewers may treat it as a weak variant of LLM-to-box plus existing layout control.

The method must prove that the graph representation and soft guidance provide value beyond directly asking an LLM for boxes.

### Potential Venue Level If Successful

If automatic graph parsing plus soft diffusion guidance clearly outperforms LLM-to-box, MAC, and ObjectDiffusion-style baselines on ratio, distance, and compositional constraints, this could be a main-conference submission.

### Fallback If Experiments Fail

Downgrade to an analysis/evaluation paper:

**Natural Language to Graph vs Natural Language to Box for Numeric-Spatial Text-to-Image Control**

This fallback would compare prompt rewriting, LLM-to-box, graph parsing, and VLM planning for numeric-spatial controllability.

## Unique Recommendation

The unique recommended direction is:

**RatioDistGraph**

## Recommendation Rationale

RatioDistGraph is the best option because:

1. It avoids the most crowded directions:
   - not count-only;
   - not ordinary left/right/above/below relation control;
   - not manual layout-to-image.

2. The research problem is sharper:
   - ratio control;
   - distance control;
   - equal spacing;
   - boundary-fraction positioning.

3. The method boundary is clearer:
   - constraint graph;
   - ratio/distance energy;
   - diffusion-stage guidance.

4. The MVP is more controllable:
   - two-object size ratio;
   - two-object distance ratio;
   - three-object equal spacing;
   - boundary-fraction constraints.

5. The fallback remains useful:
   - even if the method fails, a focused RatioDistBench could still become a workshop or evaluation paper.

## Recommended MVP

Start with the smallest version of RatioDistGraph:

1. two-object size ratio;
2. two-object distance ratio;
3. three-object equal spacing;
4. boundary-fraction position.

The first experimental goal should be to show that SDXL, prompt engineering, MAC, LLM-to-box, and ObjectDiffusion-style baselines are unstable on these constraints, while RatioDistGraph improves constraint satisfaction without severe image-quality collapse.

