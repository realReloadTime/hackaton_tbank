from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.future import select
from sqlalchemy.sql import func

from backend.api.database.db import Base, get_engine
from backend.api.database.models import Region, Ticker, TickerRegion
from backend.api.routers import user, ticker, region, new, ai
from backend.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = await get_engine()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Проверяем и добавляем регионы, если их нет
        regions_count = await conn.scalar(select(func.count()).select_from(Region))
        if regions_count == 0:
            initial_regions = [
                {"name": "Нефть и газ"},
                {"name": "Металлы и добыча"},
                {"name": "Финансы и банки"},
                {"name": "Технологии"},
                {"name": "Здравоохранение"},
                {"name": "Потребительские товары"},
                {"name": "Энергетика"},
                {"name": "Телекоммуникации"},
                {"name": "Транспорт и логистика"},
                {"name": "Недвижимость"}
            ]
            await conn.execute(Region.__table__.insert(), initial_regions)
            print("--> Added initial regions data")

        # Проверяем и добавляем тикеры, если их нет
        tickers_count = await conn.scalar(select(func.count()).select_from(Ticker))
        if tickers_count == 0:
            # Получаем ID регионов
            result = await conn.execute(select(Region))
            regions = result.scalars().all()
            region_ids = {region.name: region.region_id for region in regions}

            initial_tickers = [
                {
                    "name": "GAZP",
                    "company": "Газпром",
                    "region_ids": [region_ids["Нефть и газ"]]
                },
                {
                    "name": "GMKN",
                    "company": "Норильский никель",
                    "region_ids": [region_ids["Металлы и добыча"]]
                },
                {
                    "name": "SBER",
                    "company": "Сбербанк",
                    "region_ids": [region_ids["Финансы и банки"]]
                },
                {
                    "name": "YNDX",
                    "company": "Яндекс",
                    "region_ids": [region_ids["Технологии"]]
                },
                {
                    "name": "PHOR",
                    "company": "ФосАгро",
                    "region_ids": [region_ids["Здравоохранение"], region_ids["Потребительские товары"]]
                }
            ]

            # Добавляем тикеры и их связи с регионами
            for ticker_data in initial_tickers:
                # Добавляем тикер
                ticker_result = await conn.execute(
                    Ticker.__table__.insert().values(
                        name=ticker_data["name"],
                        company=ticker_data["company"]
                    )
                )
                ticker_id = ticker_result.inserted_primary_key[0]

                # Добавляем связи с регионами
                for region_id in ticker_data["region_ids"]:
                    await conn.execute(
                        TickerRegion.__table__.insert().values(
                            ticker_id=ticker_id,
                            region_id=region_id
                        )
                    )

            print("--> Added initial tickers data")

    print("\n--> Database tables created")
    yield


app = FastAPI(title="Hackaton API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)

app.include_router(user.router)
app.include_router(ticker.router)
app.include_router(region.router)
app.include_router(new.router)
app.include_router(ai.router)


@app.get("/")
async def root():
    return RedirectResponse('/docs')


if __name__ == '__main__':
    import json

    json.dump(settings.model_dump(), open('../config_.json', 'w'))
    uvicorn.run(app, host=settings.API_DOMAIN, port=settings.API_PORT)

