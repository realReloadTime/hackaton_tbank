from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.api.database.db import Base


# Перечисление для тональности новости
class Tonality(PyEnum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"


# Перечисление для значимости новости
class ValueLevel(PyEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    chat_id = Column(Integer, nullable=True)  # Добавляем chat_id для Telegram
    preferences = relationship('UserTicker', back_populates='user')


class Region(Base):
    __tablename__ = 'regions'

    region_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    # Изменяем связь, чтобы указывать на промежуточную таблицу
    ticker_associations = relationship('TickerRegion', back_populates='region')

    # Добавляем свойство для доступа к тикерам через ассоциации
    @property
    def tickers(self):
        return [assoc.ticker for assoc in self.ticker_associations]


class Ticker(Base):
    __tablename__ = 'tickers'

    ticker_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    company = Column(String, nullable=False)
    region_associations = relationship('TickerRegion', back_populates='ticker', lazy='selectin')

    @property
    def regions(self):
        return [assoc.region for assoc in self.region_associations]

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        data['regions'] = [region.dict() for region in self.regions]
        return data


class TickerRegion(Base):
    __tablename__ = 'ticker_regions'

    ticker_id = Column(Integer, ForeignKey('tickers.ticker_id'), primary_key=True)
    region_id = Column(Integer, ForeignKey('regions.region_id'), primary_key=True)
    ticker = relationship('Ticker', back_populates='region_associations')
    region = relationship('Region', back_populates='ticker_associations')


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
    text = Column(Text, nullable=False, unique=True)  # полный текст новости
    tonality = Column(Enum(Tonality), nullable=False)  # тональность новости
    value = Column(Integer, nullable=False)  # уровень влияния
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
