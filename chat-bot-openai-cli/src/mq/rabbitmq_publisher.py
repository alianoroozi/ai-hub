import pika

from mq.rabbitmq_connection import RabbitMQConnection
from utils.logger import get_logger

logger = get_logger(__file__)


def publish_to_rabbitmq(queue_name: str, data: str):
    """
    Publish data to a RabbitMQ queue.
    """
    try:
        rabbitmq_conn = RabbitMQConnection()
        # Establish connection
        with rabbitmq_conn:
            channel = rabbitmq_conn.get_channel()

            # Ensure the queue exists
            channel.queue_declare(queue=queue_name, durable=True)

            # Delivery confirmation
            channel.confirm_delivery()

            # Send data to the queue
            channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=data,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
            )
            logger.info(f"Published message to queue {queue_name}: {data}")

    except pika.exceptions.UnroutableError:
        logger.warning("Message could not be routed.")
        raise
    except Exception as e:
        logger.exception(f"Error publishing to RabbitMQ: {str(e)}")
        raise


if __name__ == "__main__":
    publish_to_rabbitmq("test_queue", "Hello, World!")
