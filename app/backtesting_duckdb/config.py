
import os
from ..config.files_path import SHARED_FILES_PATH, UNSHARED_FILES_PATH
from ..config import env

NO_OF_DUCKDB_FILE = env.DUCKDB_PROCESS_NUMBER

RAW_FILE_EXTENSION = "parquet"

DUCKDB_FILE_PATH = f"{UNSHARED_FILES_PATH}/database_duckdb"

STOCK_LIST_LOAD_BALANCING_PATH = f"{UNSHARED_FILES_PATH}/load_balacing_stock_per_duckdb_file"
os.makedirs(STOCK_LIST_LOAD_BALANCING_PATH, exist_ok=True)

STOCK_LIST_LOAD_BALANCING_PATH_SQLLITE = f"{STOCK_LIST_LOAD_BALANCING_PATH}/db_assignments.sqlite"
STOCK_LIST_LOAD_BALANCING_PATH_JSON = f"{STOCK_LIST_LOAD_BALANCING_PATH}/db_assignments.json"

CLEAN_DATA_1MIN = f"{SHARED_FILES_PATH}/Clean_data/1min"
CLEAN_DATA_DAILY = f"{SHARED_FILES_PATH}/Clean_data/RAW_daily_data_tradingview"
CLEAN_NEW_DATA = f"{SHARED_FILES_PATH}/Clean_data/newData"
TEMP_CHUNKS_DIR = f"{SHARED_FILES_PATH}/Clean_data/temp_chunks"




os.makedirs(CLEAN_DATA_1MIN, exist_ok=True)
os.makedirs(CLEAN_DATA_DAILY, exist_ok=True)
os.makedirs(CLEAN_NEW_DATA, exist_ok=True)
os.makedirs(TEMP_CHUNKS_DIR, exist_ok=True)

os.makedirs(DUCKDB_FILE_PATH, exist_ok=True)



