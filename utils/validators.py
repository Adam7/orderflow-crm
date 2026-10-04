"""
Простые функции валидации пользовательского ввода.
"""
import re
from datetime import datetime

PHONE_RE = re.compile(r"^[\d\s\+\-\(\)]{5,20}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_phone(value: str) -> bool:
    return bool(PHONE_RE.match(value.strip()))


def is_valid_email(value: str) -> bool:
    return bool(EMAIL_RE.match(value.strip()))


def is_valid_price(value: str) -> bool:
    try:
        price = float(value.replace(",", ".").strip())
        return price >= 0
    except ValueError:
        return False


def parse_price(value: str) -> float:
    return round(float(value.replace(",", ".").strip()), 2)


def parse_date(value: str) -> datetime | None:
    """Принимает дату в формате ДД.ММ.ГГГГ, иначе None."""
    value = value.strip()
    for fmt in ("%d.%m.%Y", "%d.%m.%y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None
