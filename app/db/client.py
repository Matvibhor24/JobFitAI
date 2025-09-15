from pymongo import AsyncMongoClient

# mongo_client: AsyncMongoClient = AsyncMongoClient("mongodb://admin:admin@mongo:27017")
mongo_client: AsyncMongoClient = AsyncMongoClient(
    "mongodb+srv://matvibhor24_db_user:vibhoratlas@cluster0.vwkhr1s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
