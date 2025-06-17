from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

import aiohttp
import logging

from backend.config import settings

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.api.database.db import get_db
from backend.api.database.models import New, NewRegion, Region, User, UserTicker, Ticker, TickerRegion
from backend.api.schemas.new import (
    NewCreateRequest,
    NewResponse,
    UserNotification
)

router = APIRouter(prefix="/news", tags=["News"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=List[UserNotification])
async def create_new(
        new_data: NewCreateRequest,
        db: AsyncSession = Depends(get_db)
):
    """
    Добавление новости и получение списка пользователей для уведомлений.
    Возвращает данные для Telegram-бота: chat_id, тикеры, регионы и анализ новости.
    """
    # 1. Создаем запись новости
    new = New(
        text=new_data.text,
        tonality=new_data.tonality,
        value=new_data.value
    )
    db.add(new)
    await db.flush()  # Получаем new_id до коммита

    # 2. Привязываем регионы к новости
    regions = []
    for region_id in new_data.region_ids:
        region = (await db.execute(
            select(Region).filter(Region.region_id == region_id)
        )).scalar_one_or_none()
        if not region:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Region with id {region_id} not found"
            )
        regions.append(region)
        db.add(NewRegion(new_id=new.new_id, region_id=region_id))

    await db.commit()

    # 3. Находим пользователей, подписанных на тикеры этих регионов
    users_to_notify = []
    for region in regions:
        # Получаем тикеры региона
        tickers = (await db.execute(
            select(Ticker)
            .join(TickerRegion, TickerRegion.ticker_id == Ticker.ticker_id)
            .filter(TickerRegion.region_id == region.region_id)
        )).scalars().all()

        # Для каждого тикера находим подписанных пользователей
        for ticker in tickers:
            users = (await db.execute(
                select(User)
                .join(UserTicker, UserTicker.user_id == User.user_id)
                .filter(UserTicker.ticker_id == ticker.ticker_id)
            )).scalars().all()

            for user in users:
                users_to_notify.append({
                    "username": user.username,
                    "chat_id": user.chat_id,
                    "regions": [region.name for region in regions],
                    "tickers": [ticker.name for ticker in tickers],
                    "value": new_data.value,
                    "tonality": new_data.tonality
                })

    return users_to_notify


@router.get("/morning-digest", response_model=List[NewResponse])
async def get_morning_digest(db: AsyncSession = Depends(get_db)):
    """
    Получить все новости за период с 07:00 вчера до 07:00 сегодня.
    """
    now = datetime.now()
    today_7am = now.replace(hour=7, minute=0, second=0, microsecond=0)
    yesterday_7am = today_7am - timedelta(days=1)

    result = await db.execute(
        select(New)
        .options(selectinload(New.regions).selectinload(NewRegion.region))
        .filter(New.created_at >= yesterday_7am, New.created_at <= today_7am)
        .order_by(New.value.desc())  # Сортировка по важности (HIGH -> LOW)
    )
    news = result.scalars().all()

    return news


@router.get("/top-3", response_model=List[NewResponse])
async def get_top_3_news(db: AsyncSession = Depends(get_db)):
    """
    Получить 3 самые значимые новости за последние 24 часа (с 07:00 вчера до 07:00 сегодня).
    """
    now = datetime.now()
    today_7am = now.replace(hour=7, minute=0, second=0, microsecond=0)
    yesterday_7am = today_7am - timedelta(days=1)

    result = await db.execute(
        select(New)
        .options(selectinload(New.regions).selectinload(NewRegion.region))
        .filter(New.created_at >= yesterday_7am, New.created_at <= today_7am)
        .order_by(New.value.desc())
        .limit(3)
    )
    news = result.scalars().all()

    return news


@router.get("/{new_id}", response_model=NewResponse)
async def get_new_by_id(new_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получить новость по ID.
    """
    result = await db.execute(
        select(New)
        .options(selectinload(New.regions).selectinload(NewRegion.region))
        .filter(New.new_id == new_id)
    )
    new = result.scalar_one_or_none()

    if not new:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found"
        )

    return new


@router.get("/", response_model=List[NewResponse])
async def get_news_paginated(
        username: str,
        skip: int = 0,
        limit: int = 10,
        db: AsyncSession = Depends(get_db)
):
    """
    Получить новости с пагинацией, отфильтрованные по подпискам пользователя.
    """
    user = (await db.execute(
        select(User).filter(User.username == username)
    )).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_tickers = (await db.execute(
        select(UserTicker.ticker_id)
        .filter(UserTicker.user_id == user.user_id)
    )).scalars().all()

    if not user_tickers:
        return []

    regions = (await db.execute(
        select(TickerRegion.region_id)
        .filter(TickerRegion.ticker_id.in_(user_tickers))
    )).scalars().all()

    result = await db.execute(
        select(New)
        .join(NewRegion, NewRegion.new_id == New.new_id)
        .filter(NewRegion.region_id.in_(regions))
        .options(
            selectinload(New.regions).selectinload(NewRegion.region)
        )
        .order_by(New.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    news = result.scalars().all()

    return news


async def send_telegram_notifications(notifications: List[UserNotification]):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{settings.TELEGRAM_WEBHOOK_URL}/webhook",
                json={"notifications": [n.dict() for n in notifications]}
            ) as response:
                if response.status != 200:
                    logger.error(f"Failed to send Telegram notifications: {await response.text()}")
        except Exception as e:
            logger.error(f"Error sending Telegram notifications: {str(e)}")