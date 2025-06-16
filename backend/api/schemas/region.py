from pydantic import BaseModel


class RegionBase(BaseModel):
    name: str


class RegionResponse(BaseModel):
    region_id: int
    name: str

    class Config:
        from_attributes = True
