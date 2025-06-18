import json
from typing import Dict, Any, List

from fastapi import APIRouter, Depends
from mistralai import Mistral

from backend.api.routers.region import get_all_regions
from backend.api.routers.new import create_new, get_morning_digest
from backend.api.schemas.ai import NewRequest
from backend.api.schemas.region import RegionResponse
from backend.api.schemas.new import NewCreateRequest, NewResponse
from backend.config import settings
from backend.api.database.db import get_db, AsyncSession

router = APIRouter(prefix="/ai", tags=["AI"])

# Используем официальный клиент Mistral
MISTRAL_API_KEY = settings.API_KEY_MISTRAL
MISTRAL_MODEL = "mistral-large-latest"
mistral = Mistral(api_key=MISTRAL_API_KEY)

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
    ai_answer['text'] = new_total_text
    if len(ai_answer.get("text", "")) > 0:
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
    prompt = prestory + f"""Ты получил новость (конец будет обозначен знаками #$%): {new_total_text}#$%
Ты должен проанализировать эту новость и вернуть в качестве ответа JSON файл с полями:
1) tonality — одна из трёх строк: POSITIVE, NEUTRAL, NEGATIVE;
2) value — число от 1 до 3;
3) regions — список id областей влияния из доступных: {regions}).
Если новость не оказывает влияния на представленные области, верни пустой JSON.

Не пиши ничего кроме него:
"""
    response = mistral.chat.complete(
        model=MISTRAL_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.0
    )
    raw = response.choices[0].message.content.strip()
    raw = '{' + raw.split('{')[1].split('}')[0] + '}'
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"Не удалось распарсить JSON от AI:\n{raw}")
    return {
        "text": parsed.get("text", ""),
        "tonality": parsed.get("tonality", "NEUTRAL"),
        "value": int(parsed.get("value", 1)),
        "region_ids": parsed.get('regions', [])
    }

async def summarize_for_user(new_texts: List[Dict[str, Any]], regions: List[Dict[str, Any]]) -> str:
    prompt = prestory + f"""Тебе передали список JSON, в котором содержатся новости и их параметры. Напиши сжатую сводку по новостям,
в формате "утренний дайджест финансовой газеты". Новости, которые ты получишь, произошли в промежутке с 7.00 утра вчерашнего дня до 7.00 утра текущего дня.

Новости: {new_texts}\nОбласти влияния (regions): {regions}. В конце текста напиши, насколько сильным было влияние на каждую из областей, id которых были в полученных тобой новостях.

В качестве ответа верни JSON с полем text (твоя сводка).

Твой ответ (JSON):
"""
    response = mistral.chat.complete(
        model=MISTRAL_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.2
    )
    raw = response.choices[0].message.content.strip()
    raw = '{' + raw.split('{')[1].split('}')[0] + '}'
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"Не удалось распарсить JSON от AI:\n{raw}")

    return parsed.get("text", "")
