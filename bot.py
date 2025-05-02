import os
import json
import threading
import logging
import re
from dotenv import load_dotenv
import pika
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from geometry_backend.core.handlers.routing import get_handler_by_competence

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="logs/telegram_bot.log",
    filemode="a"
)

# Команда для проверки статуса
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот запущен и работает!")

# Обработка запроса пользователя
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        user_query = " ".join(context.args)
        chat_id = update.effective_chat.id
        handler = get_handler_by_competence("менеджер")
        if handler:
            reply = await handler.handle(str(chat_id), user_query)
        else:
            reply = "⚠️ Не удалось найти менеджера для маршрутизации задачи."
    else:
        reply = "❗ Пожалуйста, укажите запрос после команды /ask"
    await update.message.reply_text(reply)

# Обработка уточнений (если пользователь отвечает на задачу)
async def handle_clarification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message and "📝 Я получил задачу:" in update.message.reply_to_message.text:
        details = update.message.text
        original = update.message.reply_to_message.text
        m = re.search(r'Я получил задачу: "(.*)"', original)
        task = m.group(1) if m else "<задача>"
        handler = get_handler_by_competence("менеджер")
        if handler:
            reply = await handler.handle(str(update.effective_chat.id), details)
        else:
            reply = f"⚠️ Не удалось найти обработчик для уточнения задачи."
        await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("ask", ask))
    app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, handle_clarification))

    app.run_polling()

if __name__ == "__main__":
    main()
