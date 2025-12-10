import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ===== Настройка логирования =====
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ===== Переменные окружения =====
TOKEN = os.environ.get("BOT_TOKEN")  # токен бота
PORT = int(os.environ.get("PORT", 10000))
APP_URL = os.environ.get("APP_URL", "https://my-telegram-bot-viie.onrender.com")  # URL Render

# ===== Обработчики =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Бот работает ✅")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Вы написали: {update.message.text}")

# Пример обработки голосовых сообщений
async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Голосовое сообщение получено 🎤")

# Пример отложенного напоминания
async def reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = " ".join(context.args)
        await update.message.reply_text(f"Напоминание установлено: {text}")
    else:
        await update.message.reply_text("Используй /reminder текст_напоминания")

# ===== Создаём приложение =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reminder", reminder))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.add_handler(MessageHandler(filters.VOICE, voice_handler))

# ===== Запуск webhook =====
if __name__ == "__main__":
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"{APP_URL}/{TOKEN}"
    )
