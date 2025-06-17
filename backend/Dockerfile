FROM python:3.9-slim

WORKDIR /app

# Установка зависимостей
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY ./ ./

# Переменные окружения
ENV PYTHONPATH=/app
ENV DATABASE_URL=postgresql+asyncpg://postgres:geirby2005@db:5432/hackaton_db
ENV API_DOMAIN=0.0.0.0
ENV API_PORT=8000
ENV TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
ENV TELEGRAM_WEBHOOK_URL=${TELEGRAM_WEBHOOK_URL}
ENV WEB_APP_URL=${WEB_APP_URL}

# Установка supervisord для управления процессами
RUN apt-get update && apt-get install -y supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Запуск supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
