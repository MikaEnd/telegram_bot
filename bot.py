import os
import json
import threading
import logging
from dotenv import load_dotenv
import pika
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from core.router import route_task
from core.interfaces import send_task, RABBITMQ_URL, TASK_QUEUE

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

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот запущен и работает!")

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        user_query = " ".join(context.args)
        chat_id = update.effective_chat.id
        role = route_task(user_query)
        try:
            send_task(role, user_query, chat_id)
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

def consume_queue(app):
    parameters = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=TASK_QUEUE, durable=True)
    for method_frame, properties, body in channel.consume(TASK_QUEUE, inactivity_timeout=1):
        if body:
            msg = json.loads(body)
            chat_id = msg.get("chat_id")
            text = msg.get("text")
            # Шаг уточнения деталей
            app.bot.send_message(
                chat_id=chat_id,
                text=f"📝 Я получил задачу: \"{text}\". Пожалуйста, уточните, если нужны детали."
            )
            channel.basic_ack(method_frame.delivery_tag)
    connection.close()

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("ask", ask))

    # Запускаем фоновый поток-подписчик
    consumer_thread = threading.Thread(target=consume_queue, args=(app,), daemon=True)
    consumer_thread.start()

    app.run_polling()

if __name__ == "__main__":
    main()
