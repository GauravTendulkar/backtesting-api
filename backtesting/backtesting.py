
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
from backtesting import duckdb_condition_scanner_2
from backtesting import duckdb_condition_scanner_3
from backtesting import duckdb_condition_scanner_4
from backtesting import duckdb_backtesting_1
from backtesting import duckdb_backtesting_2
from backtesting import duckdb_backtesting_3
import multiprocessing as mp
from multiprocessing import Process, Queue
import duckdb
from contextlib import asynccontextmanager
from functions_duckdb import workers
from functions_duckdb.create_files_1 import CreateFiles
from functions_v1 import data_compression
from functions_duckdb.sqllite_memory_db import TrackingDB
from functions import functions
from functions_duckdb import manage_process_stock_list
from database import stock_list as sl
from fastapi import HTTPException
import fastapi


# from functions
# [4:03 pm, 03/03/2026] G.T.😎: 11 seconds for 170 stocks 12 process
# [4:05 pm, 03/03/2026] G.T.😎: 19 seconds for 180 stocks 6 process
# [4:16 pm, 03/03/2026] G.T.😎: 10 seconds for 170 stocks 16 process
# [4:23 pm, 03/03/2026] G.T.😎: 15 seconds for 170 stocks 8 process
NO_OF_DUCKDB_FILE = 8

stock_list = list(set(sl.stock_list))

manage_process_stock_list_obj = manage_process_stock_list.ManageProcessStockList(stock_list=stock_list, no_of_process = NO_OF_DUCKDB_FILE)

def worker_process(worker_id: int, job_queue: Queue, result_queue: Queue):
    print(f"[Worker {worker_id}] Started | PID: {mp.current_process().pid}")

    duckdb_conn = duckdb.connect(database=f"database_duckdb/stocks_{worker_id}.duckdb", config={"threads": 2
                                                                                                # , "memory_limit": "512MB"
                                                                            #    , "memory_limit": "1GB"
                                                                               })
    # duckdb_conn = duckdb.connect()
    sl_db = TrackingDB()
    create  = CreateFiles(duckdb_conn = duckdb_conn, stock_list=[])
    while True:
        job = job_queue.get()
        # cpu_intensive_work(worker_id)
        print(f"job")
        if job is None:  # shutdown signal
            print(f"[Worker {worker_id}] Shutting down")
            break

        job_id = job["job_id"]
        try:
            data = job["data"]
            date_ranges = data["date_ranges"]
            stock_list = data["stock_list"]
        except:
            pass
        
        if data["mode"] == "entry_exit_backtest":
            try:
                result = duckdb_backtesting_3.duckdb_backtesting_3(data["data"], date_ranges, stock_list,  create, duckdb_conn, sl_db)
            
                result_queue.put({
                    "job_id"    : job_id,
                    "worker_id" : worker_id,
                    "pid"       : mp.current_process().pid,
                    "stock_list" : stock_list,
                    "return_data"    : result,
                    
                })
            except Exception as e:
                print("ERROR", e)
                result_queue.put({
                    "job_id"    : job_id,
                    "worker_id" : worker_id,
                    "pid"       : mp.current_process().pid,
                    "stock_list" : stock_list,
                    "return_data"    : None,
                    
                })

        elif data["mode"] == "condition_scanner":
            try:
                result = duckdb_condition_scanner_4.duckdb_condition_scanner_4( data["data"], date_ranges, stock_list, create, duckdb_conn)
            # print("result", result)
            # pass
        
                result_queue.put({
                    "job_id"    : job_id,
                    "worker_id" : worker_id,
                    "pid"       : mp.current_process().pid,
                    "stock_list" : stock_list,
                    "return_data"    : result,
                    
                })
            except:
                print("ERROR", e)
                result_queue.put({
                    "job_id"    : job_id,
                    "worker_id" : worker_id,
                    "pid"       : mp.current_process().pid,
                    "stock_list" : stock_list,
                    "return_data"    : None,
                    
                })
        elif data["mode"] == "delete_tables":
         
            create.drop_all_table()
            result_queue.put({
                    "job_id"    : job_id,
                    "worker_id" : worker_id,
                    "pid"       : mp.current_process().pid,
                    "return_data"    : None,
                    
                })
                


pool_of_process: workers.WorkerPool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool_of_process
    pool_of_process = workers.WorkerPool(worker = worker_process, num_workers=NO_OF_DUCKDB_FILE)
    yield
    pool_of_process.shutdown()

# app = FastAPI(lifespan=lifespan)
router = APIRouter(lifespan=lifespan)

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

