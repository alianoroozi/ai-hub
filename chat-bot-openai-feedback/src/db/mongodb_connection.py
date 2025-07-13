from pymongo import MongoClient

from config import settings
from utils.logger import get_logger

logger = get_logger(__file__)


class MongoDBConnection:
    def __init__(self):
        self.client = MongoClient(settings.MONGO_URI)
        self.collection = self.client.chat_cli_db.chat_log

    def insert(self, record):
        try:
            self.collection.insert_one(record)
            return True
        except Exception as e:
            logger.exception(f"Error inserting to MongoDB: {str(e)}")
            return False

    def close(self):
        self.client.close()


mongodb_client = MongoDBConnection()
