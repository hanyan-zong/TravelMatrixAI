import re

from models import DayTour, GuideService, PriceTier
from parsers.utils import (
    build_merged_map, cell_val, clean, parse_pricing_tiers,
    format_date, auto_tags,
)

_TOUR_MODE_MAP = {
    "拼车": "拼车拼船",
    "拼船": "拼车拼船",
    "专车": "专车",
    "包车": "包车",
}


def _detect_tour_mode(name):
    if not name:
        return "未知"

    return next((mode for kw, mode in _TOUR_MODE_MAP.items() if kw in name), "未知")


def parse_day_tours(ws, surcharge_note=None):
    merged = build_merged_map(ws)
    tours = []
    guide = None

    for row in range(2, ws.max_row + 1):
        a = cell_val(ws, row, 1, merged)
        b = cell_val(ws, row, 2, merged)
        c = cell_val(ws, row, 3, merged)
        d = cell_val(ws, row, 4, merged)
        f = cell_val(ws, row, 6, merged)
        g = cell_val(ws, row, 7, merged)
        h = cell_val(ws, row, 8, merged)
        i_col = cell_val(ws, row, 9, merged)
        j = cell_val(ws, row, 10, merged)

        if all(v is None for v in [a, b, d, f]):
            continue

        b_str = clean(b)

        if not b_str:
            continue

        no = None

        if a is not None:

            try:
                no = int(str(a).strip())

            except ValueError:
                continue

        # 导游服务（独立类型）
        if "导游" in b_str:
            tiers, _ = parse_pricing_tiers(str(f))

            if not tiers:
                m = re.match(r'[¥￥]?\s*([\d,.]+)\s*(元/\w+)', str(f or ''))

                if m:
                    tiers = [PriceTier(
                        min_people=int(re.search(r'(\d+)', str(d or '2')).group(1)),
                        max_people=None,
                        price=float(m.group(1).replace(',', '')),
                        unit=m.group(2),
                    )]

            guide = GuideService(
                name=b_str,
                pricing=tiers,
                valid_until=format_date(g),
            )
            continue

        name = b_str
        tour_mode = _detect_tour_mode(name)
        itinerary = clean(d) or ""
        pricing, _ = parse_pricing_tiers(str(f or ''))

        tours.append(DayTour(
            no=no,
            name=name,
            tour_mode=tour_mode,
            duration=clean(c),
            itinerary=itinerary,
            pricing=pricing,
            valid_until=format_date(g),
            cancel_policy=clean(h),
            inclusions=clean(i_col),
            notes=clean(j),
            surcharge_note=surcharge_note,
            tags=auto_tags(name, itinerary),
        ))

    if guide:
        tours.append(guide)

    return tours
