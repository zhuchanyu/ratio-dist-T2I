# Literature Matrix: Numerical and Spatial Control in Diffusion Text-to-Image

This note summarizes the literature check for diffusion-based text-to-image work on precise numerical understanding, object counting, ratio control, distance control, and spatial relation control.

Uncertain information is explicitly marked as **Needs check**.

## 1. Core Paper Verification

| Paper | Year | Venue/Status | Link | Code | Benchmark | Diffusion T2I | Role in My Work |
|---|---:|---|---|---|---|---|---|
| Evaluating Numerical Reasoning in Text-to-Image Models / GeckoNum | 2024 | arXiv; NeurIPS 2024 Datasets & Benchmarks | <https://arxiv.org/abs/2406.14774> | Needs check | GeckoNum benchmark | Yes | Strong related work; evaluation reference for numerical reasoning |
| Improving Explicit Spatial Relationships in Text-to-Image Generation / SR4G | 2024 | arXiv | <https://arxiv.org/abs/2403.00587> | Needs check | SR4G dataset | Yes | Related work and possible spatial-relation baseline |
| Diagnostic Benchmark and Iterative Inpainting for Layout-Guided Image Generation / LayoutBench | 2024 | CVPR 2024 Workshop Oral | <https://layoutbench.github.io/> | Needs check | LayoutBench | Yes | Strong benchmark/reference for layout-guided generation |
| Make It Count / CountGen | 2024 | arXiv | <https://arxiv.org/abs/2406.10210> | Needs check | Count benchmarks, details need check | Yes | Strong baseline for object-count control |
| Detection-Driven Object Count Optimization for Text-to-Image Diffusion Models | 2024 | arXiv; later publication status needs check | <https://arxiv.org/abs/2408.11721> | Needs check | Count evaluation, details need check | Yes | Related work for detector-guided count control |
| Training-free Composite Scene Generation for Layout-to-Image Synthesis | 2024 | ECCV 2024 | <https://www.ecva.net/papers/eccv_2024/papers_ECCV/html/8472_ECCV_2024_paper.php> | Reported: <https://github.com/Papple-F/csg.git> | Layout-to-image evaluation, details need check | Yes | Layout-to-image baseline or related work |
| MAC: Training-Free Layout-to-Image Generation with Marginal Attention Constraints | 2024 | arXiv; revised version status needs check | <https://arxiv.org/abs/2411.10495> | Needs check | Uses DrawBench/HRS; details need check | Yes | Training-free diffusion-stage guidance baseline |
| Generating Compositional Scenes via Text-to-Image RGBA Instance Generation | 2024 | NeurIPS 2024 | <https://proceedings.neurips.cc/paper_files/paper/2024/hash/4d90363e96781894b1327b87d1ade17e-Abstract-Conference.html> | Needs check | Paper-specific experiments; reusable benchmark needs check | Yes | Related work for compositional scene generation |
| Evaluating the Generation of Spatial Relations in Text and Image Generative Models | 2024 | arXiv | <https://arxiv.org/abs/2411.07664> | Needs check | Spatial-relation evaluation, details need check | Partly; includes T2I and text models | Related work for spatial-relation evaluation |
| CoMPaSS: Enhancing Spatial Understanding in Text-to-Image Diffusion Models | 2024/2025 | arXiv; ICCV 2025 status needs check | <https://github.com/blurgyy/CoMPaSS> | Yes, repository found | Uses VISOR, T2I-CompBench Spatial, GenEval Position; details need check | Yes | Strong related work and likely strong baseline for spatial relations |
| ObjectDiffusion: Grounding Text-to-Image Diffusion Models for Controlled High-Quality Image Generation | 2025 | arXiv | <https://arxiv.org/abs/2501.09194> | Needs check | COCO2017 evaluation | Yes | Box-conditioned diffusion baseline |
| YOLO-Count: Differentiable Object Counting for Text-to-Image Generation | 2025 | ICCV 2025 | <https://openaccess.thecvf.com/content/ICCV2025/html/Zeng_YOLO-Count_Differentiable_Object_Counting_for_Text-to-Image_Generation_ICCV_2025_paper.html> | Needs check | Count evaluation, details need check | Yes | Strong count-control baseline |
| CountLoop | 2025 | arXiv | <https://arxiv.org/abs/2508.16644> | Needs check | COCO-Count, T2I-CompBench, high-instance benchmark; details need check | Yes | Related work for high-instance count control |
| D2D: Detector-to-Differentiable Critic for Object Count Optimization in Text-to-Image Generation | 2025 | arXiv | <https://arxiv.org/abs/2510.19278> | Needs check | D2D benchmark details need check | Yes | Related work for detector-to-guidance count control |

