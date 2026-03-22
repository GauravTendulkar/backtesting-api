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

def calculate_cpu():

    num_cpus = os.cpu_count() - 1
    if num_cpus < 1:
        num_cpus = 1
    
    return num_cpus

duckdb_conn = duckdb.connect(database=':memory:')
# duckdb_conn.execute("PRAGMA threads=50")

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

def all_candle(stock, column_array, with_condition , start_date, end_date):
    fullText = """ 

"""
    for i in range(len(column_array[stock])):
        t = column_array[stock][i]
        if t[4][0].startswith("="): 
            fullText += candles.candle(15, t[4][0], t[2], stock, t[1], with_condition, '2022-02-28', '2023-02-28')
        else:
            # print(t[4][0])
            fullText += candles.candle(15, int(t[4][0]), t[2], stock, t[1], with_condition, '2022-02-28', '2023-02-28')
        # print(fullText)
        if with_condition != False:
            fullText = fullText + ",\n"
        else:
            fullText = fullText + "\n"
        fullText = str(fullText)
    return fullText

# fullText = all_candle(stock, temp, "name" ,  '2022-02-28', '2023-02-28' )

def return_main(stock, column_array, smallest, start_date, end_date):
    # smallest = 15
    path = "functions_duckdb/indicator_files"
    textFinal = f""" 
        WITH 
        
        {candles.candle(smallest, 0, "H4", stock, "Daily", True, start_date, end_date)},
        {candles.candle(smallest, -1, "close", stock, 15, True, start_date, end_date)},
        {all_candle(stock, column_array, True ,  '2022-02-28', '2023-02-28' )}
        
        OHLC AS (
        SELECT 
            DATETIME, 
            close,
            -- Construct YYYYMMDD as integer
            --date_part('year', datetime) * 10000
            --+ date_part('month', datetime) * 100
            --+ date_part('day', datetime) AS date_int,

            -- Construct HHMM as integer
            date_part('hour', datetime) * 100
            + date_part('minute', datetime) AS time_int
            FROM "{path}/{stock}_{smallest}min.parquet"
        ),



        Fresh AS  (SELECT OHLC.*, --,  "close_=2".DATETIME + INTERVAL 15 minute AS MIN   
        
        {candles.candle(smallest, 0, "H4", stock, "Daily", "name", start_date, end_date)},
        {candles.candle(smallest, -1, "close", stock, 15, "name", start_date, end_date)},
        {all_candle(stock, column_array , "name" ,  '2022-02-28', '2023-02-28' )}

        OHLC.datetime
        from OHLC 
        
        {candles.candle(smallest, 0, "H4", stock, "Daily", False, start_date, end_date)}
        {candles.candle(smallest, -1, "close", stock, 15, False, start_date, end_date)}
        {all_candle(stock, column_array , False ,  '2022-02-28', '2023-02-28' )}
        --LEFT JOIN "close_=1" ON OHLC.DATETIME = "close_=1".DATETIME
        --LEFT JOIN "close_=2" ON OHLC.DATETIME = "close_=2".DATETIME
        --LEFT JOIN "close_=2" ON (OHLC.DATETIME >= "close_=2".DATETIME  AND OHLC.DATETIME < "close_=2".DATETIME_END )
        --LEFT JOIN "close_=2" ON date_trunc('minute', OHLC.datetime) = "close_=2".DATETIME
        WHERE
        --OHLC.datetime BETWEEN '2019-10-30' AND '2024-10-30'
        OHLC.datetime BETWEEN '{start_date}' AND '{end_date}'
        
        ORDER BY OHLC.DATETIME)

        select 
        datetime,
        CASE
            WHEN ((time_int <= 1115 )
            AND ({candles.candle(smallest, -1, "close", stock, 15, "name", start_date, end_date)} > {candles.candle(smallest, 0, "H4", stock, "Daily", "name", start_date, end_date)} ) ) THEN TRUE ELSE FALSE

        END as condition,
        '{stock}' AS stock
        
        from Fresh"""
    return textFinal

def duckdb_condition_scanner_1(data, date_ranges):
    print("duckdb_condition_scanner_1")
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

    

    

    initial_time = time.perf_counter()
    list_stocks = data['stockList']
    ## check if the stocks files exist in the directory______________________________________
    list_stocks = functions.check_stock_files_if_exists(list_stocks)
    print(list_stocks)
    
