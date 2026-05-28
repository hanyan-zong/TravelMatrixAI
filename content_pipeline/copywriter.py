from __future__ import annotations

from .text_utils import replace_template_vars, safe_str


SKIP_EXPERIENCE_KEYWORDS = {"机场接送", "舒适商务车", "中文司机", "行李", "交通便利", "酒店住宿"}


def build_copy_context(theme: dict, main: dict, mix1: dict | None, mix2: dict | None) -> dict[str, str]:
    destination = safe_str(main.get("destination")) or "巴厘岛"
    visual_keywords = safe_str(main.get("visual_keywords"))
    xhs_angle = safe_str(main.get("xhs_angle"))

    raw_keywords = [
        item.strip()
        for item in visual_keywords.replace("、", ",").split(",")
        if item.strip()
    ]
    experience_keywords = [kw for kw in raw_keywords if kw not in SKIP_EXPERIENCE_KEYWORDS]
    if experience_keywords:
        core_experience = "、".join(experience_keywords[:4])
    elif xhs_angle:
        core_experience = xhs_angle.replace("第一次去", "").replace("必玩", "")
    else:
        core_experience = f"{destination}旅行"

    def mix_info(resource: dict | None) -> str:
        if not resource:
            return ""
        return f"搭配推荐：{safe_str(resource.get('product_name_cn'))}（{safe_str(resource.get('price_text'))}）"

    target_crowd = safe_str(theme.get("目标人群"))
    return {
        "目的地": destination,
        "区域": safe_str(main.get("area")),
        "主题": safe_str(theme.get("主题名称")),
        "主题名称": safe_str(theme.get("主题名称")),
        "visual_keywords": visual_keywords,
        "xhs_angle": xhs_angle,
        "核心体验": core_experience,
        "亮点": safe_str(main.get("highlights")),
        "价格": safe_str(main.get("price_text")),
        "产品名": safe_str(main.get("product_name_cn")),
        "包含项": safe_str(main.get("includes")),
        "不含项": safe_str(main.get("excludes")),
        "适合人群": target_crowd or safe_str(main.get("suitable_for")),
        "注意事项": safe_str(main.get("caution")),
        "选题角度": safe_str(theme.get("选题角度")),
        "封面卖点": safe_str(theme.get("封面卖点")),
        "搭配1": mix_info(mix1),
        "搭配2": mix_info(mix2),
        "destination": destination,
        "area": safe_str(main.get("area")),
    }


def fill_copy_templates(copy_templates: list[dict], ctx: dict[str, str]) -> dict[str, str]:
    filled: dict[str, str] = {}
    for row in copy_templates:
        module = safe_str(row.get("模块"))
        template = safe_str(row.get("模板内容"))
        if module and template:
            filled[module] = replace_template_vars(template, ctx)
    return filled


def generate_template_post(filled_modules: dict[str, str], ctx: dict[str, str]) -> str:
    parts: list[str] = []

    if filled_modules.get("标题公式"):
        parts.append(filled_modules["标题公式"])
    if filled_modules.get("开头钩子"):
        parts.append(f"\n{filled_modules['开头钩子']}")

    parts.append("\n① 为什么值得去")
    for key in ("亮点", "封面卖点"):
        if ctx.get(key):
            parts.append(ctx[key])

    parts.append("\n② 行程安排")
    if ctx.get("产品名"):
        parts.append(f"📍 {ctx['产品名']}")
    if ctx.get("包含项"):
        parts.append(f"📦 一价全含：{ctx['包含项']}")

    parts.append("\n③ 适合谁")
    parts.append(f"👥 {ctx.get('适合人群') or '第一次去巴厘岛、想省心安排的小伙伴'}")

    parts.append("\n④ 费用")
    if ctx.get("价格"):
        parts.append(f"💰 {ctx['价格']}")
    if ctx.get("不含项"):
        parts.append(f"不含：{ctx['不含项']}")

    if ctx.get("注意事项"):
        note = ctx["注意事项"]
        parts.append("\n⑤ 注意事项")
        parts.append(f"⚠️ {note[:200]}{'...' if len(note) > 200 else ''}")

    mixes = [ctx.get("搭配1"), ctx.get("搭配2")]
    if any(mixes):
        parts.append("\n⑥ 搭配推荐")
        parts.extend(f"🔗 {mix}" for mix in mixes if mix)

    if filled_modules.get("卖点句"):
        parts.append(f"\n💡 {filled_modules['卖点句']}")
    if filled_modules.get("转化CTA"):
        parts.append(f"\n📩 {filled_modules['转化CTA']}")
    if filled_modules.get("标签池"):
        parts.append(f"\n{filled_modules['标签池']}")

    return "\n".join(parts)

