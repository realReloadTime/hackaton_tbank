from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.api.database.db import get_db
from backend.api.database.models import Region
from backend.api.schemas.region import RegionResponse

router = APIRouter(prefix="/regions", tags=["Region"])


@router.get("/", response_model=List[RegionResponse])
async def get_all_regions(db: AsyncSession = Depends(get_db)):
    """
    Получить список всех областей (регионов) для тикеров
    """
    result = await db.execute(select(Region))
    regions = result.scalars().all()
    return regions
