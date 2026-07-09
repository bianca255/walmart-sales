import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "walmart_sales")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "sales")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
sales_collection = db[MONGO_COLLECTION]
