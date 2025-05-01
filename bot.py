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
from core.router import route_task
from core.interfaces import send_task, RABBITMQ_URL, TASK_QUEUE

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
    channel.basic_qos(prefetch_count=1)

    def callback(ch, method, properties, body):
        msg = json.loads(body)
        chat_id = msg["chat_id"]
        text = msg["text"]
        app.bot.send_message(
            chat_id=chat_id,
            text=(
                f"📝 Я получил задачу: \"{text}\".\n"
                "Пожалуйста, уточните, если нужны детали. (ответьте на это сообщение)"
            )
        )
        ch.basic_ack(method.delivery_tag)

    channel.basic_consume(queue=TASK_QUEUE, on_message_callback=callback)
    channel.start_consuming()

async def handle_clarification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message and "📝 Я получил задачу:" in update.message.reply_to_message.text:
        details = update.message.text
        original = update.message.reply_to_message.text
        m = re.search(r'Я получил задачу: "(.*)"', original)
        task = m.group(1) if m else "<задача>"
        await update.message.reply_text(
            f"🛠️ Принял уточнение по задаче \"{task}\":\n\"{details}\"\nЗапускаю исполнителя..."
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("ask", ask))
    app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, handle_clarification))

    consumer_thread = threading.Thread(target=consume_queue, args=(app,), daemon=True)
    consumer_thread.start()

    app.run_polling()

if __name__ == "__main__":
    main()
