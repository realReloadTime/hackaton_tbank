from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = 'postgresql+asyncpg://postgres:geirby2005@localhost:5432/hackaton_db'
    API_DOMAIN: str = 'localhost'
    TELEBOT_DOMAIN: str = 'localhost'
    WEB_APP_DOMAIN: str = 'localhost'


settings = Settings()
