from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.api.database.db import Base


# Перечисление для тональности новости
class Tonality(PyEnum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


# Перечисление для значимости новости
class ValueLevel(PyEnum):
    LOW = 1  # незначительный
    MEDIUM = 2  # значительный
    HIGH = 3  # очень значимый


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)  # ссылка на телеграм-профиль
    preferences = relationship('UserTicker', back_populates='user')


class Region(Base):
    __tablename__ = 'regions'

    region_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)  # название области (нефть, золото, ИТ и т.п.)
    tickers = relationship('Ticker', back_populates='region')


class Ticker(Base):
    __tablename__ = 'tickers'

    ticker_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    company = Column(String, nullable=False)
    regions = relationship('TickerRegion', back_populates='ticker')


class TickerRegion(Base):
    __tablename__ = 'ticker_regions'

    ticker_id = Column(Integer, ForeignKey('tickers.ticker_id'), primary_key=True)
    region_id = Column(Integer, ForeignKey('regions.region_id'), primary_key=True)
    ticker = relationship('Ticker', back_populates='regions')
    region = relationship('Region')


# Вспомогательная таблица для связи многие-ко-многим между User и Ticker
class UserTicker(Base):
    __tablename__ = 'user_tickers'

    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    ticker_id = Column(Integer, ForeignKey('tickers.ticker_id'), primary_key=True)
    user = relationship('User', back_populates='preferences')
    ticker = relationship('Ticker')


class New(Base):
    __tablename__ = 'news'

    new_id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)  # полный текст новости
    tonality = Column(Enum(Tonality), nullable=False)  # тональность новости
    value = Column(Enum(ValueLevel), nullable=False)  # уровень влияния
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # время записи

    # Связь многие-ко-многим с Region через вспомогательную таблицу
    regions = relationship('NewRegion', back_populates='new')


# Вспомогательная таблица для связи многие-ко-многим между New и Region
class NewRegion(Base):
    __tablename__ = 'news_regions'

    new_id = Column(Integer, ForeignKey('news.new_id'), primary_key=True)
    region_id = Column(Integer, ForeignKey('regions.region_id'), primary_key=True)
    new = relationship('New', back_populates='regions')
    region = relationship('Region')
