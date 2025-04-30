import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from core.router import route_task
from core.interfaces import send_task   # восстановили импорт

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="logs/telegram_bot.log",
    filemode="a"
)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот запущен и работает!")

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        user_query = " ".join(context.args)
        role = route_task(user_query)
        try:
            send_task(role, user_query)
            forward_msg = "📨 Передал задачу в очередь, ожидайте результат."
        except Exception as e:
            logging.error(f"send_task failed: {e}", exc_info=True)
            forward_msg = "⚠️ Не удалось отправить задачу в очередь, попробуйте позже."

        response = (
            f"🧠 Задача принята: \"{user_query}\"\n"
            f"🔀 Определена компетенция: *{role}*\n"
            f"{forward_msg}"
        )
    else:
        response = "❗ Пожалуйста, укажите запрос после команды /ask"

    await update.message.reply_text(response, parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("ask", ask))
    app.run_polling()

if __name__ == "__main__":
    main()
