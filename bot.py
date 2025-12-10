import os
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
from dateutil import parser as dateparser

logging.basicConfig(level=logging.INFO)

# Настройки
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID"))  # Твой Telegram ID
TOKEN = os.getenv("BOT_TOKEN")  # Токен бота
PORT = int(os.environ.get("PORT", 10000))  # Render сам даст порт

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь мне голосовое, и я создам напоминание."
    )

# Обработка голосового
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.voice:
        return

    text = update.message.caption or update.message.text or getattr(update.message.voice, "transcription", None)
    if not text:
        await update.message.reply_text("Я не смог распознать текст. Попробуй ещё раз.")
        return

    logging.info(f"Распознанный текст: {text}")

    # Определяем время напоминания
    reminder_time = None
    try:
        reminder_time = dateparser.parse(text, fuzzy=True, dayfirst=True)
    except:
        pass
    if not reminder_time:
        reminder_time = datetime.now() + timedelta(minutes=1)

    # Текст напоминания
    try:
        extracted_date = dateparser.parse(text, fuzzy=True)
        reminder_text = text.replace(str(extracted_date.date()), "").replace(str(extracted_date.time()), "").strip()
    except:
        reminder_text = text.strip()
    if not reminder_text:
        reminder_text = text

    # Подтверждение
    await update.message.reply_text(
        f"Напоминание создано!\n\n📝 Текст: {reminder_text}\n⏰ Время: {reminder_time.strftime('%d.%m.%Y %H:%M')}"
    )

    # Запланировать напоминание
    context.job_queue.run_once(
        send_reminder,
        reminder_time - datetime.now(),
        data={"text": reminder_text},
        chat_id=TELEGRAM_USER_ID
    )

# Функция отправки напоминания
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=f"🔔 Напоминание:\n{data['text']}"
    )

# Основной запуск
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    # Webhook для Render
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"https://my-telegram-bot-viie.onrender.com/{TOKEN}"
    )

if __name__ == "__main__":
    main()
