from models import AfternoonTea
from parsers.utils import build_merged_map, cell_val, clean, auto_tags, split_region


def parse_afternoon_tea(ws, surcharge_note=None):
    merged = build_merged_map(ws)
    results = []

    for row in range(2, ws.max_row + 1):
        a = cell_val(ws, row, 1, merged)
        b = cell_val(ws, row, 2, merged)
        c = cell_val(ws, row, 3, merged)
        d = cell_val(ws, row, 4, merged)
        e = cell_val(ws, row, 5, merged)
        f = cell_val(ws, row, 6, merged)

        if a is not None and '备注' in str(a):
            break

        b_str = clean(b)
        c_str = clean(c)

        if not b_str or not c_str:
            continue

        region_en, region_cn = split_region(clean(d))

        results.append(AfternoonTea(
            name_en=b_str,
            name_cn=c_str,
            region=region_en,
            region_cn=region_cn,
            price_range=clean(e) or "",
            highlights=clean(f) or "",
            tags=auto_tags(b_str, c_str, clean(f) or ""),
        ))

    return results
