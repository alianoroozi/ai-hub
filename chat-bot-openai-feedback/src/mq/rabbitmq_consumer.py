import sys

from mq.rabbitmq_connection import RabbitMQConnection
from utils.logger import get_logger

logger = get_logger(__file__)


def consume_from_rabbitmq(queue_name: str):
    """
    Consume data from a RabbitMQ queue.
    """
    try:
        rabbitmq_conn = RabbitMQConnection()
        # Establish connection
        with rabbitmq_conn:
            channel = rabbitmq_conn.get_channel()

            # Ensure the queue exists
            channel.queue_declare(queue=queue_name, durable=True)

            def callback(ch, method, properties, body):
                logger.info(f"Received {body}")

            channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=True,
            )

            logger.info("Waiting for messages. To exit press CTRL+C")
            channel.start_consuming()

    except Exception as e:
        logger.exception(f"Error consuming from rabbitMQ: {str(e)}")
        raise
    except KeyboardInterrupt:
        logger.info("RabbitMQ consume interrupted.")
        sys.exit(0)


if __name__ == "__main__":
    consume_from_rabbitmq("test_queue")
