from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, field_validator

from backend.api.schemas.region import RegionResponse


class Tonality(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"

    @field_validator('tonality', mode='before')
    @classmethod
    def validate(cls, v):
        if isinstance(v, str):
            v = v.upper()  # Приводим к верхнему регистру
            if v in {"POSITIVE", "NEGATIVE", "NEUTRAL"}:
                return cls(v)
        raise ValueError("Invalid tonality value")


class ValueLevel(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    @field_validator('value', mode='before')
    @classmethod
    def validate_value_level(cls, v):
        if isinstance(v, str) and v.isdigit():
            v = int(v)
        if v in {1, 2, 3}:
            return cls(v)
        raise ValueError("Value must be 1 (LOW), 2 (MEDIUM) or 3 (HIGH)")


class NewBase(BaseModel):
    text: str
    tonality: Tonality
    value: ValueLevel


class NewCreateRequest(NewBase):
    region_ids: List[int]  # ID регионов, которые затрагивает новость


class NewRegionResponse(BaseModel):
    region: RegionResponse  # Changed from direct fields to use RegionResponse

    class Config:
        from_attributes = True


class NewResponse(NewBase):
    new_id: int
    created_at: datetime
    regions: List[NewRegionResponse]

    class Config:
        from_attributes = True


class UserNotification(BaseModel):
    username: str
    chat_id: int
    regions: List[str]  # Названия регионов
    tickers: List[str]  # Символы тикеров (например, "$GAZP")
    value: ValueLevel
    tonality: Tonality
