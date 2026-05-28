from __future__ import annotations

import base64
import re
from pathlib import Path

from .config import OpenAISettings


def generate_image_from_prompt(
    settings: OpenAISettings,
    prompt: str,
    output_path: Path,
) -> Path | None:
    if not settings.api_key:
        return None

    from openai import OpenAI

    client = OpenAI(api_key=settings.api_key)
    response = client.images.generate(
        model=settings.image_model,
        prompt=prompt,
        size=settings.image_size,
        quality=settings.image_quality,
        n=1,
    )

    image_b64 = response.data[0].b64_json
    if not image_b64:
        return None

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(base64.b64decode(image_b64))
    return output_path


def safe_image_name(index: int, prompt_type: str) -> str:
    name = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", prompt_type).strip("_")
    return f"image_{index:02d}_{name or 'image'}.png"


def generate_images_from_prompts(
    settings: OpenAISettings,
    image_prompts: list[dict[str, str]],
    output_dir: Path,
) -> list[dict[str, str]]:
    generated: list[dict[str, str]] = []
    for index, item in enumerate(image_prompts, 1):
        prompt = item["filled_prompt"]
        negative = item.get("negative", "")
        if negative:
            prompt = f"{prompt}\nAvoid: {negative}"

        path = output_dir / safe_image_name(index, item.get("prompt_type", "image"))
        try:
            generated_path = generate_image_from_prompt(settings, prompt, path)
        except Exception as exc:
            generated.append(
                {
                    "prompt_type": item.get("prompt_type", ""),
                    "path": "",
                    "prompt": prompt,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            break
        generated.append(
            {
                "prompt_type": item.get("prompt_type", ""),
                "path": str(generated_path) if generated_path else "",
                "prompt": prompt,
                "error": "",
            }
        )
    return generated
