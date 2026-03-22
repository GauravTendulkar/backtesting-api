from fastapi import FastAPI, Request, APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from functions import timeframe, controller, indicators, functions, json_saving, df_saving
# from functions_v1 import backtesting_functions, create_files
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
import math
from cache_manager import cache_ts, cache_for_nparray

from functions.thread_safe_LRU_cache import ThreadSafeLRUCache

import redis_cache  
import json
import copy
from functions_v1 import files_check, files_tracking, data_compression
from functions import dictCache

from functions_duckdb import controller as controller_duckdb
from functions_duckdb import candles
import duckdb
import polars as pl
from functions_duckdb import backtesting_functions

from functions_duckdb.create_files_1 import CreateFiles
from functions_duckdb.backtesting_table_creation_4 import BacktestingTable
from functions_duckdb.backtesting_functions_1 import BackTestingFunction
from functions_duckdb.functions import check_tf_range as f_ddb_check_tf_range

# from functions_duckdb.duckdb_obj_pool import duckdb_conn

# duckdb_conn = duckdb.connect(database="database_duckdb/stocks.duckdb")
# duckdb_conn


# create  = CreateFiles(duckdb_conn = duckdb_conn, stock_list=[])

def convert_df_to_json_and_maxstocks(df):
    # Filter once: rows where condition is True
    df_true = df[df['condition']]

    # Group by 'entryDateTime', aggregate stocks as lists
    grouped = df_true.groupby('entryDateTime')['stock'].agg(list).sort_index()

    # Get ALL unique timestamps (including those with no stocks meeting condition)
    all_times = df['entryDateTime'].sort_values().unique()

    # Prepare full results including timestamps with empty stocks list
    # For fast lookup, convert grouped to dict
    grouped_dict = grouped.to_dict()

    result = []
    max_stocks = 0
    for ts in all_times:
        stocks_list = grouped_dict.get(ts, [])
        max_stocks = max(max_stocks, len(stocks_list))
        result.append({'timeStamp': ts, 'stocks': stocks_list})

    # JSON stringify once
    json_str = json.dumps(result, indent=2)

    return json_str, max_stocks

