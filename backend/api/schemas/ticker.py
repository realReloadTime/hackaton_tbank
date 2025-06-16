from typing import List
from pydantic import BaseModel

from backend.api.schemas.region import RegionResponse


class TickerBase(BaseModel):
    name: str
    company: str


class TickerResponse(TickerBase):
    ticker_id: int
    regions: List[RegionResponse]

    class Config:
        from_attributes = True


class TickerCreateRequest(TickerBase):
    region_ids: List[int]


class UserTickersResponse(BaseModel):
    user_id: int
    username: str
    tickers: List[TickerBase]

    class Config:
        from_attributes = True
