from __future__ import annotations

from datetime import date, datetime
from typing import Any


def safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def parse_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日"):
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except ValueError:
                pass
    return None


def replace_template_vars(template: str, variables: dict[str, Any]) -> str:
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{key}}}", safe_str(value))
    return result