## 2. Capability Coverage Matrix

### 2.1 Constraint Coverage

| Paper | Count | Ratio | Distance | Relative Position | NL-to-Constraint | Need Layout/Box |
|---|---|---|---|---|---|---|
| GeckoNum | Strong | Partial | Weak | Weak | Prompt-level evaluation | No |
| SR4G | Weak | Weak | Weak | Strong | Automatic caption/data construction | No |
| LayoutBench | Medium | Indirect via size | Weak | Strong | No | Yes |
| CountGen | Strong | Weak | Weak | Weak | Parses/uses count prompts | No |
| Detection-Driven Count Optimization | Strong | Weak | Weak | Weak | Count-token oriented | No |
| Training-free Composite Scene Generation | Medium | Indirect via layout | Weak | Strong | No | Yes |
| MAC | Medium | Indirect via box size | Weak | Strong | No | Yes |
| RGBA Instance Generation | Medium | Manual/implicit | Manual/implicit | Strong | Weak or needs check | Often needs layout/composition plan |
| Spatial Relations Evaluation | Weak | Weak | Weak | Strong | Prompt-level evaluation | No |
| CoMPaSS | Weak | Weak | Weak | Strong | Prompt-level spatial relations | No |
| ObjectDiffusion | Medium | Indirect via box size | Indirect via boxes | Strong | No | Yes |
| YOLO-Count | Strong | Weak | Weak | Weak | Count-prompt oriented | No |
| CountLoop | Strong | Weak | Partial | Medium | VLM planner, needs check | Generated or planned layout, needs check |
| D2D | Strong | Weak | Weak | Weak | Count-prompt oriented | No |

### 2.2 Method and Evaluation Coverage

| Paper | Training-free/Fine-tuning | Detector/VLM | Diffusion Guidance | Main Limitation |
|---|---|---|---|---|
| GeckoNum | Evaluation only | Human annotation; evaluator details need check | No | Does not propose a control method |
| SR4G | Fine-tuning | No | Learned spatial behavior after fine-tuning | Relation set is limited; not focused on count/ratio/distance |
| LayoutBench | Benchmark plus iterative inpainting baseline | Detector-based evaluation, details need check | Inpainting-style iterative generation | Requires explicit layouts; weak NL-to-layout parsing |
| CountGen | Method details need check; likely model-guided generation | No or needs check | Uses diffusion internal features during denoising | Focuses on count, not ratio/distance/spatial composition |
| Detection-Driven Count Optimization | Inference optimization, details need check | Detector | Detector-driven guidance/optimization | Depends on detector quality; mostly count-only |
| Training-free Composite Scene Generation | Training-free | No | Inter-token and self-attention constraints | Requires explicit layout; not full NL parsing |
| MAC | Training-free | No | Cross/self-attention and latent optimization | Relies on attention-layout correspondence; needs layout |
| RGBA Instance Generation | Training-based instance/composition framework | No or needs check | Instance generation and composition | Not primarily a natural-language-to-constraint method |
| Spatial Relations Evaluation | Evaluation only | Human/GPT-4V or evaluator details need check | No | Diagnostic only; no generation-control method |
| CoMPaSS | Fine-tuning/training framework | No | Improves spatial understanding through data/model design | Mainly spatial relations; not unified numerical control |
| ObjectDiffusion | Fine-tuning | No | ControlNet + GLIGEN-style grounding | Requires box conditions; weak prompt-to-box parsing |
| YOLO-Count | Counting guidance/training details need check | Detector-like differentiable counter | Gradient/guidance for count control | Count-focused; not ratio/distance/spatial-relation focused |
| CountLoop | Training-free loop, details need check | VLM and possibly detector | Iterative feedback plus masks, details need check | High cost; attribution of failure is hard |
| D2D | Training-free optimization, details need check | Detector converted to differentiable critic | Noise-prior or inference optimization | Count-focused; depends on detector and benchmark assumptions |

