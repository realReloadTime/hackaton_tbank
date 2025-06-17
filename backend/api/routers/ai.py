import json
from typing import Dict, Any, List

from fastapi import APIRouter, Depends
from openai import AsyncOpenAI

from backend.api.routers.region import get_all_regions
from backend.api.schemas.ai import NewRequest
from backend.api.schemas.region import RegionResponse
from backend.config import settings
from backend.api.database.db import get_db, AsyncSession

router = APIRouter(prefix="/ai", tags=["AI"])
client = AsyncOpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)

prestory = ('''Ты - опытный финансовый аналитик, которому передали свежую сводку новостей.
Ты знаешь, что некоторые новости могут влиять в некоторой степени на стоимость тех или иных акций. 
Твоя задача - оценивать влияние новостей.
Лично ты в качестве параметров для анализа выделяешь 
область влияния - region (на какую область новость может оказать влияние, например, "Нефть и газ"), 
tonality новости (делится на POSITIVE, NEGATIVE, NEUTRAL), 
value (важность новости по шкале от 1 до 3, 
где 1 - незначительное влияние, 2 - значительное влияние, 3 - очень значимое влияние).''')


@router.post("/new")
async def parsed_new(request: NewRequest, db: AsyncSession = Depends(get_db)):
    url = settings.API_DOMAIN + '/'
    new_total_text = f'{request.title} {request.text} Источник: {request.link}'
    regions = await get_all_regions(db)
    regions = [RegionResponse.model_validate(region).model_dump() for region in regions]
    ai_answer = await analyze_new(new_total_text, regions)
    print(ai_answer)

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

async def analyze_new(new_total_text: str, regions: List[Dict[int, Any]]) -> Dict[str, Any]:
    print(new_total_text,regions)
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
    prompt = prestory + f"""Ты получил новость (конец будет обозначен знаками #$%): {new_total_text}#$%
Ты должен проанализировать эту новость и вернуть в качестве ответа JSON файл с полями:
1) text — исходное содержание новости без изменений;
2) tonality — одна из трёх строк: POSITIVE, NEUTRAL, NEGATIVE;
3) value — число от 1 до 3;
4) regions — список id областей влияния из доступных: {regions}).
Если новость не оказывает влияния на представленные области, верни пустой JSON.

Твой ответ(JSON):
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
    return {
        "text": parsed.get("text", ""),
        "tonality": parsed.get("tonality", "neutral"),
        "value": int(parsed.get("value", 1)),
        "region_ids": parsed.get('regions', [1])
    }


async def summarize_for_user(news_text: List[str]) -> str:
    response = await client.completions.create(
        model="gigabateman-7b",
        prompt=f"""
        Ты - опытный финансовый аналитик, которому передали свежую сводку новостей. Ты знаешь, что некоторые новости могут влиять в некоторой степени на стоимость тех или иных акций. 
        Напиши сжатую сводку по новостям  краткое резюме новости предназначенного
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
