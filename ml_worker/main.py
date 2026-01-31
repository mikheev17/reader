import os
import pika
import time
import logging
from uuid import UUID

from database import update_task_status

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
# Настройка логирования

RM_HOST = os.environ.get("RM_HOST", "rabbitmq")
RM_PORT = int(os.environ.get("RM_PORT", "5672"))
RM_USER = os.environ.get("RM_USER", "rmuser")
RM_PASS = os.environ.get("RM_PASS", "rmpassword")
RM_VHOST = os.environ.get("RM_VHOST", "/")

connection_params = pika.ConnectionParameters(
    host=RM_HOST,
    port=RM_PORT,
    virtual_host=RM_VHOST,
    credentials=pika.PlainCredentials(username=RM_USER, password=RM_PASS),
    heartbeat=30,
    blocked_connection_timeout=2
)

connection = pika.BlockingConnection(connection_params)
channel = connection.channel()
queue_name = 'ml_task_queue'
channel.queue_declare(queue=queue_name)  # Создание очереди (если не существует)


# Функция, которая будет вызвана при получении сообщения
def callback(ch, method, properties, body):
    task_id_str = body.decode("utf-8").strip()
    logger.info(f"Received task_id: '{task_id_str}'")
    try:
        task_id = UUID(task_id_str)
    except ValueError:
        logger.error(f"Invalid task_id in message: '{task_id_str}'")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return
    try:
        updated = update_task_status(task_id, "PROCESSING")
        if not updated:
            logger.warning(f"Task not found: {task_id}")
        time.sleep(3)  # Имитация полезной работы
        update_task_status(task_id, "COMPLETED")
        logger.info(f"Task completed: {task_id}")
    except Exception as e:
        logger.exception(f"Task failed: {task_id}")
        try:
            update_task_status(task_id, "FAILED", error_message=str(e))
        except Exception:
            logger.exception("Failed to update task status to failed")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

# Подписка на очередь и установка обработчика сообщений
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=False  # Автоматическое подтверждение обработки сообщений
)

logger.info('Waiting for messages. To exit, press Ctrl+C')
channel.start_consuming()