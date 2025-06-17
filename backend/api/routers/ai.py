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
import json
from typing import Dict, Any, List

from openai import AsyncOpenAI

router = APIRouter(prefix="/ai", tags=["AI"])
client = AsyncOpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)

@router.post("/new")
async def parsed_new(request: NewRequest):
    url = settings.API_DOMAIN + '/'
    new_total_text = f'{request.title}{request.text} Источник: {request.link}'

    print(new_total_text)

    print(new_total_text)

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

async def analyze_new(new_total_text: str, regions: Dict[str, int]) -> Dict[str, Any]:
    """
    Отправляет текст новости в AI для классификации и возвращает словарь вида:
    {
        "text": str,          # краткое резюме
        "tonality": str,      # "positive" | "neutral" | "negative"
        "value": int,         # 1..3
        "region_ids": List[int]
    }

    :param new_total_text: полный текст новости
    :param regions: словарь вида { "RegionName": region_id, ... }
    """
    # Запрашиваем у модели данные в виде чистого JSON
    prompt = f"""
Ты финансовый аналитик. Для следующей новости нужно в формате JSON вернуть:
1) text — краткое резюме;
2) tonality — одна из трёх строк: positive, neutral, negative;
3) value — число от 1 (низкое), 2(среднее), 3(очень высокое);
4) regions — список названий регионов (например [ "Нефть" , Приролный газ" , "Золото" , "IT" , "Банк" ]).

Новость:
\"\"\"{new_total_text}\"\"\"

Вывод(JSON):
"""
    resp = await client.completions.create(
        model="gigabateman-7b",
        prompt=prompt,
        max_tokens=200,
        temperature=0.0,
        stop=["\n\n"]
    )

    raw = resp.choices[0].text.strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"Не удалось распарсить JSON от AI:\n{raw}")

    # мапим названия регионов на их ID
    region_ids: List[int] = []
    for name in parsed.get("regions", []):
        rid = regions.get(name)
        if rid is not None:
            region_ids.append(rid)
    return {
        "text": parsed.get("text", ""),
        "tonality": parsed.get("tonality", "neutral"),
        "value": int(parsed.get("value", 1)),
        "region_ids": region_ids
    }

async def summarize_for_user(news_text: str) -> str:
    response = await client.completions.create(
        model="gigabateman-7b",
        prompt=f"""
        Ты финансовый аналитик. Создай краткое резюме новости предназначенного
        для поддержки частных розничных трейдеров на российском фондовом рынке, 
        в формате Утренний дайджест «финансовой газеты» по:
        1)Ключевым тикерам [Example: SBER, LKOH];
        2)Тональности: positive, neutral, negative
        3) Уровень влияния:
        1 - Низкое
        2 - Среднее
        3 - Очень высокое
        4)К какой области инвестиций относится [Example: Нефть, Приролный газ, Золото, IT, Банк]

        
        Новость: {news_text}
        
        Резюме:
        """,
        max_tokens=300,
        temperature=0.2,
        stop=["\n\n"]
    )
    return response.choices[0].text.strip()
