from __future__ import annotations

from pydantic import BaseModel
from typing import Literal


class PriceTier(BaseModel):
    min_people: int
    max_people: int | None = None
    price: float
    unit: str


class TransportOption(BaseModel):
    type: Literal["transport"] = "transport"
    city: str
    category: str
    vehicle: str
    driver_lang: str | None = None
    destination: str
    price: float
    unit: str
    valid_until: str | None = None
    cancel_policy: str | None = None
    purchase_notes: str | None = None
    surcharge_note: str | None = None


class DayTour(BaseModel):
    type: Literal["day_tour"] = "day_tour"
    no: int | None = None
    name: str
    tour_mode: str
    duration: str | None = None
    itinerary: str
    pricing: list[PriceTier]
    valid_until: str | None = None
    cancel_policy: str | None = None
    inclusions: str | None = None
    notes: str | None = None
    surcharge_note: str | None = None
    tags: list[str] = []


class MultiDayTour(BaseModel):
    type: Literal["multi_day_tour"] = "multi_day_tour"
    name: str
    days_nights: str
    region: str = "泗水"
    itinerary: str
    pricing: list[PriceTier]
    pricing_notes: str | None = None
    tags: list[str] = []


class KomodoTour(BaseModel):
    type: Literal["komodo_tour"] = "komodo_tour"
    name: str
    itinerary: str
    pricing: list[PriceTier]
    inclusions: str | None = None
    notes: str | None = None
    surcharge_note: str | None = None
    tags: list[str] = []


class RoomOption(BaseModel):
    name: str
    name_cn: str | None = None
    price: float
    unit: str = "元/间/晚"


class Hotel(BaseModel):
    type: Literal["hotel"] = "hotel"
    tier: str
    name: str
    name_cn: str | None = None
    star_rating: str
    region: str | None = None
    rooms: list[RoomOption]
    valid_dates: str | None = None
    notes: str | None = None
    surcharge_note: str | None = None
    tags: list[str] = []


class AfternoonTea(BaseModel):
    type: Literal["afternoon_tea"] = "afternoon_tea"
    name_en: str
    name_cn: str
    region: str
    region_cn: str
    price_range: str
    highlights: str
    tags: list[str] = []


class Wellness(BaseModel):
    type: Literal["wellness"] = "wellness"
    name_en: str
    name_cn: str
    region: str
    region_cn: str
    description: str
    price_range: str
    tags: list[str] = []


class GuideService(BaseModel):
    type: Literal["guide"] = "guide"
    name: str
    pricing: list[PriceTier]
    valid_until: str | None = None
