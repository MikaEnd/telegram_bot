import os
import requests
from dotenv import load_dotenv

load_dotenv()
DEEPSEEK_URL = os.getenv("DEEPSEEK_URL")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def route_task(text: str) -> str:
    """
    Простейшая классификация по ключевым словам, включая API.
    """
    text_lower = text.lower()

    # Developer: добавлены слова для API
    if any(w in text_lower for w in [
        "nginx", "настрой", "html", "бот", "лендинг", "скрипт",
        "api", "протест", "тест", "health"
    ]):
        return "developer"

    # Legal
    if any(w in text_lower for w in [
        "договор", "юрист", "право", "аренда", "проверить документ"
    ]):
        return "legal"

    # Search
    if any(w in text_lower for w in [
        "найди", "поиск", "собери", "инфо", "аналитику", "исследуй"
    ]):
        return "search"

    # По умолчанию
    return "manager"
