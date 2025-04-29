import os
import subprocess
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID"))

def start(update: Update, context: CallbackContext):
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
    result = subprocess.run(['uptime', '-p'], capture_output=True, text=True)
    update.message.reply_text(f"🕒 Аптайм сервера:\n{result.stdout.strip()}")

def cpu(update: Update, context: CallbackContext):
    result = subprocess.run("top -bn1 | grep 'Cpu(s)'", shell=True, capture_output=True, text=True)
    update.message.reply_text(f"⚙️ Загрузка CPU:\n{result.stdout.strip()}")

def memory(update: Update, context: CallbackContext):
    result = subprocess.run(['free', '-h'], capture_output=True, text=True)
    update.message.reply_text(f"🧠 Использование памяти:\n{result.stdout.strip()}")

def disk(update: Update, context: CallbackContext):
    result = subprocess.run(['df', '-h'], capture_output=True, text=True)
    update.message.reply_text(f"💽 Использование дисков:\n{result.stdout.strip()}")

def services(update: Update, context: CallbackContext):
    result = subprocess.run(['systemctl', 'list-units', '--type=service', '--state=running', '--no-pager'], capture_output=True, text=True)
    services = '\n'.join(result.stdout.strip().split('\n')[:20])
    update.message.reply_text(f"🧩 Активные systemd-сервисы (первые 20):\n{services}")

def processes(update: Update, context: CallbackContext):
    result = subprocess.run("ps aux --sort=-%mem | head -n 10", shell=True, capture_output=True, text=True)
    update.message.reply_text(f"📈 Топ процессов по памяти:\n{result.stdout.strip()}")

def restart_service(update: Update, context: CallbackContext):
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
    main()
