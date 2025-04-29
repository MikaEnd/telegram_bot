import os
import subprocess
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID"))

# Настройка логирования
logging.basicConfig(
    filename='logs/telegram_bot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    logger.info("Команда /start от %s", update.effective_user.id)
    update.message.reply_text(
        "Привет! Я ManagerBot.\n"
        "Команды:\n"
        "/status — Сводка\n"
        "/services — systemd\n"
        "/processes — топ процессов\n"
        "/restart_service [name] — перезапуск\n"
        "/uptime /cpu /memory /disk"
    )

def uptime(update: Update, context: CallbackContext):
    logger.info("Команда /uptime")
    result = subprocess.run(['uptime', '-p'], capture_output=True, text=True)
    update.message.reply_text(f"🕒 Аптайм сервера:\n{result.stdout.strip()}")

def cpu(update: Update, context: CallbackContext):
    logger.info("Команда /cpu")
    result = subprocess.run("top -bn1 | grep 'Cpu(s)'", shell=True, capture_output=True, text=True)
    update.message.reply_text(f"⚙️ Загрузка CPU:\n{result.stdout.strip()}")

def memory(update: Update, context: CallbackContext):
    logger.info("Команда /memory")
    result = subprocess.run(['free', '-h'], capture_output=True, text=True)
    update.message.reply_text(f"🧠 Использование памяти:\n{result.stdout.strip()}")

def disk(update: Update, context: CallbackContext):
    logger.info("Команда /disk")
    result = subprocess.run(['df', '-h'], capture_output=True, text=True)
    update.message.reply_text(f"💽 Использование дисков:\n{result.stdout.strip()}")

def services(update: Update, context: CallbackContext):
    logger.info("Команда /services")
    result = subprocess.run(['systemctl', 'list-units', '--type=service', '--state=running', '--no-pager'], capture_output=True, text=True)
    services = '\n'.join(result.stdout.strip().split('\n')[:20])
    update.message.reply_text(f"🧩 Активные systemd-сервисы (первые 20):\n{services}")

def processes(update: Update, context: CallbackContext):
    logger.info("Команда /processes")
    result = subprocess.run("ps aux --sort=-%mem | head -n 10", shell=True, capture_output=True, text=True)
    update.message.reply_text(f"📈 Топ процессов по памяти:\n{result.stdout.strip()}")

def restart_service(update: Update, context: CallbackContext):
    logger.info("Команда /restart_service")
    args = context.args
    if not args:
        update.message.reply_text("⚠️ Укажите имя сервиса: /restart_service nginx")
        return
    service = args[0]
    update.message.reply_text(f"♻️ Перезапуск `{service}`...", parse_mode='Markdown')
    result = subprocess.run(['sudo', 'systemctl', 'restart', service])
    if result.returncode == 0:
        update.message.reply_text(f"✅ Успешно перезапущен `{service}`", parse_mode='Markdown')
    else:
        update.message.reply_text(f"❌ Ошибка при перезапуске `{service}`. Код: {result.returncode}", parse_mode='Markdown')

def status(update: Update, context: CallbackContext):
    uptime(update, context)
    cpu(update, context)
    memory(update, context)
    disk(update, context)

def main():
    logger.info("Запуск бота...")
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("uptime", uptime))
    dp.add_handler(CommandHandler("cpu", cpu))
    dp.add_handler(CommandHandler("memory", memory))
    dp.add_handler(CommandHandler("disk", disk))
    dp.add_handler(CommandHandler("services", services))
    dp.add_handler(CommandHandler("processes", processes))
    dp.add_handler(CommandHandler("restart_service", restart_service))
    dp.add_handler(CommandHandler("status", status))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("❌ Ошибка при запуске бота: %s", e)
