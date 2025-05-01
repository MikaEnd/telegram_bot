import os
import json
import pika
from abc import ABC, abstractmethod

class BotHandler(ABC):
    @abstractmethod
    def can_handle(self, task_description: str) -> bool:
        pass

    @abstractmethod
    def handle(self, task_description: str) -> str:
        pass

# Параметры подключения к RabbitMQ из .env
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
TASK_QUEUE    = os.getenv("TASK_QUEUE", "tasks")

def send_task(role: str, text: str, chat_id: int) -> None:
    """
    Публикуем задачу в очередь RabbitMQ вместе с chat_id,
    чтобы координировать дальнейшие уточнения.
    """
    parameters = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=TASK_QUEUE, durable=True)
    payload = {"role": role, "text": text, "chat_id": chat_id}
    message = json.dumps(payload)
    channel.basic_publish(
        exchange="",
        routing_key=TASK_QUEUE,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()
