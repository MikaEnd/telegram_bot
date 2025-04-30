# core/router.py

def route_task(text: str) -> str:
    """
    Простейшая маршрутизация: определяем, какой подбот (компетенция) должен выполнить задачу.
    В будущем здесь будет использоваться NLP/ИИ, а пока — ключевые слова.
    """
    text_lower = text.lower()

    if any(word in text_lower for word in ["nginx", "настрой", "html", "бот", "лендинг", "скрипт"]):
        return "developer"
    elif any(word in text_lower for word in ["договор", "юрист", "право", "аренда", "проверить документ"]):
        return "legal"
    elif any(word in text_lower for word in ["найди", "поиск", "собери", "инфо", "аналитику", "исследуй"]):
        return "search"
    else:
        return "manager"  # по умолчанию — не знает кому, оставляет себе
