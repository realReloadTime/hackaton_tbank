from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.api.database.db import get_db
from backend.api.database.models import Ticker, Region, TickerRegion
from backend.api.schemas.ticker import TickerResponse, TickerCreateRequest

from typing import List

router = APIRouter(prefix="/tickers", tags=["Ticker"])


@router.post("/", response_model=TickerResponse, status_code=status.HTTP_201_CREATED)
async def create_ticker(
        ticker_data: TickerCreateRequest,
        db: AsyncSession = Depends(get_db)
):
    # Проверяем существование всех регионов вне транзакции
    regions = []
    for region_id in ticker_data.region_ids:
        region = (await db.execute(
            select(Region).filter(Region.region_id == region_id)
        )).scalar_one_or_none()
        if not region:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Region with id {region_id} not found"
            )
        regions.append(region)

    # Проверяем уникальность имени тикера
    existing_ticker = (await db.execute(
        select(Ticker).filter(Ticker.name == ticker_data.name)
    )).scalar_one_or_none()

    if existing_ticker:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticker with this name already exists"
        )

    # Создаем тикер и связи в одной транзакции
    try:
        new_ticker = Ticker(
            name=ticker_data.name,
            company=ticker_data.company
        )
        db.add(new_ticker)
        await db.flush()  # Получаем ID до коммита

        # Добавляем связи с регионами
        for region in regions:
            db.add(TickerRegion(
                ticker_id=new_ticker.ticker_id,
                region_id=region.region_id
            ))

        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating ticker: {str(e)}"
        )

    # Загружаем полные данные для ответа
    ticker_with_regions = (await db.execute(
        select(Ticker)
        .options(selectinload(Ticker.region_associations).selectinload(TickerRegion.region))
        .filter(Ticker.ticker_id == new_ticker.ticker_id)
    )).scalar_one()

    return ticker_with_regions

    # Загружаем полные данные для ответа
    ticker_with_regions = ((await db.execute(select(Ticker)
                                            .options(selectinload(Ticker.region_associations)
                                                     .selectinload(TickerRegion.region))
                                            .filter(Ticker.ticker_id == new_ticker.ticker_id)))
                           .scalar_one())

    return ticker_with_regions


@router.get("/", response_model=List[TickerResponse])
async def get_all_tickers(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 5
):
    """
    Получить список всех тикеров с их регионами
    - **skip**: количество пропускаемых записей (для пагинации)
    - **limit**: максимальное количество возвращаемых записей
    """
    result = await db.execute(
        select(Ticker)
        .options(selectinload(Ticker.region_associations).selectinload(TickerRegion.region))
        .offset(skip)
        .limit(limit)
    )
    tickers = result.scalars().all()

    return tickers


@router.get('/my')
async def get_my_tickers(username: str,
                         db: AsyncSession = Depends(get_db)):
    user = (await db.execute(
        select(User).filter(User.username == username)
    )).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