#________________________________________
    # apply indicators or generator csv files


    fast_cache_list = []
    def combine_fast_cache_list_function(iter_list):
        for i in range(0, len(iter_list)):

            if iter_list[i] not in fast_cache_list:
                fast_cache_list.append(iter_list[i])

    fast_cache = files_check.convert_equation_to_([data["entry"]], list_stocks)
    combine_fast_cache_list_function(fast_cache)


















    # ______________________________________________________________________



    fast_cache = files_check.convert_equation_to_([data["entryPrice"]], list_stocks)
    combine_fast_cache_list_function(fast_cache)
    fast_cache = files_check.convert_equation_to_([data["quantity"]], list_stocks)
    combine_fast_cache_list_function(fast_cache)
    fast_cache = files_check.convert_equation_to_([data["entry"]], list_stocks)
    combine_fast_cache_list_function(fast_cache)
    for x in data["exitCollection"]:
        fast_cache = files_check.convert_equation_to_([x["exit"]], list_stocks)
        combine_fast_cache_list_function(fast_cache)
        fast_cache = files_check.convert_equation_to_([x["exitPrice"]], list_stocks)
        combine_fast_cache_list_function(fast_cache)
    # print("fast_cache_list", fast_cache_list)


    columns_not_exists = controller_duckdb.check_column_present(fast_cache_list)

    # print("columns_not_exists", columns_not_exists)
    for i in range(0, len(columns_not_exists)):
    # controller.apply_indicators(stock, timeframe_value ,shortform_indicator, arr)
        controller_duckdb.apply_indicators(columns_not_exists[i][0], 
                                    columns_not_exists[i][1] ,
                                    columns_not_exists[i][3], 
                                    columns_not_exists[i][4])




    smallest = files_check.get_smallest_tf(fast_cache_list)
    print("smallest", smallest)
    for i in range(0, len(fast_cache_list)):
        fast_cache_list[i][3] = f"{smallest}_{fast_cache_list[i][3]}"
        fast_cache_list[i].append(smallest)
################################################
    fast_cache_dict = {}
    for i in range(len(fast_cache_list)):
        if fast_cache_list[i][0] not in fast_cache_dict:
            fast_cache_dict[fast_cache_list[i][0]]  = []
        fast_cache_dict[fast_cache_list[i][0]].append(fast_cache_list[i])

    
    print(data['dateRange'], data['dateRange']['from'], data['dateRange']['to']) 

    print(fast_cache_dict.keys())
    print(fast_cache_dict)
    initial_time = time.perf_counter()
    # newText = return_main("INFY", 15, data['dateRange']['from'], data['dateRange']['to'])
    # OUTPUT = pd.DataFrame()
    # for i in range(0, len(list_stocks)):
    #     newText = candles.return_main(list_stocks[i], fast_cache_dict, smallest, data['dateRange']['from'], data['dateRange']['to'] )
    #     newText = duckdb_conn.execute(newText).df()
    #     OUTPUT = pd.concat([OUTPUT, newText], ignore_index=True)
    

    # OUTPUT = pl.DataFrame()
    # for i in range(0, len(list_stocks)):
    #     newText = candles.return_main(list_stocks[i], fast_cache_dict, smallest, data['dateRange']['from'], data['dateRange']['to'])
    #     newText = duckdb_conn.execute(newText).pl()  # Use .pl() instead of .df()
    #     OUTPUT = pl.concat([OUTPUT, newText])

#     newText = ""
#     for i in range(0, len(list_stocks)):
#         stock = list_stocks[i]
#         text = f"""
# {candles.return_main(stock, fast_cache_dict, smallest, data['dateRange']['from'], data['dateRange']['to'] )}
#         """
        
#         newText += text
#         newText += "\n"
#         if i <len(list_stocks) -1:
#             # print(i)
#             newText += "UNION ALL"
#             newText += "\n"

#     with open("output.txt", "w") as file:
#         file.write(newText)

    
    
#     OUTPUT = duckdb_conn.execute(newText).pl()
    # print(OUTPUT)

    newText = candles.return_main_data(list_stocks[0], fast_cache_dict, smallest, data['dateRange']['from'], data['dateRange']['to'])
    OUTPUT = duckdb_conn.execute(newText).df()

    print(OUTPUT[["datetime","date_int", "time_int", "start", "end"]])
    print(OUTPUT.columns)
    print("count",len(OUTPUT))

    

    # entry_to_equation(temp, option, smallest)

    entry = backtesting_functions.entry_to_equation([data["entry"]] , None, smallest)

    print(entry)
   # ______________________________________________________________________




    # entry = backtesting_functions.entry_to_equation([data["entry"]] , None, smallest)
    # print("entry")
    # print(entry)
    
    # Tracking = pd.DataFrame()
    # for t in range(len(list_stocks)):
    #     result = run_for_each_stock(date_start, date_end, entry, list_stocks[t], fast_cache_list, smallest)
    #     Tracking = pd.concat([Tracking, result], ignore_index=True)

    

    

    
    # current, peak = tracemalloc.get_traced_memory()
    
    # tracemalloc.stop()
    # memory_check = {
    #     "current_memory": f"{current / 10**6:.2f} MB",
    #     "peak_memory": f"{peak / 10**6:.2f} MB"
    # }
    # print("current_memory",memory_check["current_memory"],"peak_memory", memory_check["peak_memory"])
    
    

    
    
    # Tracking.to_csv("Tracking.csv")



    
   

    
    # json_data, max_stocks = convert_df_to_json_and_maxstocks(Tracking)
    # print("Max stocks at single timestamp:", max_stocks)
    # elapsed_time = time.perf_counter() - initial_time
    # print(elapsed_time)
    # print(f"Elapsed time: {elapsed_time * 1_000:.2f} ms")   # Microseconds
    # print(f"Elapsed time: {elapsed_time * 1_000_000:.2f} µs")   # Microseconds
    # print(f"Elapsed time: {elapsed_time * 1_000_000_000:.2f} ns")  # Nanoseconds
    
    # # return {"data_result":Tracking.to_json(orient='records')}
    # return {"data_result": data_compression.compress_json_for_frontend(json_data), "max_length" : max_stocks}

    
    # # return {"Hello": "World"}