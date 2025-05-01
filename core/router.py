import os
import requests
from dotenv import load_dotenv

load_dotenv()
DEEPSEEK_URL = os.getenv("DEEPSEEK_URL")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def route_task(text: str) -> str:
    """
    Определяем роль: сначала fallback по ключевым словам,
    включая новые для API, а при необходимости — LLM.
    """
    text_lower = text.lower()

    # Developer: добавлены слова для API
    if any(word in text_lower for word in [
        "nginx", "настрой", "html", "бот", "лендинг", "скрипт",
        "api", "протест", "тест", "health"
    ]):
        return "developer"

    # Legal
    if any(word in text_lower for word in [
        "договор", "юрист", "право", "аренда", "проверить документ"
    ]):
        return "legal"

    # Search
    if any(word in text_lower for word in [
        "найди", "поиск", "собери", "инфо", "аналитику", "исследуй"
    ]):
        return "search"

    # По умолчанию
    return "manager"

    # -- Если нужен LLM, можно раскомментировать ниже --
    """
    try:
        prompt = (
            "Классифицируй запрос на одну из ролей: developer, legal, search, manager.\n"
            f"Текст: \"{text}\"\n"
            "Ответь только ключевым словом роли."
        )
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type":"application/json"}
        payload = {"model":"gpt-4","messages":[{"role":"user","content":prompt}]}
        resp = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=5)
        resp.raise_for_status()
        role = resp.json()["choices"][0]["message"]["content"].strip().lower()
        if role in {"developer","legal","search","manager"}:
            return role
    except:
        pass
    """
