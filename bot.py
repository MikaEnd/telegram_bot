import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я ManagerBot.\n"
        "Команды:\n"
        "/status — Сводка\n"
        "/services — systemd\n"
        "/processes — топ процессов\n"
        "/uptime /cpu /memory /disk"
    )

async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    output = os.popen("uptime -p").read()
    await update.message.reply_text(f"🕒 Аптайм сервера:\n{output}")

async def cpu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    output = os.popen("top -bn1 | grep 'Cpu(s)'").read()
    await update.message.reply_text(f"⚙️ Загрузка CPU:\n{output}")

async def memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    output = os.popen("free -h").read()
    await update.message.reply_text(f"🧠 Использование памяти:\n{output}")

async def disk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    output = os.popen("df -h").read()
    await update.message.reply_text(f"💽 Использование дисков:\n{output}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = os.popen("uptime -p").read().strip()
    cpu = os.popen("top -bn1 | grep 'Cpu(s)'").read().strip()
    mem = os.popen("free -h").read().strip()
    disk = os.popen("df -h").read().strip()

    status_message = f"""📊 Статус сервера:

🕒 Аптайм:
{uptime}

⚙️ CPU:
{cpu}

🧠 Память:
{mem}

💽 Диск:
{disk}
"""
    await update.message.reply_text(status_message)

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    output = os.popen("systemctl list-units --type=service --no-pager --state=running | head -n 20").read()
    await update.message.reply_text(f"🧩 Активные systemd-сервисы (первые 20):\n{output}")

async def processes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    output = os.popen("ps aux --sort=-%mem | head -n 10").read()
    await update.message.reply_text(f"📈 Топ процессов по памяти:\n{output}")

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

    app.run_polling()

if __name__ == "__main__":
    main()
