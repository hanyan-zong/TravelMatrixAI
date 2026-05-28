import re

from models import MultiDayTour
from parsers.utils import (
    build_merged_map, cell_val, clean, parse_pricing_tiers, auto_tags,
)


def _extract_days_nights(name):
    """从产品名中提取天数，如 '布罗莫2天1晚' → '2天1晚'"""
    m = re.search(r'(\d+天\d+晚)', str(name))
    return m.group(1) if m else ""


def parse_multi_day_tours(ws, surcharge_note=None):
    merged = build_merged_map(ws)
    results = []

    for row in range(2, ws.max_row + 1):
        a = cell_val(ws, row, 1, merged)
        b = cell_val(ws, row, 2, merged)
        c = cell_val(ws, row, 3, merged)

        a_str = clean(a)
        b_str = clean(b)

        if not a_str:
            continue

        if a_str.startswith("备注"):
            continue

        name = a_str
        itinerary = b_str or ""
        days_nights = _extract_days_nights(name)
        pricing, pricing_notes = parse_pricing_tiers(str(c or ''))

        results.append(MultiDayTour(
            name=name,
            days_nights=days_nights,
            itinerary=itinerary,
            pricing=pricing,
            pricing_notes=pricing_notes,
            tags=auto_tags(name, itinerary),
        ))

    return results
