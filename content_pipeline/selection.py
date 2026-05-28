from __future__ import annotations

import random
from dataclasses import dataclass

from .text_utils import parse_date, safe_str


THEME_RESOURCE_TYPE_MAP = {
    "T001": "一日游/玩乐",
    "T002": "酒店/常规",
    "T003": "酒店/高端",
    "T004": "小众路线/泗水",
    "T005": "科莫多/出海",
    "T006": "疗愈/瑜伽",
    "T007": "交通/车费",
}

THEME_MIX_TYPE_MAP = {
    "T001": ["交通/车费", "酒店/常规"],
    "T002": ["交通/车费", "疗愈/瑜伽"],
    "T003": ["高端下午茶", "疗愈/瑜伽"],
    "T004": ["交通/车费", "酒店/常规"],
    "T005": ["酒店/常规", "交通/车费"],
    "T006": ["酒店/常规", "高端下午茶"],
    "T007": ["一日游/玩乐", "酒店/常规"],
}

THEME_KEYWORD_HINTS = {
    "T001": ["佩尼达", "蓝梦", "海岛", "出海", "浮潜"],
    "T002": ["酒店", "住宿"],
    "T003": ["高端", "蜜月", "度假", "下午茶"],
    "T004": ["泗水", "布罗莫", "伊真", "火山"],
    "T005": ["科莫多", "粉沙滩", "出海"],
    "T006": ["疗愈", "瑜伽", "乌布", "苍古", "SPA"],
    "T007": ["包车", "接送机", "交通", "司机"],
}


@dataclass(frozen=True)
class ResourceSelection:
    schedule_row: dict
    theme: dict
    main: dict
    mix1: dict | None
    mix2: dict | None
    mode: str = "rules"
    reason: str = ""


def get_schedule_for_date(schedule: list[dict], target_date) -> dict | None:
    for row in schedule:
        if parse_date(row.get("发布日期")) == target_date:
            return row
    return None


def find_theme(themes: list[dict], theme_id: str) -> dict | None:
    return next((t for t in themes if safe_str(t.get("theme_id")) == theme_id), None)


def find_resource_by_id(resources: list[dict], resource_id: str) -> dict | None:
    return next((r for r in resources if safe_str(r.get("resource_id")) == resource_id), None)


def match_score(resource: dict, keywords: list[str]) -> int:
    text = " ".join(
        safe_str(resource.get(key))
        for key in ("product_name_cn", "visual_keywords", "xhs_angle", "area", "destination")
    )
    return sum(1 for keyword in keywords if keyword in text)


def pick_main_resource(
    resources: list[dict],
    theme_id: str,
    hint_id: str | None = None,
    rng: random.Random | None = None,
) -> dict:
    rng = rng or random
    if hint_id:
        found = find_resource_by_id(resources, hint_id)
        if found:
            return found

    resource_type = THEME_RESOURCE_TYPE_MAP.get(theme_id, "")
    candidates = [r for r in resources if safe_str(r.get("resource_type")) == resource_type] or resources
    keywords = THEME_KEYWORD_HINTS.get(theme_id, [])
    if not keywords:
        return rng.choice(candidates)

    scored = [(r, match_score(r, keywords)) for r in candidates]
    max_score = max(score for _, score in scored)
    top = [r for r, score in scored if score == max_score]
    return rng.choice(top)


def pick_mix_resource(
    resources: list[dict],
    theme_id: str,
    main: dict,
    slot: int,
    hint_id: str | None = None,
    rng: random.Random | None = None,
) -> dict | None:
    rng = rng or random
    if hint_id:
        found = find_resource_by_id(resources, hint_id)
        if found and safe_str(found.get("resource_id")) != safe_str(main.get("resource_id")):
            return found

    mix_types = THEME_MIX_TYPE_MAP.get(theme_id, [])
    if not mix_types:
        return None

    target_type = mix_types[min(slot - 1, len(mix_types) - 1)]
    candidates = [
        r for r in resources
        if safe_str(r.get("resource_type")) == target_type
        and safe_str(r.get("resource_id")) != safe_str(main.get("resource_id"))
    ]
    if not candidates:
        return None

    main_area = safe_str(main.get("area"))
    if main_area:
        same_area = [r for r in candidates if safe_str(r.get("area")) == main_area]
        if same_area:
            return rng.choice(same_area)

    main_destination = safe_str(main.get("destination"))
    if main_destination:
        same_destination = [r for r in candidates if safe_str(r.get("destination")) == main_destination]
        if same_destination:
            return rng.choice(same_destination)

    return rng.choice(candidates)


def select_by_rules(data: dict, target_date) -> ResourceSelection | None:
    schedule_row = get_schedule_for_date(data["schedule"], target_date)
    if not schedule_row:
        return None

    theme_id = safe_str(schedule_row.get("主题ID"))
    theme = find_theme(data["themes"], theme_id)
    if not theme:
        return None

    rng = random.Random(target_date.isoformat())
    main = pick_main_resource(
        data["resources"],
        theme_id,
        safe_str(schedule_row.get("主资源ID")) or None,
        rng,
    )
    mix1 = pick_mix_resource(
        data["resources"],
        theme_id,
        main,
        1,
        safe_str(schedule_row.get("搭配资源ID 1")) or None,
        rng,
    )
    mix2 = pick_mix_resource(
        data["resources"],
        theme_id,
        main,
        2,
        safe_str(schedule_row.get("搭配资源ID 2")) or None,
        rng,
    )
    return ResourceSelection(schedule_row, theme, main, mix1, mix2, reason="规则匹配 + 日期固定随机种子")

