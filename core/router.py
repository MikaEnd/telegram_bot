from core.interfaces import BotHandler

class TaskRouter:
    def __init__(self):
        self.handlers: list[BotHandler] = []

    def add_handler(self, handler: BotHandler):
        self.handlers.append(handler)

    def route(self, task_description: str) -> str:
        for handler in self.handlers:
            if handler.can_handle(task_description):
                return handler.handle(task_description)
        return "❌ Не найден подходящий исполнитель для задачи."
