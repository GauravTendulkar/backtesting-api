
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
import cProfile
import io
import pstats
from database import configurations
import pytz
from backtesting.backtesting_12 import long_running_12

router = APIRouter()

def calculate_cpu():

    num_cpus = os.cpu_count()
    # if num_cpus >= 14:
    #     return num_cpus-2
    # elif num_cpus >= 12:
    #     return num_cpus-2
    # elif num_cpus >= 10:
    #     return num_cpus-2
    # elif num_cpus >= 8:
    #     return num_cpus-2
    # elif num_cpus >= 6:
    #     return num_cpus-2
    # elif num_cpus >= 4:
    #     return num_cpus-2
    # else :
    return num_cpus
    



# _________________________________________________________________________________________________
thread_pool = ThreadPoolExecutor(max_workers=1)
# process_pool = ProcessPoolExecutor(max_workers=4)

async def run_in_thread(func, *args):
    """Run function in thread pool"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(thread_pool, partial(func, *args))


def get_datetime_now():
    return datetime.strptime(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

@router.post("")
async def root(request: Request):  
    data = await request.json()
    # # print(data)
# Example of running multiple thread tasks
    # tasks = [
    #     run_in_thread(long_running, request),
        
    # ]

    # results = await asyncio.gather(*tasks)

    # return results[0]
# Run CPU-intensive task in thread pool   
    # print(data.keys())
    # print(data["contentId"])
    # print(data["link"])
    # print("email", data["user_email"])
    # print(get_datetime_now())
    configurations.collection_strategy_run.insert_one({"contentId": data["contentId"], 
                                                       "link" : data["link"], 
                                                       "email" : data["user_email"],
                                                       "strategy_run_at" : get_datetime_now()})
    result = await run_in_thread(long_running_12, data)
    return result