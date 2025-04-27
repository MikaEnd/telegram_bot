from core.router import TaskRouter
from bots.fullstack.handler import FullstackDeveloperHandler

class ManagerBot:
    def __init__(self):
        self.router = TaskRouter()
        self._register_bots()

    def _register_bots(self):
        self.router.add_handler(FullstackDeveloperHandler())

    def handle_user_task(self, task_description: str) -> str:
        return self.router.route(task_description)
