from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_EXCEL_PATH = BASE_DIR / "BWS碎片化整理 - 2026年05月25日 chatGPT清洗过的.xlsx"
OUTPUT_DIR = BASE_DIR / "output"


@dataclass(frozen=True)
class OpenAISettings:
    api_key: str | None
    content_model: str
    image_model: str
    image_size: str
    image_quality: str


def load_openai_settings() -> OpenAISettings:
    env_path = BASE_DIR / ".env"
    if load_dotenv:
        load_dotenv(env_path)
    elif env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    return OpenAISettings(
        api_key=os.getenv("OPENAI_API_KEY") or None,
        content_model=os.getenv("OPENAI_MODEL_CONTENT", "gpt-4o"),
        image_model=os.getenv("OPENAI_MODEL_IMAGE", "gpt-image-1"),
        image_size=os.getenv("OPENAI_IMAGE_SIZE", "1024x1536"),
        image_quality=os.getenv("OPENAI_IMAGE_QUALITY", "high"),
    )
