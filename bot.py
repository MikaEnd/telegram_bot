import os
import subprocess
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)

# Настройка логирования
logging.basicConfig(
    filename='logs/telegram_bot.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Команда /start от %s", update.effective_user.id)
    await update.message.reply_text(
        "Привет! Я ManagerBot.\n"
        "Команды:\n"
        "/status — Сводка\n"
        "/services — systemd\n"
        "/processes — топ процессов\n"
        "/restart_service [name] — перезапуск\n"
        "/uptime /cpu /memory /disk"
    )

async def restart_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Команда /restart_service")
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Недостаточно прав для выполнения этой команды.")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Укажите имя сервиса: /restart_service nginx")
        return

    service = context.args[0]
    await update.message.reply_text(f"♻️ Перезапуск `{service}`...", parse_mode='Markdown')

    result = subprocess.run(['sudo', 'systemctl', 'restart', service])
    if result.returncode == 0:
        await update.message.reply_text(f"✅ Успешно перезапущен `{service}`", parse_mode='Markdown')
    else:
        await update.message.reply_text(f"❌ Ошибка при перезапуске `{service}`. Код: {result.returncode}", parse_mode='Markdown')

async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Команда /uptime")
    output = subprocess.getoutput("uptime -p")
    await update.message.reply_text(f"🕒 Аптайм сервера:\n{output}")

async def cpu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Команда /cpu")
    output = subprocess.getoutput("top -bn1 | grep 'Cpu(s)'")
    await update.message.reply_text(f"⚙️ Загрузка CPU:\n{output}")

async def memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Команда /memory")
    output = subprocess.getoutput("free -h")
    await update.message.reply_text(f"🧠 Использование памяти:\n{output}")

async def disk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Команда /disk")
    output = subprocess.getoutput("df -h")
    await update.message.reply_text(f"💽 Использование дисков:\n{output}")

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Команда /services")
    output = subprocess.getoutput("systemctl list-units --type=service --state=running --no-pager")
    await update.message.reply_text(f"🧩 Активные systemd-сервисы (первые 20):\n" + "\n".join(output.splitlines()[:20]))

async def processes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Команда /processes")
    output = subprocess.getoutput("ps aux --sort=-%mem | head -n 10")
    await update.message.reply_text(f"📈 Топ процессов по памяти:\n{output}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await uptime(update, context)
    await cpu(update, context)
    await memory(update, context)
    await disk(update, context)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("uptime", uptime))
    app.add_handler(CommandHandler("cpu", cpu))
    app.add_handler(CommandHandler("memory", memory))
    app.add_handler(CommandHandler("disk", disk))
    app.add_handler(CommandHandler("services", services))
    app.add_handler(CommandHandler("processes", processes))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("restart_service", restart_service))

    logger.info("✅ Бот запущен!")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception("❌ Ошибка при запуске бота: %s", e)
