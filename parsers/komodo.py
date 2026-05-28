import re

from models import KomodoTour, PriceTier
from parsers.utils import build_merged_map, cell_val, clean, auto_tags


def _build_pricing_map(text):
    """从合并定价文本构建关键词→PriceTier映射"""
    if not text:
        return {}

    d = {}

    for line in str(text).strip().split('\n'):
        m = re.search(r'(\d+)\s*$', line.strip())

        if not m:
            continue

        tier = PriceTier(min_people=2, max_people=None, price=float(m.group(1)), unit="元/人")

        if '8景点' in line:
            d['8景点'] = tier

        elif '6景点' in line:
            d['6景点'] = tier

        elif '日落' in line:
            d['日落'] = tier

    return d


def parse_komodo(ws, surcharge_note=None):
    merged = build_merged_map(ws)
    results = []

    pricing_text = clean(cell_val(ws, 2, 2, merged))
    pricing_map = _build_pricing_map(pricing_text)

    for row in range(2, ws.max_row + 1):
        a = cell_val(ws, row, 1, merged)
        c = cell_val(ws, row, 3, merged)

        a_str = clean(a)

        if not a_str:
            continue

        name_match = re.search(r'【(.+?)】', a_str)
        name = name_match.group(1) if name_match else a_str.split('\n')[0].strip()

        lines = a_str.split('\n')
        itinerary = '\n'.join(ln.strip() for ln in lines[1:] if ln.strip()).strip()

        product_pricing = [tier for key, tier in pricing_map.items() if key in name]

        results.append(KomodoTour(
            name=name,
            itinerary=itinerary,
            pricing=product_pricing,
            inclusions=clean(c),
            surcharge_note=surcharge_note,
            tags=auto_tags(name, itinerary),
        ))

    return results