## 3. Strongly Related Papers

The following papers are the most important for this project and should be prioritized for close reading:

1. Evaluating Numerical Reasoning in Text-to-Image Models / GeckoNum
2. Improving Explicit Spatial Relationships in Text-to-Image Generation / SR4G
3. Diagnostic Benchmark and Iterative Inpainting for Layout-Guided Image Generation / LayoutBench
4. Make It Count / CountGen
5. CoMPaSS: Enhancing Spatial Understanding in Text-to-Image Diffusion Models
6. ObjectDiffusion: Grounding Text-to-Image Diffusion Models for Controlled High-Quality Image Generation
7. MAC: Training-Free Layout-to-Image Generation with Marginal Attention Constraints
8. YOLO-Count: Differentiable Object Counting for Text-to-Image Generation
9. Training-free Composite Scene Generation for Layout-to-Image Synthesis
10. CountLoop

## 4. Papers Needing Manual Verification

The following items require manual verification before they are used as formal citations, baselines, or reproducible benchmarks:

| Paper | What Needs Verification |
|---|---|
| SR4G | Whether the official code and SR4G dataset are publicly available and complete |
| LayoutBench | Whether the project page provides directly runnable code and downloadable benchmark files |
| CountGen | Official code availability, benchmark access, and exact method category |
| Detection-Driven Object Count Optimization | Final publication status, official code, benchmark details |
| MAC | Official code availability and final publication status |
| RGBA Instance Generation | Official code availability and whether its evaluation assets are reusable |
| Spatial Relations Evaluation | Code/data availability and exact evaluator protocol |
| CoMPaSS | Exact publication status and reproducibility of code/data pipeline |
| ObjectDiffusion | Code availability and whether box-conditioned evaluation is directly reproducible |
| YOLO-Count | Code availability and benchmark release status |
| CountLoop | Code/data availability and exact VLM/detector dependencies |
| D2D | Code availability, benchmark availability, and final publication status |

## 5. Most Reliable Research Gaps

The strongest current gaps for a publishable project are:

1. **Unified natural-language-to-constraint parsing**

   Existing work often handles one narrow input type: count prompts, explicit spatial relations, or user-provided boxes/layouts. A still-open problem is parsing natural language into a unified numeric-spatial constraint representation covering object count, ratio, distance, relative position, and composition.

2. **Ratio and distance control**

   Count control and left/right/above/below relations are increasingly studied. In contrast, ratio and distance constraints such as "half the size", "one third from the left", "twice as far", and "equally spaced" remain underdeveloped.

3. **Control without manually provided boxes**

   Many strong layout-to-image methods assume box or layout input. For this project, a more distinctive direction is automatic constraint extraction from prompt text, followed by diffusion-stage guidance without requiring the user to manually specify boxes.

4. **Composable constraints**

   Real prompts combine multiple constraints: count plus ratio plus relative position plus distance. Existing methods tend to optimize one constraint at a time, and multi-constraint conflict resolution is not well solved.

5. **Reliable evaluation beyond FID/CLIPScore**

   The project should avoid relying on generic image quality metrics. A stronger contribution would define reproducible metrics for count accuracy, ratio error, distance error, relative-position accuracy, and multi-constraint satisfaction, with detector/VLM-based scores clearly separated from human verification.

