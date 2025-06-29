from fastapi import FastAPI, Request, APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from functions import timeframe, controller, indicators, backtesting_functions
import time
from datetime import date
from filelock import FileLock
import concurrent.futures
from fastapi.middleware.cors import CORSMiddleware
from database import configurations, models
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from datetime import datetime
import os
import re
from database.auth import oauth_router
from database.equations import equation_router
import tracemalloc
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import partial
from backtesting.backtesting import router
from database.stock_list import stock_list_router
from database.new_user import new_user_social
from admin_dashboard.admin_requests  import admin_dashboard
from database.likesdislikes import likesdislikes
from database.verifytoken import protected
from admin_dashboard.user_role_manager import admin_dashboard_social_role_change
from database.strategy_categories import strategy_categories



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
    

app = FastAPI()




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as necessary
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


def create_dir():
    os.makedirs("Clean_data/1min", exist_ok=True)
    os.makedirs("Clean_data/newData", exist_ok=True)
    os.makedirs("Clean_data/RAW_daily_data_tradingview", exist_ok=True)
    os.makedirs("fastCache", exist_ok=True)
    os.makedirs("indicator_process", exist_ok=True)
    
create_dir()


# Read all equations (GET)



@app.get("/data")
def get_data():
    start = time.time()
    df = pd.read_parquet("indicator_process/COALINDIA_1min.parquet")
    df = df.to_dict(orient="records")
    print((time.time() - start)/60)
    return  df # send as JSON
    return {"hello":"world"}




@router.post("/test")
async def root_1(request: Request):
    # body = await request.json()
    # print(body["entry"])
    # my_list = body["mylist"]
    # df = pd.read_csv("indicator_process/"+str(my_list[0]) +"_15min.csv",low_memory=False,parse_dates=['datetime'],index_col=['datetime'])
    
    abc = [["AARTIIND", 60, ["sma", "close", 25]],
           ["AARTIIND", 60, ["sma", "close", 15]],
           ["AARTIIND", 60, ["sma", "close", 5]],
           ["AARTIIND", 30, ["sma", "close", 25]],
           ["AARTIIND", 30, ["sma", "close", 15]],
           ["AARTIIND", 30, ["sma", "close", 5]],
           ["AARTIIND", 15, ["sma", "close", 50]],
           ["AARTIIND", 15, ["sma", "close", 15]],
           ["AARTIIND", 15, ["sma", "close", 5]],
           ["AARTIIND", 15, ["sma", "close", 13]]]
    stocks, timeframes, params = zip(*abc)
    # print(stocks)
    t = time.time()
    with concurrent.futures.ProcessPoolExecutor(calculate_cpu()) as executor:
        
        executor.map(controller.apply_indicators, stocks, timeframes, params)

    # with concurrent.futures.ProcessPoolExecutor(16) as executor:
        
    #     executor.map(controller.change_into_any_timeframe, stocks, timeframes)
    print((time.time() - t)/60)

    return{"Hello":"World"}







    


app.include_router(router, prefix="/backend/api/run-backtesting", tags=["backtesting"])
app.include_router(oauth_router, prefix="/backend/oauth", tags=["oauth"])
app.include_router(equation_router, prefix="/backend/equations",  tags=["equation_router"])
app.include_router(stock_list_router, prefix="/backend/api/stock-list", tags=["stock-list"]) 
app.include_router(new_user_social, prefix="/backend/api/social-signin", tags=["user-signin"])
app.include_router(admin_dashboard, prefix="/backend/api/admin-dashboard", tags=["user-signin"])
app.include_router(likesdislikes, prefix="/backend/api/likes-dislikes", tags=["user-signin"])
app.include_router(protected, prefix="/backend/api/protected", tags=["user-signin"])
app.include_router(admin_dashboard_social_role_change, prefix="/backend/api/social-user-role-change", tags=["user-signin"])
app.include_router(strategy_categories, prefix="/backend/api/strategy_categories", tags=["user-signin"])

