import re

from models import PriceTier


def build_merged_map(ws):
    """构建合并单元格的值映射: (row, col) → top-left cell value"""
    merged = {}
    for rng in ws.merged_cells.ranges:
        val = ws.cell(rng.min_row, rng.min_col).value
        for r in range(rng.min_row, rng.max_row + 1):
            for c in range(rng.min_col, rng.max_col + 1):
                if r != rng.min_row or c != rng.min_col:
                    merged[(r, c)] = val
    return merged


def cell_val(ws, row, col, merged_map):
    v = ws.cell(row, col).value
    if v is not None:
        return v
    return merged_map.get((row, col))


def clean(text):
    if text is None:
        return None
    s = str(text).strip()
    return s if s else None


def parse_simple_price(text):
    """解析 '110元/趟' → (110.0, '元/趟')"""
    text = str(text).strip()
    m = re.match(r'[¥￥]?\s*([\d,.]+)\s*(元[/\w]*)', text)
    if m:
        return float(m.group(1).replace(',', '')), m.group(2)
    return None, None


def parse_pricing_tiers(text):
    """解析多档价格文本 → (PriceTier列表, 备注)

    '2人：450元/人\\n3人：400元/人' → ([PriceTier(...)], None)
    """
    if not text:
        return [], None

    tiers = []
    extra_notes = []

    for line in str(text).strip().split('\n'):
        line = line.strip()
        if not line:
            continue

        m = re.match(
            r'(\d+)\s*(?:[-–—~]\s*(\d+))?\s*人\s*[：:]\s*[¥￥]?\s*([\d,.]+)\s*(元/\w+)',
            line,
        )
        if m:
            tiers.append(PriceTier(
                min_people=int(m.group(1)),
                max_people=int(m.group(2)) if m.group(2) else int(m.group(1)),
                price=float(m.group(3).replace(',', '')),
                unit=m.group(4),
            ))
        elif re.match(r'[备注（(注]', line):
            extra_notes.append(line)

    return tiers, '\n'.join(extra_notes) if extra_notes else None


def format_date(val):
    if val is None:
        return None
    if hasattr(val, 'strftime'):
        return val.strftime('%Y-%m-%d')
    return str(val).strip()


TAG_KEYWORDS = {
    "浮潜": ["浮潜", "snorkeling"],
    "冲浪": ["冲浪", "surfing"],
    "瀑布": ["瀑布", "waterfall"],
    "火山": ["火山", "布罗莫", "伊真", "巴图尔"],
    "日出": ["日出", "sunrise"],
    "日落": ["日落", "sunset"],
    "探险": ["漂流", "ATV", "滑翔伞", "吉普车", "越野"],
    "文化": ["皇宫", "寺", "市场", "象窟"],
    "疗愈": ["疗愈", "SPA", "瑜伽", "冥想", "healing", "wellness"],
    "出海": ["出海", "船", "佩尼达", "蓝梦", "科莫多"],
    "高端": ["五星", "5星", "丽思", "瑞吉", "四季", "莱佛士", "六善", "凯宾斯基"],
    "海景": ["海景", "ocean", "beach", "海滩", "海边"],
    "悬崖": ["悬崖", "cliff", "崖"],
    "田园": ["梯田", "稻田", "rice"],
    "亲水": ["泳池", "pool"],
}


def auto_tags(*texts):
    combined = ' '.join(str(t) for t in texts if t).lower()
    return [tag for tag, keywords in TAG_KEYWORDS.items()
            if any(kw.lower() in combined for kw in keywords)]


def split_region(text):
    """拆分 'Nusa Dua 努沙杜瓦' → ('Nusa Dua', '努沙杜瓦')"""
    if not text:
        return "", ""

    m = re.match(r'([A-Za-z\s]+?)\s+([一-鿿]+)', str(text).strip())

    if m:
        return m.group(1).strip(), m.group(2).strip()

    return str(text).strip(), str(text).strip()


def split_name(text):
    """拆分中英文名称，返回 (英文, 中文)"""
    if not text:
        return None, None

    lines = [ln.strip().strip('()（）') for ln in str(text).strip().split('\n') if ln.strip()]

    en, cn = None, None
    for line in lines:
        has_en = bool(re.search(r'[a-zA-Z]{3,}', line))
        has_cn = bool(re.search(r'[一-鿿]', line))

        if has_en and not en:
            en = line
        if has_cn and not cn:
            cn = line

    return en, cn
