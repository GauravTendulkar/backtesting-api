
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
from backtesting.backtesting_2 import long_running_2 
from backtesting.backtesting_3 import long_running_3
from backtesting.backtesting_4 import long_running_4
from backtesting.backtesting_5 import long_running_5
from backtesting.backtesting_6 import long_running_6
from backtesting.backtesting_7 import long_running_7
from backtesting.backtesting_8 import long_running_8
from backtesting.backtesting_9 import long_running_9
from backtesting.backtesting_10 import long_running_10
from backtesting.backtesting_11 import long_running_11

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
    result = await run_in_thread(long_running_10, data)
    return result