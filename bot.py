import subprocess
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

import os

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_TELEGRAM_ID", "0"))

def is_admin(update: Update) -> bool:
    return update.effective_user.id == ADMIN_ID

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

def restart_service(update: Update, context: CallbackContext):
    if not is_admin(update):
        update.message.reply_text("❌ Недостаточно прав для выполнения этой команды.")
        return

    if len(context.args) != 1:
        update.message.reply_text("⚠️ Укажите имя сервиса: /restart_service nginx")
        return

    service = context.args[0]
    update.message.reply_text(f"♻️ Перезапуск `{service}`...", parse_mode='Markdown')

    try:
        result = subprocess.run(
            ["systemctl", "restart", service],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            update.message.reply_text("✅ Успешно")
        else:
            update.message.reply_text(f"❌ Неудачно. Код: {result.returncode}")
    except Exception as e:
        update.message.reply_text(f"❌ Ошибка: {e}")

def services(update: Update, context: CallbackContext):
    result = subprocess.run(
        ["systemctl", "list-units", "--type=service", "--no-pager"],
        stdout=subprocess.PIPE
    )
    output = "\n".join(result.stdout.decode().split("\n")[0:20])
    update.message.reply_text(f"🧩 Активные systemd-сервисы (первые 20):\n{output}")

def processes(update: Update, context: CallbackContext):
    result = subprocess.run(
        ["ps", "aux", "--sort=-%mem"],
        stdout=subprocess.PIPE
    )
    lines = result.stdout.decode().split("\n")[0:10]
    update.message.reply_text("📈 Топ процессов по памяти:\n" + "\n".join(lines))

def uptime(update: Update, context: CallbackContext):
    result = subprocess.run(["uptime", "-p"], stdout=subprocess.PIPE)
    update.message.reply_text(f"🕒 Аптайм сервера:\n{result.stdout.decode()}")

def cpu(update: Update, context: CallbackContext):
    result = subprocess.run(["top", "-bn1"], stdout=subprocess.PIPE)
    cpu_line = [line for line in result.stdout.decode().split("\n") if "Cpu(s)" in line][0]
    update.message.reply_text(f"⚙️ Загрузка CPU:\n{cpu_line}")

def memory(update: Update, context: CallbackContext):
    result = subprocess.run(["free", "-h"], stdout=subprocess.PIPE)
    update.message.reply_text(f"🧠 Использование памяти:\n{result.stdout.decode()}")

def disk(update: Update, context: CallbackContext):
    result = subprocess.run(["df", "-h"], stdout=subprocess.PIPE)
    update.message.reply_text(f"💽 Использование дисков:\n{result.stdout.decode()}")

def status(update: Update, context: CallbackContext):
    uptime(update, context)
    cpu(update, context)
    memory(update, context)
    disk(update, context)

def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("uptime", uptime))
    dp.add_handler(CommandHandler("cpu", cpu))
    dp.add_handler(CommandHandler("memory", memory))
    dp.add_handler(CommandHandler("disk", disk))
    dp.add_handler(CommandHandler("services", services))
    dp.add_handler(CommandHandler("processes", processes))
    dp.add_handler(CommandHandler("restart_service", restart_service, pass_args=True))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
