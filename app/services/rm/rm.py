import logging

import pika

from database.config import get_settings

logger = logging.getLogger(__name__)


def _connection_params() -> pika.ConnectionParameters:
    s = get_settings()
    return pika.ConnectionParameters(
        host=s.RM_HOST,
        port=s.RM_PORT,
        virtual_host=s.RM_VHOST,
        credentials=pika.PlainCredentials(username=s.RM_USER, password=s.RM_PASS),
        heartbeat=30,
        blocked_connection_timeout=2,
    )


def send_task(message: str) -> None:
    connection = pika.BlockingConnection(_connection_params())
    channel = connection.channel()
    queue_name = get_settings().ML_QUEUE

    channel.queue_declare(queue=queue_name)

    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=message
    )
    logger.info("Message sent to queue: queue=%s, body_length=%s", queue_name, len(message))
    connection.close()