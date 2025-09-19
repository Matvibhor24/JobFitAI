from pymongo import AsyncMongoClient
from dotenv import load_dotenv
import os

load_dotenv()
# mongo_client: AsyncMongoClient = AsyncMongoClient("mongodb://admin:admin@mongo:27017")
mongo_client: AsyncMongoClient = AsyncMongoClient(os.getenv("MONGO_URL"))
