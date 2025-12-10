import os
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
from dateutil import parser as dateparser

logging.basicConfig(level=logging.INFO)

TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID"))  # Ваш ID
TOKEN = os.getenv("BOT_TOKEN")

# Обработчик ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Произошла ошибка: {context.error}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь мне голосовое, и я создам напоминание."
    )

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.voice:
        return

    text = update.message.caption or update.message.text or getattr(update.message.voice, "transcription", None)
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
        f"Напоминание создано!\n\n"
        f"📝 Текст: {reminder_text}\n"
        f"⏰ Время: {reminder_time.strftime('%d.%m.%Y %H:%M')}"
    )

    context.job_queue.run_once(
        send_reminder,
        reminder_time - datetime.now(),
        data={"text": reminder_text},
        chat_id=TELEGRAM_USER_ID
    )

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=f"🔔 Напоминание:\n{data['text']}"
    )

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))

    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)

    application.run_polling()

if __name__ == "__main__":
    main()
