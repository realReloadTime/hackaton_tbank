from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
import aiohttp
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.api.database.db import get_db
from backend.api.database.models import New, NewRegion, Region, User, UserTicker, Ticker, TickerRegion
from backend.api.schemas.ai import NewRequest

from backend.config import settings

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/new")
async def parsed_new(request: NewRequest):
    url = settings.API_DOMAIN + '/'
    new_total_text = f'{request.title}\n{request.text}\n Источник: {request.link}'

    # async with aiohttp.ClientSession() as session:
    #     async with session.post():

#   далее отправка запроса на AI с текстом new_total_text. Получаем ответ и направляем на POST news/ с параметрами
# {
#   "text": "string",
#   "tonality": "POSITIVE",
#   "value": 1,
#   "region_ids": [
#     0
#   ]
# }

