from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .config import OpenAISettings
from .text_utils import safe_str


class ContentPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(description="小红书标题")
    hook: str = Field(description="开头钩子")
    content_angle: str = Field(description="本篇内容角度")
    main_resource_id: str = Field(description="主资源 ID")
    mix_resource_ids: list[str] = Field(description="搭配资源 ID，最多 2 个")
    selection_reason: str = Field(description="选择这些资源的理由")
    sections: list[str] = Field(description="正文分段，每段独立成文")
    hashtags: list[str] = Field(description="小红书标签，不带 # 或带 # 均可")
    image_prompt_brief: str = Field(description="给图片 prompt 的视觉方向补充")


def _compact_resource(resource: dict[str, Any]) -> dict[str, str]:
    keys = [
        "resource_id",
        "resource_type",
        "destination",
        "area",
        "product_name_cn",
        "price_text",
        "highlights",
        "suitable_for",
        "visual_keywords",
        "xhs_angle",
    ]
    return {key: safe_str(resource.get(key)) for key in keys}


def _schema() -> dict[str, Any]:
    return ContentPlan.model_json_schema()


def _build_prompt(schedule_row: dict, theme: dict, candidates: list[dict]) -> str:
    payload = {
        "schedule": {k: safe_str(v) for k, v in schedule_row.items()},
        "theme": {k: safe_str(v) for k, v in theme.items()},
        "candidate_resources": [_compact_resource(r) for r in candidates],
    }
    return (
        "你是 BWS 印尼旅行社的小红书内容策划。请只从候选资源里选择资源，"
        "生成适合发布的一篇小红书内容方案。避免夸大承诺，价格和包含项以资源数据为准。\n\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def plan_with_openai(
    settings: OpenAISettings,
    schedule_row: dict,
    theme: dict,
    candidates: list[dict],
) -> ContentPlan | None:
    if not settings.api_key:
        return None

    from openai import OpenAI

    client = OpenAI(api_key=settings.api_key)
    prompt = _build_prompt(schedule_row, theme, candidates)
    schema = _schema()

    if hasattr(client, "responses"):
        response = client.responses.create(
            model=settings.content_model,
            input=[
                {
                    "role": "system",
                    "content": "输出必须符合给定 JSON Schema，语言为中文，面向小红书旅行用户。",
                },
                {"role": "user", "content": prompt},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "content_plan",
                    "schema": schema,
                    "strict": True,
                }
            },
        )
        raw_text = response.output_text
    else:
        response = client.chat.completions.create(
            model=settings.content_model,
            messages=[
                {
                    "role": "system",
                    "content": "输出必须符合给定 JSON Schema，语言为中文，面向小红书旅行用户。",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "content_plan",
                    "schema": schema,
                    "strict": True,
                },
            },
        )
        raw_text = response.choices[0].message.content or "{}"

    return ContentPlan.model_validate_json(raw_text)


def render_ai_post(plan: ContentPlan) -> str:
    tags = " ".join(tag if tag.startswith("#") else f"#{tag}" for tag in plan.hashtags)
    return "\n\n".join([plan.title, plan.hook, *plan.sections, tags]).strip()
