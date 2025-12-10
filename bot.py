import os
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)
from dateutil import parser as dateparser

logging.basicConfig(level=logging.INFO)

# Получаем токен и ID из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID"))

PORT = int(os.environ.get("PORT", 10000))  # Render порт


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне голосовое сообщение, и я создам напоминание.")


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.voice:
        return

    text = update.message.caption or update.message.text or getattr(update.message.voice, 'transcription', None)
    if not text:
        await update.message.reply_text("Я не смог распознать текст. Попробуй ещё раз.")
        return

    logging.info(f"Распознанный текст: {text}")

    try:
        reminder_time = dateparser.parse(text, fuzzy=True, dayfirst=True)
    except:
        reminder_time = datetime.now() + timedelta(minutes=1)

    try:
        extracted_date = dateparser.parse(text, fuzzy=True)
        reminder_text = text.replace(str(extracted_date.date()), "").replace(str(extracted_date.time()), "").strip()
    except:
        reminder_text = text.strip()

    if not reminder_text:
        reminder_text = text

    await update.message.reply_text(
        f"Напоминание создано!\n\n📝 Текст: {reminder_text}\n⏰ Время: {reminder_time.strftime('%d.%m.%Y %H:%M')}"
    )

    context.job_queue.run_once(
        send_reminder,
        reminder_time - datetime.now(),
        data={"text": reminder_text},
        chat_id=TELEGRAM_USER_ID
    )


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    await context.bot.send_message(chat_id=context.job.chat_id, text=f"🔔 Напоминание:\n{data['text']}")


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
