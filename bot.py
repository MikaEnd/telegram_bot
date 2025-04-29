import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Токен бота
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Я ManagerBot. Список доступных команд: /uptime /disk /memory /cpu')

# Команда /uptime
async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    output = os.popen('uptime -p').read()
    await update.message.reply_text(f"🕒 Аптайм сервера:\n{output}")

# Команда /disk
async def disk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    output = os.popen('df -h').read()
    await update.message.reply_text(f"💽 Использование дисков:\n{output}")

# Команда /memory
async def memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    output = os.popen('free -h').read()
    await update.message.reply_text(f"🧠 Использование памяти:\n{output}")

# Команда /cpu
async def cpu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    output = os.popen('top -bn1 | grep "Cpu(s)"').read()
    await update.message.reply_text(f"⚙️ Загрузка CPU:\n{output}")

# Основной запуск
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("uptime", uptime))
    app.add_handler(CommandHandler("disk", disk))
    app.add_handler(CommandHandler("memory", memory))
    app.add_handler(CommandHandler("cpu", cpu))

    app.run_polling()

if __name__ == '__main__':
    main()
