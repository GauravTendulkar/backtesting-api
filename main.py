from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
# from functions import timeframe, controller, indicators, backtesting_functions
import time

from fastapi.middleware.cors import CORSMiddleware
# from database import configurations, models
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from datetime import datetime
import os
import re

import tracemalloc
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import partial

from contextlib import asynccontextmanager

from app.routes.router import app_router
from dotenv import load_dotenv
from app.config.files_path import create_folders

# load_dotenv()


# create folder 
create_folders()

def calculate_cpu():

    num_cpus = os.cpu_count()
    if num_cpus >= 14:
        return num_cpus-2
    elif num_cpus >= 12:
        return num_cpus-2
    elif num_cpus >= 10:
        return num_cpus-2
    elif num_cpus >= 8:
        return num_cpus-2
    elif num_cpus >= 6:
        return num_cpus-2
    elif num_cpus >= 4:
        return num_cpus-2
    else :
        return num_cpus
# create workers pool 
# pool_of_process: workers.WorkerPool = None

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     global pool_of_process
#     pool_of_process = workers.WorkerPool(num_workers=4)
#     yield
#     pool_of_process.shutdown()

# app = FastAPI(lifespan=lifespan)
    

app = FastAPI()




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as necessary
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# def create_dir():
#     os.makedirs("Clean_data/1min", exist_ok=True)
#     os.makedirs("Clean_data/newData", exist_ok=True)
#     os.makedirs("Clean_data/RAW_daily_data_tradingview", exist_ok=True)
#     os.makedirs("fastCache", exist_ok=True)
#     os.makedirs("indicator_process", exist_ok=True)
#     os.makedirs("database_duckdb", exist_ok=True)
    
    
# create_dir()


# Read all equations (GET)



@app.get("/backend/api/test")
def get_data():
    start = time.time()
    
    # df = df.to_dict(orient="records")
    print((time.time() - start)/60)
    # return  df # send as JSON
    return {"hello":"world"}









app.include_router(app_router)   


# app.include_router(router, prefix="/backend/api/run-backtesting", tags=["backtesting"])
# app.include_router(oauth_router, prefix="/backend/oauth", tags=["oauth"])
# app.include_router(equation_router, prefix="/backend/equations",  tags=["equation_router"])
# app.include_router(stock_list_router, prefix="/backend/api/stock-list", tags=["stock-list"]) 
# app.include_router(new_user_social, prefix="/backend/api/social-signin", tags=["user-signin"])
# app.include_router(admin_dashboard, prefix="/backend/api/admin-dashboard", tags=["user-signin"])
# app.include_router(likesdislikes, prefix="/backend/api/likes-dislikes", tags=["user-signin"])
# app.include_router(protected, prefix="/backend/api/protected", tags=["user-signin"])
# app.include_router(admin_dashboard_social_role_change, prefix="/backend/api/social-user-role-change", tags=["user-signin"])
# app.include_router(strategy_categories, prefix="/backend/api/strategy_categories", tags=["user-signin"])
# app.include_router(date_range, prefix="/backend/api/date_range", tags=["user-signin"])

