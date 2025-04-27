#!/bin/bash

REMOTE_ROOT="Python projects"
LOCAL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_NAME="$(basename "$LOCAL_DIR")"
REMOTE_DIR="$REMOTE_ROOT/$PROJECT_NAME"

# Проверяем корневую папку на Диске
if ! rclone lsd "AI_Telegram_Bot:/$REMOTE_ROOT" &>/dev/null; then
    echo "ℹ️ Папка '$REMOTE_ROOT' не найдена, создаём..."
    rclone mkdir "AI_Telegram_Bot:/$REMOTE_ROOT"
fi

echo "
1 → Загрузить с Яндекс.Диска на ВМ (перезапись локальной папки)
2 → Выгрузить с ВМ на Яндекс.Диск (перезапись удалённой папки)
ESC → Отмена
"
read -n 1 -p "Выберите действие (1/2): " choice
echo ""

case $choice in
    1)
        echo "🔄 Загрузка '$REMOTE_DIR' на ВМ..."
        rclone sync "AI_Telegram_Bot:/$REMOTE_DIR" "$LOCAL_DIR" --progress --delete-after
        ;;
    2)
        # Проверяем папку проекта на Диске перед выгрузкой
        if ! rclone lsd "AI_Telegram_Bot:/$REMOTE_DIR" &>/dev/null; then
            echo "ℹ️ Папка '$REMOTE_DIR' не найдена, создаём..."
            rclone mkdir "AI_Telegram_Bot:/$REMOTE_DIR"
        fi
        echo "🔄 Выгрузка '$LOCAL_DIR' на Яндекс.Диск..."
        rclone sync "$LOCAL_DIR" "AI_Telegram_Bot:/$REMOTE_DIR" --progress --delete-after
        ;;
    $'\e')
        echo "🚫 Отмена."
        exit 0
        ;;
    *)
        echo "❌ Неверный выбор. Используйте 1, 2 или ESC."
        exit 1
        ;;
esac

echo "✅ Готово! Логи: $LOCAL_DIR/sync.log"
