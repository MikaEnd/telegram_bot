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

# Публикация задачи в очередь RabbitMQ
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
TASK_QUEUE    = os.getenv("TASK_QUEUE", "tasks")

def send_task(role: str, text: str) -> None:
    parameters = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    # Гарантируем, что очередь существует
    channel.queue_declare(queue=TASK_QUEUE, durable=True)
    message = json.dumps({"role": role, "text": text})
    channel.basic_publish(
        exchange="",
        routing_key=TASK_QUEUE,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)  # durable
    )
    connection.close()
