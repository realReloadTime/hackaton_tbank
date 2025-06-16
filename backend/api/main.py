from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.api.database.db import Base, get_engine

# from api.routers import


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = await get_engine()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return RedirectResponse('/docs')


if __name__ == '__main__':
    uvicorn.run(app, port=8000)
