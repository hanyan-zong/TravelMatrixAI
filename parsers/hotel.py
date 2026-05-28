import re

from models import Hotel, RoomOption
from parsers.utils import (
    build_merged_map, cell_val, clean, split_name, auto_tags,
)

REGION_KEYWORDS = {
    "库塔": ["Kuta"],
    "水明漾": ["Seminyak"],
    "金巴兰": ["Jimbaran"],
    "乌布": ["Ubud"],
    "努沙杜瓦": ["Nusa Dua"],
    "沙努尔": ["Sanur"],
    "乌鲁瓦图": ["Uluwatu"],
    "登巴萨": ["Denpasar"],
    "苍古": ["Canggu"],
}


def _guess_region(name):
    """从酒店名猜测区域"""
    if not name:
        return None

    name_lower = name.lower()

    return next(
        (cn for cn, en_list in REGION_KEYWORDS.items()
         if cn in name or any(kw.lower() in name_lower for kw in en_list)),
        None,
    )


def _split_room_name(text):
    """拆分房型的中英文名称"""
    if not text:
        return None, None

    lines = [ln.strip() for ln in str(text).strip().split('\n') if ln.strip()]
    en_parts, cn_parts = [], []

    for ln in lines:

        if re.search(r'[a-zA-Z]{2,}', ln):
            en_parts.append(ln)

        elif re.search(r'[一-鿿]', ln):
            cn_parts.append(ln)

        else:
            en_parts.append(ln)

    en = ' / '.join(en_parts) if en_parts else None
    cn = ' / '.join(cn_parts) if cn_parts else None
    return en or str(text).strip(), cn


def parse_standard_hotels(ws, surcharge_note=None):
    """解析'巴厘岛酒店'sheet: A=名, B=星级, C=区域, D=房型, E=日期, F=价格, G=备注"""
    merged = build_merged_map(ws)
    hotels = []

    current_name = None
    current_star = None
    current_region = None
    current_valid = None
    current_notes = None
    current_rooms = []

    def _flush():

        if current_name and current_rooms:
            en, cn = split_name(current_name)
            hotels.append(Hotel(
                tier="standard",
                name=en or current_name,
                name_cn=cn,
                star_rating=current_star or "",
                region=current_region,
                rooms=list(current_rooms),
                valid_dates=current_valid,
                notes=current_notes,
                surcharge_note=surcharge_note,
                tags=auto_tags(current_name, current_region or ""),
            ))

    for row in range(2, ws.max_row + 1):
        a = cell_val(ws, row, 1, merged)
        b = cell_val(ws, row, 2, merged)
        c = cell_val(ws, row, 3, merged)
        d = cell_val(ws, row, 4, merged)
        e = cell_val(ws, row, 5, merged)
        f = cell_val(ws, row, 6, merged)
        g = cell_val(ws, row, 7, merged)

        if all(v is None for v in [a, d, f]):
            continue

        a_raw = ws.cell(row, 1).value

        if a_raw is not None:
            _flush()
            current_name = clean(a_raw)
            current_star = clean(b)
            current_region = clean(c)
            current_valid = clean(e)
            current_notes = clean(g)
            current_rooms = []

        d_str = clean(d)

        if d_str and f is not None:

            try:
                price = float(str(f).replace(',', ''))

            except ValueError:
                continue

            room_en, room_cn = _split_room_name(d_str)
            current_rooms.append(RoomOption(
                name=room_en or d_str,
                name_cn=room_cn,
                price=price,
            ))

            if e is not None:
                current_valid = clean(e)

    _flush()
    return hotels


def parse_luxury_hotels(ws, surcharge_note=None):
    """解析'高端酒店'sheet: A=名, B=星级, C=房型, D=价格"""
    merged = build_merged_map(ws)
    hotels = []

    current_name = None
    current_star = None
    current_rooms = []

    def _flush():

        if current_name and current_rooms:
            en, cn = split_name(current_name)
            region = _guess_region(current_name)
            hotels.append(Hotel(
                tier="luxury",
                name=en or current_name,
                name_cn=cn,
                star_rating=current_star or "",
                region=region,
                rooms=list(current_rooms),
                surcharge_note=surcharge_note,
                tags=auto_tags(current_name, "高端 奢华"),
            ))

    for row in range(2, ws.max_row + 1):
        a = cell_val(ws, row, 1, merged)
        b = cell_val(ws, row, 2, merged)
        c = cell_val(ws, row, 3, merged)
        d = cell_val(ws, row, 4, merged)

        if all(v is None for v in [a, c, d]):
            continue

        a_raw = ws.cell(row, 1).value

        if a_raw is not None:
            _flush()
            current_name = clean(a_raw)
            current_star = clean(b)
            current_rooms = []

        c_str = clean(c)
        d_str = clean(d)

        if c_str and d_str:
            m = re.search(r'([\d,.]+)', d_str)

            if m:
                price = float(m.group(1).replace(',', ''))
                current_rooms.append(RoomOption(
                    name=c_str,
                    price=price,
                ))

    _flush()
    return hotels
