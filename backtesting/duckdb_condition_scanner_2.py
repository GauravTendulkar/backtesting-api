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

from functions_duckdb.create_files import CreateFiles
# from functions_duckdb.backtesting_table_creation import BacktestingTable
from functions_duckdb.backtesting_table_creation_2 import BacktestingTable

duckdb_conn = duckdb.connect(database=':memory:')


def duckdb_condition_scanner_2(data, date_ranges):
    print("duckdb_condition_scanner_2")
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
    print(data['exitCollection'])

    

    initial_time = time.perf_counter()
    list_stocks = data['stockList']
    ## check if the stocks files exist in the directory______________________________________
    list_stocks = functions.check_stock_files_if_exists(list_stocks)
    print(list_stocks)
    

    init = time.perf_counter_ns()
    create  = CreateFiles(duckdb_conn= duckdb_conn)
    # print(data['entry'])
    # print(create.raw_data_list)
    print("___________")
    create.accumulate_request_data([data["entry"]], list_stocks)
    create.accumulate_request_data([data["entryPrice"]], list_stocks)
    create.accumulate_request_data([data["quantity"]], list_stocks)
    create.accumulate_request_data([data["exitCollection"]], list_stocks)

    # print(create.raw_data_list)
    print("___________")
    # print(create.unique_indicator_columns)
    print("___________")
    create.check_files_exist()
    # print(files_check.convert_equation_to_([data["entry"]], list_stocks))
    create.check_indicator_exist()
    # print(create.indicator_to_be_created)
    init = time.perf_counter_ns()
    create.create_indicators()

    # print(create.smallest_tf)



    obj = BacktestingTable(stock_list=list_stocks, duckdb_conn=duckdb_conn)
    obj.accumulate_request_data([data["entry"]])
    obj.accumulate_request_data([data["entryPrice"]])
    obj.accumulate_request_data([data["quantity"]])
    obj.accumulate_request_data([data["exitCollection"]])

    

    print((time.perf_counter_ns() - init)/1000/1000)


    start_date = '2020-01-01'
    end_date = '2021-01-01'

    start_date = data['dateRange']['from']
    end_date = data['dateRange']['to']
    
    final_text = f""" 

    WITH 
    {obj.fetch_all_timeframes("SBIN")}
    {obj.accumulate_prepare_columns_for_each_stock(start_date , end_date, "SBIN")}


    {obj.union_all_stock("SBIN")}

    """
    # print(final_text)
#     final_text = f"""
 

#     WITH 
     
 
# '15min_table' AS (
 
#     SELECT
         
# symbol,
# tf,
# datetime,
# "close",
# "sma_250_close"
        
#     FROM read_parquet( 'indicator_process_duckdb/symbol=SBIN/tf=15min/data.parquet' )

    
# ),

    

# "SBIN" AS (

# WITH 

 

    
#             "15_15_=1_close" AS  (
            
#                 WITH 
#                 numbered AS (
#                     SELECT *,
#                         row_number() OVER (PARTITION BY date_trunc('day', datetime) ORDER BY datetime) AS rn,
#                         date_trunc('day', datetime) AS candle_day
#                     FROM "15min_table"
#                     --WHERE datetime BETWEEN '2016-02-28' AND '2026-02-28'
#                     --AND symbol = 'SBIN'
#                 ),
#                 first_candles AS (
#                     SELECT candle_day,
#                         MAX(CASE WHEN rn = 1 THEN close ELSE NULL END) AS close_1,
                        
#                     FROM numbered
#                     GROUP BY candle_day
#                 )

#                 SELECT n.datetime, n.datetime + INTERVAL 15 minute AS "datetime_end",
#                 --n.close, n.rn, f.close_1,
#                 CASE 
#                     WHEN (n.rn > 1) THEN f.close_1 ELSE NULL
#                 END as "15_15_=1_close"

#                 FROM numbered n
#                 JOIN first_candles f ON n.candle_day = f.candle_day
#                 ORDER BY n.datetime

                
#             ),

#             "15_15_-1_sma_250_close" AS  (
            
#                 SELECT 
#                 datetime, 
#                 datetime + INTERVAL 15 minute AS "datetime_end", 
#                 lag("sma_250_close", 1) OVER (ORDER BY datetime) AS "15_15_-1_sma_250_close", 
#                 FROM
#                 "15min_table"
#                 --WHERE datetime BETWEEN '2016-02-28' AND '2026-02-28'
#                 --AND symbol = 'SBIN'
                
#             ),

#             "15_15_0_close" AS  (
            
#                 SELECT 
#                 datetime, 
#                 datetime + INTERVAL 15 minute AS "datetime_end", 
#                 "close" AS "15_15_0_close", 
#                 FROM
#                 "15min_table"
#                 --WHERE datetime BETWEEN '2016-02-28' AND '2026-02-28'
#                 --AND symbol = 'SBIN'
                
#             ),

# OHLC AS (
# SELECT
# DATETIME, 
# SYMBOL,
# close,
# -- Construct YYYYMMDD as integer
# --date_part('year', datetime) * 10000
# --+ date_part('month', datetime) * 100
# --+ date_part('day', datetime) AS date_int,

# -- Construct HHMM as integer
# --date_part('hour', datetime) * 100
# --+ date_part('minute', datetime) AS time_int
# FROM "15min_table"
# --WHERE symbol = 'SBIN'

# ),

# FRESH AS (
# select OHLC.*, 
 

#     "15_15_=1_close",
# "15_15_-1_sma_250_close",
# "15_15_0_close",

# from OHLC
 

#     LEFT JOIN "15_15_=1_close" ON OHLC.DATETIME = "15_15_=1_close".DATETIME
# LEFT JOIN "15_15_-1_sma_250_close" ON OHLC.DATETIME = "15_15_-1_sma_250_close".DATETIME
# LEFT JOIN "15_15_0_close" ON OHLC.DATETIME = "15_15_0_close".DATETIME

# --WHERE OHLC.datetime BETWEEN '2016-02-28' AND '2026-02-28'
# order by OHLC.datetime
# )

# SELECt * FROM FRESH


# )



    

# SELECT * FROM "SBIN"



    
# """    


    
    with open("w_output.txt", "w") as file:
        file.write(final_text)
    init = time.perf_counter_ns()
    obj.create_fast_cache()
    df = duckdb_conn.sql(final_text).df()

    print((time.perf_counter_ns() - init)/1000/1000)

    print(data['dateRange'])

    print(obj.raw_data_group_by_stock)
    # print(df)
    print(df.columns)