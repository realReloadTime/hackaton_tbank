import logging
from typing import Dict

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Веб-приложение FastAPI для обработки вебхуков
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)

# Глобальная переменная для хранения состояния бота (можно заменить на Redis в продакшене)
bot_data: Dict[str, Dict] = {}


@app.post("/telegram-webhook")
async def handle_telegram_webhook(request: Request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return {"status": "ok"}


@app.post("/webhook")
async def handle_webhook(request: Request):
    """
    Обработчик вебхуков для рассылки уведомлений
    """
    try:
        data = await request.json()
        notifications = data.get("notifications", [])

        if not notifications:
            return {"status": "error", "message": "No notifications provided"}

        # Отправляем уведомления пользователям
        for notification in notifications:
            chat_id = notification.get("chat_id")
            if not chat_id:
                continue

            message = format_notification_message(notification)
            try:
                await bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
                logger.info(f"Notification sent to chat_id: {chat_id}")
            except Exception as e:
                logger.error(f"Failed to send notification to {chat_id}: {str(e)}")

        return {"status": "success", "message": f"{len(notifications)} notifications sent"}

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}


def format_notification_message(notification: Dict) -> str:
    """
    Форматирует сообщение уведомления в HTML
    """
    tonality_emoji = {
        "POSITIVE": "🟢",
        "NEGATIVE": "🔴",
        "NEUTRAL": "⚪"
    }

    value_emoji = {
        1: "🔹",  # LOW
        2: "🔸",  # MEDIUM
        3: "🔺"  # HIGH
    }

    tonality = notification.get("tonality", "NEUTRAL")
    value = notification.get("value", 1)
    regions = ", ".join(notification.get("regions", []))
    tickers = ", ".join(notification.get("tickers", []))

    return (
        f"{tonality_emoji.get(tonality, '⚪')} {value_emoji.get(value, '🔹')} <b>Новость по вашим подпискам</b>\n\n"
        f"<b>Регионы:</b> {regions}\n"
        f"<b>Тикеры:</b> {tickers}\n"
        f"<b>Тональность:</b> {tonality}\n"
        f"<b>Важность:</b> {value}\n\n"
        f"<a href='{settings.WEB_APP_URL}'>Подробнее в веб-приложении</a>"
    )


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Обработчик команды /start
    """
    try:
        username = message.from_user.username
        if not username:
            await message.answer("Пожалуйста, установите username в настройках Telegram")
            return

        chat_id = message.chat.id

        # Регистрируем пользователя через API
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"https://api2.academus-pobeda.ru/users/first_launch",
                    json={"username": username, "chat_id": chat_id},
                    timeout=5  # Таймаут 5 секунд
                ) as response:
                    if response.status == 200:
                        # Создаем клавиатуру с кнопкой
                        builder = InlineKeyboardBuilder()
                        builder.add(types.InlineKeyboardButton(
                            text="Открыть веб-приложение",
                            url=settings.WEB_APP_URL
                        ))

                        await message.answer(
                            "Добро пожаловать в финансовый мониторинг!\n\n"
                            "Вы можете настроить свои подписки и посмотреть новости в веб-приложении:",
                            reply_markup=builder.as_markup()
                        )
                    elif response.status == 208:
                        builder = InlineKeyboardBuilder()
                        builder.add(types.InlineKeyboardButton(
                            text="Открыть веб-приложение",
                            url=settings.WEB_APP_URL
                        ))
                        await message.answer(
                            "Вы уже зарегистрированы! Можете настроить подписки в веб-приложении:",
                            reply_markup=builder.as_markup()
                        )
                    else:
                        error_text = await response.text()
                        logger.error(f"API error: {error_text}")
                        await message.answer("Ошибка при регистрации. Попробуйте позже.")

            except aiohttp.ClientError as e:
                logger.error(f"Connection error: {str(e)}")
                await message.answer("Не удалось подключиться к серверу. Попробуйте позже.")
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                await message.answer("Произошла непредвиденная ошибка. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Error in cmd_start: {str(e)}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")


async def on_startup():
    # Устанавливаем вебхук для Telegram
    webhook_url = f"{settings.TELEGRAM_WEBHOOK_URL}/telegram-webhook"
    await bot.set_webhook(webhook_url)
    logger.info(f"Telegram webhook set to {webhook_url}")


async def on_shutdown():
    """
    Действия при остановке бота
    """
    await bot.delete_webhook()
    logger.info("Webhook deleted")


if __name__ == "__main__":
    import uvicorn

    # Добавляем on_startup в список событий при запуске
    app.add_event_handler("startup", on_startup)
    app.add_event_handler("shutdown", on_shutdown)

    uvicorn.run(app, host='localhost', port=settings.TELEGRAM_PORT)

