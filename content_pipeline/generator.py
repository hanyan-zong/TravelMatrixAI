from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .ai_planner import ContentPlan, plan_with_openai, render_ai_post
from .config import OUTPUT_DIR, OpenAISettings, load_openai_settings
from .copywriter import build_copy_context, fill_copy_templates, generate_template_post
from .image_generator import generate_images_from_prompts
from .poster import create_poster
from .prompt_builder import fill_image_prompts
from .selection import ResourceSelection, find_resource_by_id, select_by_rules
from .text_utils import parse_date, safe_str


@dataclass(frozen=True)
class GenerateOptions:
    use_ai_plan: bool = False
    generate_images: bool = False
    generate_poster: bool = False
    output_dir: Path = OUTPUT_DIR


def schedule_dates(data: dict) -> list[date]:
    dates: list[date] = []
    for row in data["schedule"]:
        parsed = parse_date(row.get("发布日期"))
        if parsed and parsed not in dates:
            dates.append(parsed)
    return sorted(dates)


def _candidate_resources(data: dict, selection: ResourceSelection, limit: int = 40) -> list[dict]:
    selected_ids = {
        safe_str(selection.main.get("resource_id")),
        safe_str(selection.mix1.get("resource_id")) if selection.mix1 else "",
        safe_str(selection.mix2.get("resource_id")) if selection.mix2 else "",
    }
    candidates = [
        r for r in data["resources"]
        if safe_str(r.get("resource_id")) in selected_ids
        or safe_str(r.get("resource_type")) in {
            safe_str(selection.main.get("resource_type")),
            safe_str(selection.mix1.get("resource_type")) if selection.mix1 else "",
            safe_str(selection.mix2.get("resource_type")) if selection.mix2 else "",
        }
    ]
    return candidates[:limit]


def _selection_from_plan(
    base: ResourceSelection,
    data: dict,
    plan: ContentPlan | None,
) -> ResourceSelection:
    if not plan:
        return base

    main = find_resource_by_id(data["resources"], plan.main_resource_id) or base.main
    mixes = [
        find_resource_by_id(data["resources"], rid)
        for rid in plan.mix_resource_ids[:2]
    ]
    mixes = [m for m in mixes if m]
    mix1 = mixes[0] if mixes else base.mix1
    mix2 = mixes[1] if len(mixes) > 1 else base.mix2
    return ResourceSelection(
        schedule_row=base.schedule_row,
        theme=base.theme,
        main=main,
        mix1=mix1,
        mix2=mix2,
        mode="openai",
        reason=plan.selection_reason,
    )


