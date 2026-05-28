from models import TransportOption
from parsers.utils import build_merged_map, cell_val, clean, parse_simple_price, format_date


def parse_transport(ws, surcharge_note=None):
    merged = build_merged_map(ws)
    results = []

    current_product = None
    current_vehicle = None
    current_driver = None
    current_valid = None
    current_cancel = None
    current_purchase = None

    for row in range(2, ws.max_row + 1):
        a = cell_val(ws, row, 1, merged)
        b = cell_val(ws, row, 2, merged)
        c = cell_val(ws, row, 3, merged)
        d = cell_val(ws, row, 4, merged)
        e = cell_val(ws, row, 5, merged)
        f = cell_val(ws, row, 6, merged)
        g = cell_val(ws, row, 7, merged)
        h = cell_val(ws, row, 8, merged)
        i_col = cell_val(ws, row, 9, merged)

        if all(v is None for v in [a, b, c, d, e, f]):
            continue

        if a is not None and str(a).strip().isdigit():
            current_product = clean(b)
            current_driver = None

        if c is not None:
            current_vehicle = clean(c)

        if g is not None:
            current_valid = format_date(g)

        if h is not None:
            current_cancel = clean(h)

        if i_col is not None:
            current_purchase = clean(i_col)

        if f is None:
            continue

        price, unit = parse_simple_price(str(f))

        if price is None:
            continue

        prod = current_product or ""
        city = "雅加达" if "雅加达" in prod else "巴厘岛"

        if "接送" in str(e or "") or (unit == "元/趟"):
            category = "接送机"

        elif "包车" in prod or unit == "元/天":
            category = "包车"

        else:
            category = "接送机"

        d_str = clean(d)

        if d_str and "司机" in d_str:
            current_driver = d_str
            destination = clean(e) or ""

        else:
            destination = clean(e) or d_str or ""

        driver_lang = None

        if current_driver:
            driver_lang = "中文" if "中文" in current_driver else "印尼"

        results.append(TransportOption(
            city=city,
            category=category,
            vehicle=current_vehicle or "",
            driver_lang=driver_lang,
            destination=destination,
            price=price,
            unit=unit,
            valid_until=current_valid,
            cancel_policy=current_cancel,
            purchase_notes=current_purchase,
            surcharge_note=surcharge_note,
        ))

    return results
