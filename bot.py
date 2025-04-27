import os
import re
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import paramiko
import requests
from dotenv import load_dotenv
from datetime import datetime

# ✅ Импорт менеджера
from bots.manager.manager_bot import ManagerBot

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH", "/home/avipython/.ssh/id_ed25519")
ADMIN_ID = os.getenv("ADMIN_TELEGRAM_ID", "346399418")

# Менеджер задач
manager = ManagerBot()

# Настройка логов
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("/home/avipython/telegram_bot/bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def log_action(user_id: str, action: str, result: str = ""):
    with open("/home/avipython/telegram_bot/actions.log", "a") as f:
        f.write(f"[{datetime.now()}] User:{user_id} | {action}\n")
        if result:
            f.write(f"Результат: {result}\n\n")

def clean_command(raw_command: str) -> str:
    return re.sub(r'```(bash)?|```', '', raw_command).strip()

def execute_ssh_command(command: str) -> str:
    try:
        key = paramiko.Ed25519Key.from_private_key_file(SSH_KEY_PATH)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect("localhost", username="avipython", pkey=key)

        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        client.close()

        return output if output else error or "Команда выполнена успешно"
    except Exception as e:
        return f"SSH error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    log_action(user_id, "Command /start")

    text = (
        "🖥️ Я ИИ-администратор вашего сервера\n\n"
        "Доступные команды:\n"
        "/status - состояние сервера\n"
        "/ask <задача> - передать менеджеру задачу\n\n"
        "Пример:\n/ask настрой Nginx для сайта"
    )
    await update.message.reply_text(text)

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if not context.args:
        log_action(user_id, "Empty /ask command")
        await update.message.reply_text("Введите задачу после /ask")
        return

    question = " ".join(context.args)
    log_action(user_id, f"🧠 Задача менеджеру: {question}")

    try:
        response = manager.handle_user_task(question)
        await update.message.reply_text(response, parse_mode="HTML")
    except Exception as e:
        error_msg = f"❌ Ошибка: {str(e)}"
        log_action(user_id, error_msg)
        await update.message.reply_text(error_msg)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Доступ запрещен")
        return

    log_action(user_id, "Command /status")
    output = execute_ssh_command("df -h && free -h")
    await update.message.reply_text(f"📊 <b>Статус сервера:</b>\n<code>{output}</code>", parse_mode="HTML")

def main():
    try:
        app = Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("ask", ask))
        app.add_handler(CommandHandler("status", status))

        logger.info("Bot starting...")
        app.run_polling()
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
