from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = 'postgresql+asyncpg://postgres:geirby2005@localhost:5432/hackaton_db'
    API_DOMAIN: str = 'localhost'
    API_PORT: int = 8000
    TELEGRAM_BOT_TOKEN: str = '7867949246:AAFYbX8UvKQwLSsJbmLwepfZaAauzqHURuM'
    TELEGRAM_WEBHOOK_URL: str = 'https://w7aa7t-176-59-144-238.ru.tuna.am'
    WEB_APP_URL: str = 'localhost'


settings = Settings()
