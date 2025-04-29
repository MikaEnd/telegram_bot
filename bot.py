import os
import logging
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.constants import ChatAction

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("logs/telegram_bot.log"),
        logging.StreamHandler()
    ]
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я ManagerBot.\n"
        "Команды:\n"
        "/status — Сводка\n"
        "/services — systemd\n"
        "/processes — топ процессов\n"
        "/restart_service [name] — перезапуск\n"
        "/uptime /cpu /memory /disk"
    )

async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    output = os.popen("uptime -p").read()
    await update.message.reply_text(f"\U0001F552 Аптайм сервера:\n{output}")

async def cpu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    output = os.popen("top -bn1 | grep 'Cpu(s)'").read()
    await update.message.reply_text(f"\u2699\ufe0f Загрузка CPU:\n{output}")

async def memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    output = os.popen("free -h").read()
    await update.message.reply_text(f"\U0001F9E0 Использование памяти:\n{output}")

async def disk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    output = os.popen("df -h").read()
    await update.message.reply_text(f"\U0001F4BD Использование дисков:\n{output}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = os.popen("uptime -p").read().strip()
    cpu = os.popen("top -bn1 | grep 'Cpu(s)'").read().strip()
    mem = os.popen("free -h").read().strip()
    disk = os.popen("df -h").read().strip()

    status_message = f"""\U0001F4CA Статус сервера:

\U0001F552 Аптайм:
{uptime}

\u2699\ufe0f CPU:
{cpu}

\U0001F9E0 Память:
{mem}

\U0001F4BD Диск:
{disk}
"""
    await update.message.reply_text(status_message)

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    output = os.popen("systemctl list-units --type=service --no-pager --state=running | head -n 20").read()
    await update.message.reply_text(f"\U0001F9E9 Активные systemd-сервисы (первые 20):\n{output}")

async def processes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    output = os.popen("ps aux --sort=-%mem | head -n 10").read()
    await update.message.reply_text(f"\U0001F4C8 Топ процессов по памяти:\n{output}")

async def restart_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Доступ запрещён.")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Укажите имя сервиса: /restart_service nginx")
        return

    service = context.args[0]
    await update.message.reply_text(f"♻️ Перезапуск `{service}`...")

    result = os.system(f"sudo systemctl restart {service}")

    if result == 0:
        await update.message.reply_text(f"✅ Сервис `{service}` успешно перезапущен.")

        if service == "telegram_bot":
            chat_id = update.effective_chat.id
            subprocess.Popen([
                "bash", "-c",
                f"sleep 5 && curl -s -X POST https://api.telegram.org/bot{TOKEN}/sendMessage -d chat_id={chat_id} -d text='/status'"
            ])
    else:
        await update.message.reply_text(f"❌ Ошибка при перезапуске `{service}`. Код: {result}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("uptime", uptime))
    app.add_handler(CommandHandler("cpu", cpu))
    app.add_handler(CommandHandler("memory", memory))
    app.add_handler(CommandHandler("disk", disk))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("services", services))
    app.add_handler(CommandHandler("processes", processes))
    app.add_handler(CommandHandler("restart_service", restart_service))

    app.run_polling()

if __name__ == "__main__":
    main()
