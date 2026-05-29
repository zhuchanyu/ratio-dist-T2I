"""Prompt variants for baseline experiments."""

from copy import deepcopy


def direct_prompt_variant(prompt: dict) -> dict:
    record = deepcopy(prompt)
    record["baseline_variant"] = "sdxl_direct"
    record["baseline_source_prompt"] = prompt["prompt"]
    return record


def strong_prompt_variant(prompt: dict) -> dict:
    record = deepcopy(prompt)
    relation = prompt["constraint_graph"]["relations"][0]
    objects = prompt["objects"]

    if prompt["task_type"] == "SIZE_RATIO":
        obj_a = objects[0]
        obj_b = objects[1]
        target = float(relation["target"])
        extra = (
            " Generate exactly two objects and no extra objects."
            f" The {obj_a['attributes'][0]} {obj_a['name']} must be visually about {target:g} times"
            f" the area of the {obj_b['attributes'][0]} {obj_b['name']}."
            " Keep both objects clearly separated on a plain background."
            " Preserve the requested object colors."
        )
    elif prompt["task_type"] == "BOUNDARY_FRACTION":
        obj_a = objects[0]
        target = float(relation["target"])
        extra = (
            " Generate exactly one clear object and no extra objects."
            f" Place the center of the {obj_a['attributes'][0]} {obj_a['name']} at x={target:.2f}"
            " of the image width measured from the left boundary."
            " Use a simple plain background and preserve the requested object color."
        )
    else:
        raise ValueError(f"Unsupported task_type for baseline prompt: {prompt['task_type']}")

    record["prompt"] = prompt["prompt"] + extra
    record["baseline_variant"] = "strong_prompt"
    record["baseline_source_prompt"] = prompt["prompt"]
    return record


def rejection_sampling_prompt_variant(prompt: dict) -> dict:
    record = direct_prompt_variant(prompt)
    record["baseline_variant"] = "rejection_sampling_candidates"
    return record


def build_baseline_prompt_sets(prompts):
    return {
        "sdxl_direct": [direct_prompt_variant(prompt) for prompt in prompts],
        "strong_prompt": [strong_prompt_variant(prompt) for prompt in prompts],
        "rejection_sampling_candidates": [rejection_sampling_prompt_variant(prompt) for prompt in prompts],
    }