def _write_outputs(
    out_dir: Path,
    output_data: dict,
    post_text: str,
    image_prompts: list[dict],
    html: str,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "content_data.json").write_text(
        json.dumps(output_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "post_text.txt").write_text(post_text, encoding="utf-8")

    prompt_lines: list[str] = []
    for item in image_prompts:
        prompt_lines.extend(
            [
                f"[{item['prompt_type']}]",
                f"Prompt: {item['filled_prompt']}",
                f"Negative: {item['negative']}",
                f"Aspect: {item['aspect']}",
                "",
            ]
        )
    (out_dir / "image_prompts.txt").write_text("\n".join(prompt_lines), encoding="utf-8")
    (out_dir / "preview.html").write_text(html, encoding="utf-8")


def _html_preview(
    target_date: date,
    selection: ResourceSelection,
    post_text: str,
    image_prompts: list[dict],
    generated_images: list[dict],
    poster_path: Path | None,
) -> str:
    def resource_card(resource: dict | None, label: str) -> str:
        if not resource:
            return ""
        return f"""
        <section class="resource">
          <strong>{label}</strong>
          <div>{safe_str(resource.get('resource_id'))} · {safe_str(resource.get('resource_type'))}</div>
          <h3>{safe_str(resource.get('product_name_cn'))}</h3>
          <p>{safe_str(resource.get('area'))} · {safe_str(resource.get('price_text'))}</p>
          <p>{safe_str(resource.get('highlights'))}</p>
        </section>
        """

    prompt_cards = "\n".join(
        f"<section class='prompt'><strong>{p['prompt_type']}</strong><p>{p['filled_prompt']}</p><small>{p['negative']} · {p['aspect']}</small></section>"
        for p in image_prompts
    )
    poster_html = f"<img class='poster' src='{poster_path.name}' alt='poster'>" if poster_path else ""
    image_gallery = "\n".join(
        f"<figure><img src='{Path(item['path']).name}' alt='{item['prompt_type']}'><figcaption>{item['prompt_type']}</figcaption></figure>"
        for item in generated_images
        if item.get("path")
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BWS 内容预览 - {target_date.isoformat()}</title>
  <style>
    body {{ margin: 0; background: #f5f5f5; color: #252525; font-family: -apple-system, BlinkMacSystemFont, "Microsoft YaHei", sans-serif; }}
    main {{ max-width: 1080px; margin: 0 auto; padding: 24px; }}
    header, .panel {{ background: #fff; border: 1px solid #e7e7e7; border-radius: 8px; padding: 20px; margin-bottom: 16px; }}
    h1 {{ margin: 0 0 8px; font-size: 24px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }}
    .resource, .prompt {{ border: 1px solid #eee; border-radius: 8px; padding: 14px; background: #fff; }}
    .post {{ white-space: pre-wrap; line-height: 1.8; }}
    .poster {{ width: min(360px, 100%); border-radius: 8px; display: block; }}
    figure {{ margin: 0; }}
    figure img {{ width: 100%; border-radius: 8px; display: block; }}
    figcaption {{ margin-top: 6px; color: #666; font-size: 13px; }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>{target_date.isoformat()} · {safe_str(selection.theme.get('主题名称'))}</h1>
    <div>{selection.mode} · {selection.reason}</div>
  </header>
  <div class="panel grid">
    {resource_card(selection.main, "主资源")}
    {resource_card(selection.mix1, "搭配 1")}
    {resource_card(selection.mix2, "搭配 2")}
  </div>
  <div class="panel">{poster_html}<div class="post">{post_text}</div></div>
  <div class="panel grid">{image_gallery}</div>
  <div class="panel">{prompt_cards}</div>
</main>
</body>
</html>"""


def generate_for_date(
    target_date: date,
    data: dict,
    options: GenerateOptions,
    settings: OpenAISettings | None = None,
) -> Path:
    settings = settings or load_openai_settings()
    base_selection = select_by_rules(data, target_date)
    if not base_selection:
        return Path("")

    plan = None
    openai_plan_error = ""
    if options.use_ai_plan:
        try:
            plan = plan_with_openai(
                settings,
                base_selection.schedule_row,
                base_selection.theme,
                _candidate_resources(data, base_selection),
            )
        except Exception as exc:
            openai_plan_error = f"{type(exc).__name__}: {exc}"

    selection = _selection_from_plan(base_selection, data, plan)
    ctx = build_copy_context(selection.theme, selection.main, selection.mix1, selection.mix2)
    filled_modules = fill_copy_templates(data["copy_templates"], ctx)
    post_text = render_ai_post(plan) if plan else generate_template_post(filled_modules, ctx)

    image_prompts = fill_image_prompts(data["image_prompts"], ctx)
    if plan and image_prompts:
        image_prompts[0]["filled_prompt"] += f"\nVisual direction: {plan.image_prompt_brief}"

    out_dir = options.output_dir / target_date.isoformat()
    generated_images: list[dict[str, str]] = []
    if options.generate_images and image_prompts:
        generated_images = generate_images_from_prompts(
            settings,
            image_prompts,
            out_dir,
        )
    generated_cover = next((Path(item["path"]) for item in generated_images if item.get("path")), None)

    poster_path = None
    if options.generate_poster:
        poster_path = create_poster(
            generated_cover,
            out_dir / "poster.jpg",
            plan.title if plan else (filled_modules.get("标题公式") or safe_str(selection.schedule_row.get("小红书标题"))),
            ctx.get("封面卖点", ""),
            ctx.get("价格", ""),
        )

    output_data = {
        "date": target_date.isoformat(),
        "selection_mode": selection.mode,
        "selection_reason": selection.reason,
        "openai_plan_error": openai_plan_error,
        "theme_id": safe_str(selection.schedule_row.get("主题ID")),
        "theme_name": safe_str(selection.theme.get("主题名称")),
        "schedule_row": {k: safe_str(v) for k, v in selection.schedule_row.items()},
        "main_resource": {k: safe_str(v) for k, v in selection.main.items()},
        "mix1_resource": {k: safe_str(v) for k, v in selection.mix1.items()} if selection.mix1 else None,
        "mix2_resource": {k: safe_str(v) for k, v in selection.mix2.items()} if selection.mix2 else None,
        "ai_plan": plan.model_dump() if plan else None,
        "filled_copy_modules": filled_modules,
        "full_post_text": post_text,
        "image_prompts": image_prompts,
        "generated_images": generated_images,
        "poster": str(poster_path) if poster_path else "",
        "context_variables": ctx,
    }
    html = _html_preview(target_date, selection, post_text, image_prompts, generated_images, poster_path)
    _write_outputs(out_dir, output_data, post_text, image_prompts, html)
    return out_dir
