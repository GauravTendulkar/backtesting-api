
from fastapi import FastAPI, Request, APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from functions import timeframe, controller, indicators, backtesting_functions
import time
from database import jwt_decoder
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
from backtesting.backtesting_13 import long_running_13
from backtesting.backtesting_14 import long_running_14
from datetime import datetime, timezone
from backtesting import condition_scanner_1
from backtesting import condition_scanner_2
from backtesting import duckdb_condition_scanner_1

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

def getRoles(roles_data):
    

    if not roles_data:
        return []

    valid_roles = []
    now = datetime.now(timezone.utc)
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    now = datetime.strptime(now, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    print("now", now)
    for role in roles_data:
        if not role.get("isActive", True):
            continue

        limit = role.get("limit", "unlimited")
        print(limit)
        if limit == "limited":
            try:
                end_date = role.get("end_date")
                end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")
                end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                print("end_date", end_date, type(end_date))
                if end_date < now:
                    continue
            except:
                continue

        valid_roles.append(role.get("name"))
    if not valid_roles:
        return []
    return valid_roles

def collect_make_date_range(data):
    temp = {}
    for i in range(0, len(data)):
        for j in range(0, len(data[i]["date_range"])):
            # print(data[i]["date_range"][j])
            if data[i]["date_range"][j]["tf"] not in temp.keys():
                temp[data[i]["date_range"][j]["tf"]] = data[i]["date_range"][j]["range"]
            else:
                tf = data[i]["date_range"][j]["tf"]
                if temp[tf]["years"] < data[i]["date_range"][j]["range"]["years"]:
                    temp[tf]["years"] = data[i]["date_range"][j]["range"]["years"]
                if temp[tf]["months"] < data[i]["date_range"][j]["range"]["months"]:
                    temp[tf]["months"] = data[i]["date_range"][j]["range"]["months"]

                if temp[tf]["days"] < data[i]["date_range"][j]["range"]["days"]:
                    temp[tf]["days"] = data[i]["date_range"][j]["range"]["days"]
    return temp

@router.post("/entry_exit_backtest")
async def root(request: Request, user_email = Depends(jwt_decoder.get_current_user)):  
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
    # date_ranges = []
    if "contentId" not in data.keys() :
        print(False, "contentId" not in data.keys(), data.keys())
    else:

        configurations.collection_strategy_run.insert_one({"contentId": data["contentId"], 
                                                       "link" : data["link"],
                                                       "tradeMode" : data["tradeMode"], 
                                                       "email" : user_email,
        
                                                       "strategy_run_at" : get_datetime_now()})
    
        if user_email:
            res = configurations.collection_social_user.find_one({"email" : user_email} , {"roles": 1}) 
            res = dict(res)
            print("res", res)
            active_roles = getRoles(res["roles"])
            temp = []
            for i in range(0, len(active_roles)):
                temp.append({"role_name" :  active_roles[i]})
            print("active_roles", active_roles)

            date_range_cursor = configurations.collection_date_range.find(
                {"role_name": {"$in": active_roles}}
            )

            date_ranges = list(date_range_cursor)
            date_ranges = collect_make_date_range(date_ranges)
            print("dateRange", date_ranges)
        else:
            active_roles = ["user-logout"]
            date_range_cursor = configurations.collection_date_range.find(
                {"role_name": {"$in": active_roles}}
            )
            date_ranges = list(date_range_cursor)
            date_ranges = collect_make_date_range(date_ranges)
            print("dateRange", date_ranges)

    result = await run_in_thread(long_running_14, data, date_ranges)
    return result


@router.post("/condition_scanner")
async def root(request: Request, user_email = Depends(jwt_decoder.get_current_user)):  
    data = await request.json()


    if "contentId" not in data.keys() :
        print(False, "contentId" not in data.keys(), data.keys())
    else:

        configurations.collection_strategy_run.insert_one({"contentId": data["contentId"], 
                                                       "link" : data["link"], 
                                                       "tradeMode" : data["tradeMode"], 
                                                       "email" : user_email,
                                                       "strategy_run_at" : get_datetime_now()})
        if user_email:
            res = configurations.collection_social_user.find_one({"email" : user_email} , {"roles": 1}) 
            res = dict(res)
            print("res", res)
            active_roles = getRoles(res["roles"])
            temp = []
            for i in range(0, len(active_roles)):
                temp.append({"role_name" :  active_roles[i]})
            print("active_roles", active_roles)

            date_range_cursor = configurations.collection_date_range.find(
                {"role_name": {"$in": active_roles}}
            )

            date_ranges = list(date_range_cursor)
            date_ranges = collect_make_date_range(date_ranges)
            print("dateRange", date_ranges)
        else:
            active_roles = ["user-logout"]
            date_range_cursor = configurations.collection_date_range.find(
                {"role_name": {"$in": active_roles}}
            )
            date_ranges = list(date_range_cursor)
            date_ranges = collect_make_date_range(date_ranges)
            print("dateRange", date_ranges)

    # result = await run_in_thread(condition_scanner_1.condition_scanner_1, data, date_ranges)
    result = await run_in_thread(duckdb_condition_scanner_1.duckdb_condition_scanner_1, data, date_ranges)
    return result