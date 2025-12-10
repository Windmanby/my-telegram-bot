import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import httpx
import asyncio

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Переменные окружения
TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))  # Render обычно задаёт PORT
APP_URL = os.environ.get("APP_URL", f"https://my-telegram-bot-viie.onrender.com")  # твой URL на Render

# Простая база отложенных сообщений
reminders = []

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот, готов слушать голосовые и текстовые сообщения.")

# Текстовые сообщения
async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.lower().startswith("напомни"):
        # Простейший синтаксис: "Напомни через 10 секунд проверить почту"
        try:
            parts = text.split()
            seconds = int(parts[2])
            message = " ".join(parts[3:])
            reminders.append((asyncio.get_event_loop().time() + seconds, update.effective_chat.id, message))
            await update.message.reply_text(f"Напоминание установлено через {seconds} секунд: {message}")
        except Exception:
            await update.message.reply_text("Не понял формат. Пример: 'Напомни через 10 проверить почту'")
    else:
        await update.message.reply_text(f"Вы написали: {text}")

# Голосовые сообщения (пример)
async def voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    if voice:
        file = await context.bot.get_file(voice.file_id)
        # Сохраняем временно
        path = f"voice_{voice.file_id}.ogg"
        await file.download_to_drive(path)
        # Здесь можно добавить распознавание через сторонний STT сервис
        # Простейший пример: просто отправляем обратно "получили голосовое"
        await update.message.reply_text("Голосовое получено, обработка в разработке 😉")

# Функция проверки отложенных сообщений
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

# Добавляем обработчики
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_message))
app.add_handler(MessageHandler(filters.VOICE, voice_message))

# Запуск webhook на Render
async def main():
    # Запускаем цикл напоминаний
    asyncio.create_task(reminder_loop(app))

    # Запуск webhook
    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"{APP_URL}/{TOKEN}",
        webhook_path=f"/{TOKEN}",
    )

if __name__ == "__main__":
    asyncio.run(main())
