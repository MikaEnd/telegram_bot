import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)
from core.router import route_task

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="logs/telegram_bot.log",
    filemode="a"
)

# Команда: /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Статус сервера:\n(будет реализовано)")

# Команда: /cpu
async def cpu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚙️ Загрузка CPU:\n(будет реализовано)")

# Команда: /ask <текст запроса>
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        user_query = " ".join(context.args)
        role = route_task(user_query)
        response = (
            f"🧠 Задача принята: \"{user_query}\"\n"
            f"🔀 Определена компетенция: *{role}*"
        )
    else:
        response = "❗ Пожалуйста, укажите запрос после команды /ask"

    await update.message.reply_text(response, parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("cpu", cpu))
    app.add_handler(CommandHandler("ask", ask))

    app.run_polling()

if __name__ == "__main__":
    main()
