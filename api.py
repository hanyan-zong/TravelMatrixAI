from __future__ import annotations

import base64
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from content_pipeline.config import DEFAULT_EXCEL_PATH, OUTPUT_DIR, OpenAISettings, load_openai_settings
from content_pipeline.data_loader import load_all_data
from content_pipeline.generator import GenerateOptions, generate_for_date
from content_pipeline.text_utils import parse_date, safe_str

_data: dict[str, list[dict[str, Any]]] = {}
_openai_settings: OpenAISettings | None = None


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    global _data, _openai_settings
    _data = load_all_data(DEFAULT_EXCEL_PATH)
    _openai_settings = load_openai_settings()
    yield


app = FastAPI(title="BWS Social Content API", version="0.1.0", lifespan=_lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    use_ai_plan: bool = False
    generate_images: bool = False
    generate_poster: bool = False


def _read_content(out_dir: Path) -> dict[str, Any]:
    content_path = out_dir / "content_data.json"
    if not content_path.exists():
        return {}

    data = json.loads(content_path.read_text(encoding="utf-8"))

    poster_path = out_dir / "poster.jpg"
    data["poster_base64"] = (
        base64.b64encode(poster_path.read_bytes()).decode()
        if poster_path.exists() else None
    )

    images_b64: dict[str, str] = {}
    for item in data.get("generated_images", []):
        if item.get("path"):
            img_path = Path(item["path"])
            if not img_path.is_absolute():
                img_path = out_dir / img_path.name

            if img_path.exists():
                images_b64[item["prompt_type"]] = base64.b64encode(img_path.read_bytes()).decode()

    data["images_base64"] = images_b64
    return data


# ── 端点 ──────────────────────────────────────────────

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "resources_loaded": len(_data.get("resources", [])),
        "schedule_entries": len(_data.get("schedule", [])),
    }


@app.post("/reload")
def reload_data():
    global _data, _openai_settings
    _data = load_all_data(DEFAULT_EXCEL_PATH)
    _openai_settings = load_openai_settings()
    return {
        "status": "reloaded",
        "resources": len(_data["resources"]),
        "schedule": len(_data["schedule"]),
    }


@app.get("/schedule")
def list_schedule():
    entries = []

    theme_map = {safe_str(t.get("theme_id")): safe_str(t.get("主题名称")) for t in _data.get("themes", [])}

    for row in _data.get("schedule", []):
        d = parse_date(row.get("发布日期"))

        if not d:
            continue

        date_str = d.isoformat()
        theme_id = safe_str(row.get("主题ID"))

        entries.append({
            "date": date_str,
            "theme_id": theme_id,
            "theme_name": theme_map.get(theme_id, ""),
            "title": safe_str(row.get("小红书标题")),
            "has_generated": (OUTPUT_DIR / date_str / "content_data.json").exists(),
        })

    entries.sort(key=lambda e: e["date"])
    return {"dates": entries}


@app.get("/resources")
def list_resources(
    resource_type: str | None = Query(None, alias="type"),
    area: str | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    resources = _data.get("resources", [])

    if resource_type:
        resources = [r for r in resources if safe_str(r.get("resource_type")) == resource_type]

    if area:
        resources = [r for r in resources if safe_str(r.get("area")) == area]

    total = len(resources)
    page = resources[offset: offset + limit]
    return {
        "total": total,
        "resources": [
            {
                "resource_id": safe_str(r.get("resource_id")),
                "resource_type": safe_str(r.get("resource_type")),
                "product_name_cn": safe_str(r.get("product_name_cn")),
                "destination": safe_str(r.get("destination")),
                "area": safe_str(r.get("area")),
                "price_text": safe_str(r.get("price_text")),
                "highlights": safe_str(r.get("highlights")),
            }
            for r in page
        ],
    }


@app.get("/content/{date_str}")
def get_content(date_str: str):
    out_dir = OUTPUT_DIR / date_str
    if not (out_dir / "content_data.json").exists():
        raise HTTPException(404, f"No generated content found for {date_str}")
    return _read_content(out_dir)


@app.post("/generate")
def generate(req: GenerateRequest):
    target = parse_date(req.date)

    if not target:
        raise HTTPException(400, f"Invalid date format: {req.date}")

    options = GenerateOptions(
        use_ai_plan=req.use_ai_plan,
        generate_images=req.generate_images,
        generate_poster=req.generate_poster,
    )

    out_dir = generate_for_date(target, _data, options, _openai_settings)
    if not out_dir or not Path(out_dir).exists():
        raise HTTPException(404, f"No schedule entry found for date {req.date}")

    return _read_content(out_dir)
