from datetime import datetime

from pymongo import MongoClient

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


def insert_data_to_mongodb(mongo_uri, db_name, collection_name, data):
    client = None
    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        collection.insert_one(data)
        logger.info("Data inserted successfully")
    except Exception as e:
        logger.exception(f"Error in test CDC: {str(e)}")
    finally:
        if client:
            client.close()


if __name__ == "__main__":
    insert_data_to_mongodb(
        mongo_uri=settings.MONGO_URI,
        db_name="chat_cli_db",
        collection_name="chat_log",
        data={
            "timestamp": datetime.now(),
            "prompt": "Sample user message",
            "response": "Sample response",
            "feedback": "n",
        },
    )
