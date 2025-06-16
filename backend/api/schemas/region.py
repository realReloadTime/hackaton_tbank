from pydantic import BaseModel


class RegionBase(BaseModel):
    name: str


class RegionResponse(RegionBase):
    region_id: int

    class Config:
        from_attributes = True
