from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.api.database.db import get_db
from backend.api.database.models import User, UserTicker, Ticker, TickerRegion
from backend.api.schemas.ticker import UserTickersResponse
from backend.api.schemas.user import UserResponse, AddPreferenceRequest, UsernameRequest

router = APIRouter(prefix="/users", tags=["User"])


@router.post('/first_launch')
async def first_launch(request: UsernameRequest, db: AsyncSession = Depends(get_db)):
    username = request.username
    chat_id = request.chat_id  # Добавляем chat_id из запроса

    user_in_db = (await db.execute(select(User).where(User.username == username))).scalar_one_or_none()
    if user_in_db:
        return JSONResponse(content={'detail': "User already registered."},
                            status_code=status.HTTP_208_ALREADY_REPORTED)

    new_user = User(username=username, chat_id=chat_id)  # Сохраняем chat_id
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return JSONResponse(content={'detail': "User successfully registered."},
                        status_code=status.HTTP_200_OK)


@router.get("/get", response_model=UserResponse)
async def get_user(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User)
        .options(selectinload(User.preferences))
        .filter(User.username == username)
    )
    user = result.scalar_one_or_none()

    return user


@router.delete('/preferences/delete', response_model=UserResponse)
async def delete_preference(
        ticker_id: int,
        username: str,
        db: AsyncSession = Depends(get_db)
):
    user = (await db.execute(
        select(User)
        .options(selectinload(User.preferences))
        .filter(User.username == username)
    )).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    await db.execute(
        delete(UserTicker)
        .where(
            (UserTicker.user_id == user.user_id) &
            (UserTicker.ticker_id == ticker_id)
        )
    )
    await db.commit()

    await db.refresh(user)
    return user


@router.get("/{username}/tickers", response_model=UserTickersResponse)
async def get_user_tickers(
    username: str,
    db: AsyncSession = Depends(get_db)
):
    user = (await db.execute(
        select(User).filter(User.username == username)
    )).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tickers = (await db.execute(
        select(Ticker)
        .join(UserTicker, UserTicker.ticker_id == Ticker.ticker_id)
        .options(selectinload(Ticker.region_associations).selectinload(TickerRegion.region))
        .filter(UserTicker.user_id == user.user_id)
        .distinct()  # Исключаем дубликаты
    )).scalars().all()

    return {
        "user_id": user.user_id,
        "username": user.username,
        "tickers": tickers  # Теперь включает ticker_id и регионы
    }


@router.post("/preferences/add", status_code=status.HTTP_201_CREATED)
async def add_preference(
        request: AddPreferenceRequest,
        db: AsyncSession = Depends(get_db)
):
    user = (await db.execute(
        select(User).filter(User.username == request.username)
    )).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    ticker = (await db.execute(
        select(Ticker).filter(Ticker.ticker_id == request.ticker_id)
    )).scalar_one_or_none()

    if not ticker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticker not found."
        )

    existing_preference = (await db.execute(
        select(UserTicker)
        .filter(
            (UserTicker.user_id == user.user_id) &
            (UserTicker.ticker_id == request.ticker_id)
        )
    )).scalar_one_or_none()

    if existing_preference:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticker already in user preferences."
        )

    new_preference = UserTicker(
        user_id=user.user_id,
        ticker_id=request.ticker_id
    )

    db.add(new_preference)
    await db.commit()

    return {"detail": "Ticker added to preferences successfully."}