# using database_duckdb/stocks.duckdb
def duckdb_condition_scanner_4(data, date_ranges,stock_list, create, duckdb_conn):
    print("duckdb_condition_scanner_4")
    # print("____________________") 
    # print(data['stockList']) 
    # print("____________________") 
    # print(data['dateRange']) 
    # print("____________________") 
    # print(data['entry']) 
    # print("____________________") 
    # print(data['entryPrice'])  
    # print("____________________") 
    # print(data['quantity']) 
    # print("____________________") 
    # print(data['exitCollection']) 
    # print("____________________")  

    # print(data['entry'])
    # print(data['entryPrice'])
    # print(data['quantity'])
    # print(data['exitCollection'])
    init_all = time.perf_counter_ns()
    

    # initial_time = time.perf_counter()
    # list_stocks = data['stockList']
    list_stocks = stock_list
    ## check if the stocks files exist in the directory______________________________________
    list_stocks = functions.check_stock_files_if_exists(list_stocks)
    print(list_stocks)
    

    btf_obj = BackTestingFunction(stock_list=list_stocks)
    btf_obj.convert_req_data_to_list([data["entry"]], tag = "entry")
    # btf_obj.convert_req_data_to_list([data["entryPrice"]], tag = "entryPrice")
    # btf_obj.convert_req_data_to_list([data["quantity"]], tag = "quantity")
    # btf_obj.convert_req_data_to_list([data["exitCollection"]], tag = "exitCollection")


    init = time.perf_counter_ns()
    # create  = CreateFiles(duckdb_conn = duckdb_conn, stock_list=list_stocks)
    create.manual_init(duckdb_conn = duckdb_conn, stock_list=list_stocks)
    print("___________")
    create.accumulate_request_data(btf_obj.tags["entry"])
    # create.accumulate_request_data(btf_obj.tags["entryPrice"])
    # create.accumulate_request_data(btf_obj.tags["quantity"])
    # create.accumulate_request_data(btf_obj.tags["exitCollection"])

    # print(create.raw_data_list)
    print("___________")
    # print(create.unique_indicator_columns)
    print("___________")
    # create.check_files_exist()
    # create.check_indicator_exist()
    # create.create_indicators()
    
    init = time.perf_counter_ns()

    create.create_indicators_and_candles()

    


    # print("Time taken", (time.perf_counter_ns() - init)/1000/1000)

    obj = BacktestingTable(stock_list=list_stocks)
    obj.accumulate_request_data(btf_obj.tags["entry"])
    # obj.accumulate_request_data(btf_obj.tags["entryPrice"])
    # obj.accumulate_request_data(btf_obj.tags["quantity"])
    # obj.accumulate_request_data(btf_obj.tags["exitCollection"])
    
    # start_date = '2020-01-01'
    # end_date = '2021-01-01'

    start_date = data['dateRange']['from']
    end_date = data['dateRange']['to']

    # check date range for the role
    print("smallest", obj.smallest_tf)
    date_ranges_output = f_ddb_check_tf_range(obj.smallest_tf, data['dateRange']["from"], data['dateRange']["to"], date_ranges)
    
    if date_ranges_output is not None and "exception" in date_ranges_output:
        
        # print(type(date_ranges_output) == fastapi.exceptions.HTTPException)
        return date_ranges_output
    
   
    btf_obj.find_special_functions([data["entry"]] , "entry")


    obj.collect_depth_zero_uniqueid = btf_obj.collect_depth_zero_uniqueid
    obj.collect_all_cte_tables = btf_obj.collect_all_cte_tables

    final_text = obj.final_query(start_date, end_date)
 
    with open("w_output.txt", "w") as file:
        file.write(final_text)
    init = time.perf_counter_ns()
    df = duckdb_conn.sql(final_text).fetchnumpy()

    print("Time taken generater df", (time.perf_counter_ns() - init)/1000/1000)

    print(data['dateRange'])

    
    print("________________")
    
    print(df.keys())
    
    # print(df)
    

    entry = btf_obj.entry_to_equation([data["entry"]] , None, obj.smallest_tf)



    print("_______________________")
    print(obj.collect_depth_zero_uniqueid)
    # print(obj.create_cte_for_window_functions(15, "SBIN"))
#__________________________________________________________
    print("entry")
    print(entry)
    init = time.perf_counter_ns()
    pre_c_entry = compile(entry, "<string>", "eval") 

    initial_length = len(df["datetime"])
    result = {}
    result["stock"] = np.empty(initial_length, dtype=object)
    result["condition"] = np.zeros(initial_length, dtype=bool)  # efficiently stores booleans
    result["entryDateTime"] = np.empty(initial_length, dtype=object)

    for i in range(0, len(df["datetime"])):
        datetime_str = str(df["datetime"][i])
        # s = {s[6:8]}-{s[4:6]}-{s[0:4]}
        s = f"{datetime_str[8:10]}-{datetime_str[5:7]}-{datetime_str[0:4]} {datetime_str[11:16]}"
        try:
            if eval(pre_c_entry, globals(), locals()):
                
                
                result["stock"][i] = df["symbol"][i]
                result["condition"][i] = True
                result["entryDateTime"][i] = s
            
            else:
                result["stock"][i] = df["symbol"][i]
                result["condition"][i] = False
                result["entryDateTime"][i] = s
        except:
            result["stock"][i] = df["symbol"][i]
            result["condition"][i] = False
            result["entryDateTime"][i] = s

       
    print("Time taken logic",(time.perf_counter_ns() - init)/1000/1000)
    # print(result)
    Tracking = pd.DataFrame(result)
    return Tracking
    # json_data, max_stocks = convert_df_to_json_and_maxstocks(Tracking)
    # print("Max stocks at single timestamp:", max_stocks)
    # print("Time taken total", (time.perf_counter_ns() - init_all)/1000/1000)

    print("Total Time",(time.perf_counter_ns() - init_all)/1000/1000, "ms")
    print("Total Time",(time.perf_counter_ns() - init_all)/1000/1000/1000, "s")
    print(f"Total Time / stock {len(list_stocks)}" ,(time.perf_counter_ns() - init_all)/1000/1000/len(list_stocks), "ms")

    # return {"data_result": data_compression.compress_json_for_frontend(json_data), "max_length" : max_stocks}


    