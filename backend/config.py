from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = 'postgresql+asyncpg://postgres:qah112@localhost:5432/hackaton_db'

    API_DOMAIN: str = '127.0.0.1'
    API_PORT: int = 8000

    TELEGRAM_BOT_TOKEN: str = '7867949246:AAFYbX8UvKQwLSsJbmLwepfZaAauzqHURuM'
    TELEGRAM_WEBHOOK_URL: str = 'bot2.academus-pobeda.ru'
    TELEGRAM_PORT: int = 7000
    API_KEY_MISTRAL: str = "JfSjIKgF2WRAVSLiYcB3ZOuEQF05Asjf"

    WEB_APP_URL: str = 'tbank2.academus-pobeda.ru'


settings = Settings()
