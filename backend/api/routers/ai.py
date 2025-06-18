import json
from typing import Dict, Any, List

from fastapi import APIRouter, Depends
from openai import AsyncOpenAI

from backend.api.routers.region import get_all_regions
from backend.api.routers.new import create_new, get_morning_digest
from backend.api.schemas.ai import NewRequest
from backend.api.schemas.region import RegionResponse
from backend.api.schemas.new import NewCreateRequest, NewResponse
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
    new_total_text = f'{request.title} {request.text} Источник: {request.link}'
    regions = await get_all_regions(db)
    regions = [RegionResponse.model_validate(region).model_dump() for region in regions]
    ai_answer = await analyze_new(new_total_text, regions)
    if len(ai_answer["text"]) > 0:
        result = await create_new(NewCreateRequest.model_validate(ai_answer), db)
        return result
    return {"detail": "No relevant news found"}


@router.get("/morning-digest")
async def digest_new(db: AsyncSession = Depends(get_db)):
    new_texts = await get_morning_digest(db)
    regions = await get_all_regions(db)
    if not new_texts:
        return None

    regions = [RegionResponse.model_validate(region).model_dump() for region in regions]
    new_texts = [NewResponse.model_validate(new).model_dump() for new in new_texts]
    ai_answer = await summarize_for_user(new_texts, regions)
    if not ai_answer:
        return None

    return {"text": ai_answer}


async def analyze_new(new_total_text: str, regions: List[Dict[str, Any]]) -> Dict[str, Any]:
    print(new_total_text, regions)

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


async def summarize_for_user(new_texts: List[Dict], regions: List[Dict[str, Any]]) -> str:
    response = await client.completions.create(
        model="gigabateman-7b",
        prompt=prestory + f"""Тебе передали список JSON, в котором содержатся новости и их параметры. Напиши сжатую сводку по новостям, 
        в формате "утренний дайджест финансовой газеты". Новости, которые ты получишь, произошли в промежутке с 7.00 утра вчерашнего дня до 7.00 утра текущего дня.

        Новости: {new_texts}\n Области влияния (regions): {regions}. В конце текста напиши, насколько сильным было влияние на каждую из областей, id которых были в полученных тобой новостях.
        
        В качеcтве ответа верни JSON с полями text (твоя сводка).
        
        Твой ответ (JSON):
        """,
        max_tokens=300,
        temperature=0.2,
        stop=["\n\n"]
    )

    raw = response.choices[0].text.strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"Не удалось распарсить JSON от AI:\n{raw}")

    return parsed.get("text", "")
