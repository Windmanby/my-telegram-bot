import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Переменные окружения
TOKEN = os.environ.get("BOT_TOKEN")  # Ваш токен
PORT = int(os.environ.get("PORT", 10000))
APP_URL = os.environ.get("APP_URL", "https://my-telegram-bot-viie.onrender.com")  # Ваш URL на Render

# Простая база напоминаний
reminders = []

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Бот работает ✅")

# Текстовые сообщения
async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"Вы написали: {text}")

# Голосовые сообщения
async def voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    if voice:
        file = await context.bot.get_file(voice.file_id)
        path = f"voice_{voice.file_id}.ogg"
        await file.download_to_drive(path)
        await update.message.reply_text("Голосовое получено ✅")

# Цикл напоминаний
async def reminder_loop(application):
    while True:
        now = asyncio.get_event_loop().time()
        for reminder in reminders.copy():
            if reminder[0] <= now:
                chat_id = reminder[1]
                message = reminder[2]
                try:
                    await application.bot.send_message(chat_id, f"⏰ Напоминание: {message}")
                except Exception as e:
                    logging.error(f"Ошибка при отправке напоминания: {e}")
                reminders.remove(reminder)
        await asyncio.sleep(1)

# Создание приложения
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_message))
app.add_handler(MessageHandler(filters.VOICE, voice_message))

# Запуск webhook на Render
async def main():
    asyncio.create_task(reminder_loop(app))
    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"{APP_URL}/{TOKEN}"  # только webhook_url
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
