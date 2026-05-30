
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
# from dotenv import load_dotenv  # Import load_dotenv
from ...config import env



# URL = os.getenv("DATABASE_URL")

# Create a new client and connect to the server
client = MongoClient(env.MONGODB_DATABASE_URL, server_api=ServerApi('1')) 













# Dependency to get the database connection
# def get_collection():
#     try:
#         yield collection
#     finally:
#         client.close()  # Close the connection after the request is completed

