from dotenv import load_dotenv  # Import load_dotenv
import os

load_dotenv(dotenv_path=".env")


# SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))  # Default to 30 if not set
MONGODB_DATABASE_URL = os.getenv("MONGODB_DATABASE_URL")

JWT_SECRET = os.getenv("BACKEND_JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")


INITIAL_ADMIN_EMAIL_ID =  os.getenv("INITIAL_ADMIN_EMAIL_ID")

DUCKDB_PROCESS_NUMBER : int  = int(os.getenv("DUCKDB_PROCESS_NUMBER"))


DISABLE_DUCKDB_FILE_CREATEION : str = os.getenv("DISABLE_DUCKDB_FILE_CREATEION")

# print("*****************************")
# print("####################")
# print(JWT_SECRET, ALGORITHM , "\n", MONGODB_DATABASE_URL)


# JWT_SECRET = os.getenv("BACKEND_JWT_SECRET")
# ALGORITHM = os.getenv("JWT_ALGORITHM")