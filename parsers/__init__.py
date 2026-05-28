from parsers.transport import parse_transport
from parsers.day_tour import parse_day_tours
from parsers.multi_day_tour import parse_multi_day_tours
from parsers.komodo import parse_komodo
from parsers.hotel import parse_standard_hotels, parse_luxury_hotels
from parsers.afternoon_tea import parse_afternoon_tea
from parsers.wellness import parse_wellness

PARSERS = {
    "巴厘岛车费": parse_transport,
    "巴厘岛一日游": parse_day_tours,
    "泗水": parse_multi_day_tours,
    "科莫多": parse_komodo,
    "巴厘岛酒店": parse_standard_hotels,
    "高端酒店": parse_luxury_hotels,
    "高端下午茶": parse_afternoon_tea,
    "疗愈+瑜伽": parse_wellness,
}
