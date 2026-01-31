import os
import pika
import logging
from uuid import UUID

from services.crud import (
    update_task_status,
    get_task_by_id,
    get_document_content,
    get_user_english_level,
    create_prediction,
    mark_document_processed,
)
from ollama_client import find_and_translate_words

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

RM_HOST = os.environ.get("RM_HOST", "rabbitmq")
RM_PORT = int(os.environ.get("RM_PORT", "5672"))
RM_USER = os.environ.get("RM_USER", "rmuser")
RM_PASS = os.environ.get("RM_PASS", "rmpassword")
RM_VHOST = os.environ.get("RM_VHOST", "/")

DEFAULT_ENGLISH_LEVEL = "B1"

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
channel.queue_declare(queue=queue_name)


def process_task(task_id: UUID) -> None:
    """
    Get document by task_id, get user english level, ask Gemma to find words
    by level in document, translate them and create prediction.
    """
    task = get_task_by_id(task_id)
    if not task:
        raise ValueError(f"Task not found: {task_id}")
    document_id = task.get("document_id")
    user_id = task.get("user_id")
    if not document_id or not user_id:
        raise ValueError("Task has no document_id or user_id")

    content = get_document_content(UUID(str(document_id)))
    if not content:
        raise ValueError(f"Document not found or deleted: {document_id}")

    english_level = get_user_english_level(UUID(str(user_id))) or DEFAULT_ENGLISH_LEVEL

    items = find_and_translate_words(content, english_level)
    prediction_data = {"words": items, "english_level": english_level}

    create_prediction(task_id, prediction_data)
    mark_document_processed(UUID(str(document_id)))
    logger.info("Created prediction for task %s with %d words", task_id, len(items))


def callback(ch, method, properties, body):
    task_id_str = body.decode("utf-8").strip()
    logger.info("Received task_id: '%s'", task_id_str)
    try:
        task_id = UUID(task_id_str)
    except ValueError:
        logger.error("Invalid task_id in message: '%s'", task_id_str)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return
    try:
        updated = update_task_status(task_id, "PROCESSING")
        if not updated:
            logger.warning("Task not found: %s", task_id)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        process_task(task_id)
        update_task_status(task_id, "COMPLETED")
        logger.info("Task completed: %s", task_id)
    except Exception as e:
        logger.exception("Task failed: %s", task_id)
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