def check_tf_range(tf, start_date, end_date, 
                   date_ranges={1: {'years': 1, 'months': 0, 'days': 0},
                                2: {'years': 1, 'months': 0, 'days': 0},
                                3: {'years': 1, 'months': 0, 'days': 0},
                                5: {'years': 1, 'months': 0, 'days': 0},
                                10: {'years': 1, 'months': 0, 'days': 0},
                                15: {'years': 1, 'months': 0, 'days': 0},
                                30: {'years': 1, 'months': 0, 'days': 0},
                                60: {'years': 1, 'months': 0, 'days': 0},
                                120: {'years': 1, 'months': 0, 'days': 0},
                                180: {'years': 1, 'months': 0, 'days': 0},
                                240: {'years': 1, 'months': 0, 'days': 0},
                                'Daily': {'years': 1, 'months': 0, 'days': 0},
                                'Weekly': {'years': 1, 'months': 0, 'days': 0},
                                'Monthly': {'years': 1, 'months': 0, 'days': 0}}):
    date_format = "%Y-%m-%d"
    try:
        start = datetime.strptime(start_date, date_format)
        end = datetime.strptime(end_date, date_format)
    except ValueError:
        return HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    limit = {
        1 : end - relativedelta(years=date_ranges[1]["years"], months=date_ranges[1]["months"], days=date_ranges[1]["days"] ),
        2 : end - relativedelta(years=date_ranges[2]["years"], months=date_ranges[2]["months"], days=date_ranges[2]["days"] ),
        3 : end - relativedelta(years=date_ranges[3]["years"], months=date_ranges[3]["months"], days=date_ranges[3]["days"] ),
        5 : end - relativedelta(years=date_ranges[5]["years"], months=date_ranges[5]["months"], days=date_ranges[5]["days"] ),
        10 : end - relativedelta(years=date_ranges[10]["years"], months=date_ranges[10]["months"], days=date_ranges[10]["days"] ),
        15 : end - relativedelta(years=date_ranges[15]["years"], months=date_ranges[15]["months"], days=date_ranges[15]["days"] ),
        30 : end - relativedelta(years=date_ranges[30]["years"], months=date_ranges[30]["months"], days=date_ranges[30]["days"] ),
        60 : end - relativedelta(years=date_ranges[60]["years"], months=date_ranges[60]["months"], days=date_ranges[60]["days"] ),
        120 : end - relativedelta(years=date_ranges[120]["years"], months=date_ranges[120]["months"], days=date_ranges[120]["days"] ),
        180 : end - relativedelta(years=date_ranges[180]["years"], months=date_ranges[180]["months"], days=date_ranges[180]["days"] ),
        240 : end - relativedelta(years=date_ranges[240]["years"], months=date_ranges[240]["months"], days=date_ranges[240]["days"] ),
        "Daily" : end - relativedelta(years=date_ranges["Daily"]["years"], months=date_ranges["Daily"]["months"], days=date_ranges["Daily"]["days"] ),
        "Weekly" : end - relativedelta(years=date_ranges["Weekly"]["years"], months=date_ranges["Weekly"]["months"], days=date_ranges["Weekly"]["days"] ),
        "Monthly" : end - relativedelta(years=date_ranges["Monthly"]["years"], months=date_ranges["Monthly"]["months"], days=date_ranges[1]["days"] ),

    }

    # print("tf ************", tf)
    data = {
        "error" : f"Date range exceeds the allowed limit for timeframe '{tf}'. "
                   f"Minimum allowed start date: {limit[tf].strftime('%Y-%m-%d')}",
             "fromDate": limit[tf].strftime('%Y-%m-%d')
    }

    if limit[tf] <= start:
        pass
    else:
        # raise HTTPException(status_code=400, detail="Date range exceeds the allowed limit of 1 year.")
        raise HTTPException(
            status_code=400,
            detail= data
        
                
        )
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
    # print("data", data.keys())
    # print("data", data)
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
            # print("dateRange", date_ranges)
        list_stocks = functions.check_stock_files_if_exists(data['stockList'])
        print("list_stocks", list_stocks)
        manage_process_stock_list_obj.insert_stock_list(list_stocks)
        
    
        result = manage_process_stock_list_obj.stock_key_process_id_value(list_stocks)

    #     tasks = [
    #     pool_of_process.submit_async(1, {
    #         "mode" : "entry_exit_backtest",
    #         "stock_list" : ["INFY", "CIPLA"] ,
    #         "date_ranges" : date_ranges,
    #         "data": data
    #     }),
    #     pool_of_process.submit_async(2, {
    #         "mode" : "entry_exit_backtest",
    #         "stock_list" : ["SBIN", "AARTIIND"] ,
    #         "date_ranges" : date_ranges,
    #         "data": data
    #     })
        
    # ]
        # print("result", result)
        tasks = [ ]
        for i, item in enumerate(result):
            tasks.append(
                pool_of_process.submit_async(int(item), {
            "mode" : "entry_exit_backtest",
            "stock_list" : result[item] ,
            "date_ranges" : date_ranges,
            "data": data
        })
            )
        results = await asyncio.gather(*tasks)
        # print(results)
        Tracking = pd.DataFrame()
        for i, items in enumerate(results):
            if items["return_data"] is None:
                return Tracking
            if "exception" in items["return_data"]:
                raise items["return_data"]["exception"](status_code=items["return_data"]["status_code"], detail=items["return_data"]["detail"])
            
            
            if len(items["return_data"]) > 0:
                if len(Tracking) == 0:
                    Tracking = items["return_data"]
                else:
                    Tracking = pd.concat([Tracking, items["return_data"]], ignore_index=True)

        # print(Tracking)
        return {"data_result": data_compression.compress_json_for_frontend(Tracking.to_json(orient='records'))}
    # result = await run_in_thread(long_running_14, data, date_ranges)
    # result = await run_in_thread(duckdb_backtesting_1.duckdb_backtesting_1, data, date_ranges)
    # result = duckdb_backtesting_2.duckdb_backtesting_2( data, date_ranges)
    # result = duckdb_backtesting_1.duckdb_backtesting_1( data, date_ranges)
    # return result


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
    # result = await run_in_thread(duckdb_condition_scanner_3.duckdb_condition_scanner_3, data, date_ranges)
    # result = duckdb_condition_scanner_3.duckdb_condition_scanner_3( data, date_ranges)
        
        list_stocks = functions.check_stock_files_if_exists(data['stockList'])
        manage_process_stock_list_obj.insert_stock_list(list_stocks)

        result = manage_process_stock_list_obj.stock_key_process_id_value(list_stocks)
        print(result)

        # for i, item in enumerate(pool_of_process.job_queues):
        #     print("pool_of_process", item, len(pool_of_process.job_queues[item]))

        # def peek_queue(worker_id: int) -> list:
        #     with pool_of_process.job_queues[worker_id].mutex:
        #         return list(pool_of_process.job_queues[worker_id].queue)
        # print(1,peek_queue(worker_id = 1))
        

    #     tasks = [
    #     pool_of_process.submit_async(1, {
    #         "mode" : "condition_scanner",
    #         "stock_list" : ["INFY", "CIPLA"] ,
    #         "date_ranges" : date_ranges,
    #         "data": data
    #     }),
    #     pool_of_process.submit_async(2, {
    #         "mode" : "condition_scanner",
    #         "stock_list" : ["SBIN", "AARTIIND"] ,
    #         "date_ranges" : date_ranges,
    #         "data": data
    #     })
        
    # ]
        tasks = [ ]
        for i, item in enumerate(result):
            tasks.append(
                pool_of_process.submit_async(int(item), {
            "mode" : "condition_scanner",
            "stock_list" : result[item] ,
            "date_ranges" : date_ranges,
            "data": data
        })
            )
            

        
        

        results = await asyncio.gather(*tasks)
        Tracking = pd.DataFrame()
        for i, items in enumerate(results):
            if items["return_data"] is None:
                return Tracking
            if "exception" in items["return_data"]:
                raise items["return_data"]["exception"](status_code=items["return_data"]["status_code"], detail=items["return_data"]["detail"])
            
            if len(items["return_data"]) > 0:
                if len(Tracking) == 0:
                    Tracking = items["return_data"]
                else:
                    Tracking = pd.concat([Tracking, items["return_data"]], ignore_index=True)

        # print()
        
        json_data, max_stocks = duckdb_condition_scanner_4.convert_df_to_json_and_maxstocks(Tracking)
    # print(Tracking)
        return {"data_result": data_compression.compress_json_for_frontend(json_data), "max_length" : max_stocks}
    # return result




# @router.post("/delete_tables")
# async def delete_tables(user_email = Depends(jwt_decoder.get_current_user)):  
@router.post("/delete_tables")
async def delete_tables(): 
    print("delete_tables Started")
    # if user_email:
    #         res = configurations.collection_social_user.find_one({"email" : user_email} , {"roles": 1}) 
    #         res = dict(res)
    #         print("res", res)
    #         active_roles = getRoles(res["roles"])
    #         if "admin" in active_roles:
    #             print("admin")
    
    
    tasks = [ ]
    for i in range(1, NO_OF_DUCKDB_FILE+1):
        tasks.append(
            pool_of_process.submit_async(i, {
        "mode" : "delete_tables",
                    
        }))
    await asyncio.gather(*tasks)
    print("delete_tables Ended")

    