import os
import requests
import paramiko
from core.interfaces import BotHandler
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL = os.getenv("DEEPSEEK_URL", "https://api.deepseek.com/v1/chat/completions")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH")
USERNAME = "avipython"

class FullstackDeveloperHandler(BotHandler):
    def can_handle(self, task_description: str) -> bool:
        keywords = ["установи", "настрой", "сервер", "nginx", "gunicorn", "домен", "docker"]
        return any(word in task_description.lower() for word in keywords)

    def handle(self, task_description: str) -> str:
        try:
            command = self.ask_deepseek(task_description)
            if not command:
                return "❌ Не удалось получить команду от ИИ"

            result = self.run_ssh_command(command)

            return (
                f"🛠️ Фулстек-разработчик получил задачу:\n<code>{task_description}</code>\n\n"
                f"🔧 Выполненная команда:\n<code>{command}</code>\n\n"
                f"📄 Результат:\n<code>{result}</code>"
            )
        except Exception as e:
            return f"❌ Ошибка FullstackHandler: {str(e)}"

    def ask_deepseek(self, task_description: str) -> str:
        prompt = (
            f"Сгенерируй одну исполняемую Linux-команду для задачи:\n{task_description}.\n"
            f"Только команду, без пояснений, без markdown."
        )

        response = requests.post(
            DEEPSEEK_URL,
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    def run_ssh_command(self, command: str) -> str:
        key = paramiko.Ed25519Key.from_private_key_file(SSH_KEY_PATH)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect("localhost", username=USERNAME, pkey=key)

        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        client.close()

        return output if output else error or "Команда выполнена успешно"
