import sys
import json
from bson import json_util

from db.mongodb_connection import mongodb_client
from mq.rabbitmq_publisher import publish_to_rabbitmq
from config import settings
from utils.logger import get_logger

logger = get_logger(__file__)


def watch():
    try:
        logger.info("Attempting to connect to MongoDB ...")
        # Test connection
        mongodb_client.client.admin.command("ping")
        logger.info("Connected to MongoDB successfully")
        logger.info("Watching for changes ...")

        with mongodb_client.collection.watch(
            [{"$match": {"operationType": {"$in": ["insert"]}}}]
        ) as changes:
            for change in changes:
                logger.info("Change detected in MongoDB.")

                data = json.dumps(change["fullDocument"], default=json_util.default)
                publish_to_rabbitmq(queue_name=settings.RABBITMQ_QUEUE_NAME, data=data)

                logger.info("Detected change published to RabbitMQ.")

    except Exception as e:
        logger.exception(f"Error in CDC: {str(e)}")
    except KeyboardInterrupt:
        logger.info("Shutting down CDC ...")
        mongodb_client.client.close()
        sys.exit(0)


if __name__ == "__main__":
    watch()
