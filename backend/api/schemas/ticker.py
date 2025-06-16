from typing import List
from pydantic import BaseModel, Field

from backend.api.schemas.region import RegionResponse


class TickerBase(BaseModel):
    name: str
    company: str


class TickerResponse(TickerBase):
    ticker_id: int
    regions: List[RegionResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
        json_encoders = {
            'Ticker': lambda v: v.dict()
        }


class TickerCreateRequest(TickerBase):
    region_ids: List[int]


class UserTickersResponse(BaseModel):
    user_id: int
    username: str
    tickers: List[TickerResponse]

    class Config:
        from_attributes = True
