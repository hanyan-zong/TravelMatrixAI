from __future__ import annotations

from .text_utils import replace_template_vars, safe_str


def fill_image_prompts(image_prompts: list[dict], ctx: dict[str, str]) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    for row in image_prompts:
        template = safe_str(row.get("GPT-image-2 Prompt 模板"))
        if not template:
            continue
        results.append(
            {
                "prompt_type": safe_str(row.get("prompt_type")),
                "filled_prompt": replace_template_vars(template, ctx),
                "negative": safe_str(row.get("负面/限制")),
                "aspect": safe_str(row.get("画幅建议")),
            }
        )
    return results

