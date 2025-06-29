
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv  # Import load_dotenv

load_dotenv()


uri = os.getenv("DATABASE_URL")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client.stocks_backtesing_data_server

collection = db["equation"]
collection_user = db["users"]
collection_social_user = db["social_user"]
collection_roles = db["roles"]
collection_votes = db["votes"]
collection_strategy_run = db["strategy_run"]

# Dependency to get the database connection
def get_collection():
    try:
        yield collection
    finally:
        client.close()  # Close the connection after the request is completed

# def get_collection_user():
#     try:
#         yield collection_user
#     finally:
#         client.close()