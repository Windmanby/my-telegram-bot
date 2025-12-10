# bot.py
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ---- ПЕРЕМЕННЫЕ ----
TOKEN = os.environ.get("TOKEN")  # токен бота из Render secrets
APP_URL = os.environ.get("APP_URL")  # URL твоего Render сервиса, например https://my-telegram-bot-viie.onrender.com
PORT = int(os.environ.get("PORT", 10000))

# ---- ХЕНДЛЕРЫ ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает! 🎉")

# ---- ОСНОВНАЯ ФУНКЦИЯ ----
async def main():
    # Создаём приложение
    app = Application.builder().token(TOKEN).build()
    
    # Добавляем команду /start
    app.add_handler(CommandHandler("start", start))

    # Инициализация
    await app.initialize()

    # Запуск webhook
    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"{APP_URL}/{TOKEN}"  # URL + токен
    )

    print("✅ Webhook запущен, бот готов к работе")

    # Держим приложение живым
    await app.updater.idle()

# ---- ЗАПУСК ----
if __name__ == "__main__":
    asyncio.run(main())
