from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.future import select
from sqlalchemy.sql import func

from backend.api.database.db import Base, get_engine
from backend.api.database.models import Region
from backend.api.routers import user, ticker, region, new, ai
from backend.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = await get_engine()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Проверяем, есть ли уже регионы в базе
        regions_count = await conn.scalar(select(func.count()).select_from(Region))
        if regions_count == 0:
            # Добавляем начальные данные
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

    print("\n--> Database tables created")

    async def cleanup():
        await engine.dispose()

    await cleanup()
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
    uvicorn.run(app, host=settings.API_DOMAIN, port=settings.API_PORT)
