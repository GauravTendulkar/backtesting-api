from fastapi import FastAPI, Request, APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from functions import timeframe, controller, indicators, functions, json_saving, df_saving
from functions_v1 import backtesting_functions, create_files
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
import asyncpg
import psycopg2
from sqlalchemy import create_engine
import pyarrow.dataset as ds
from datetime import datetime
from functions import dictCache

def calculate_cpu():

    num_cpus = os.cpu_count() - 1
    if num_cpus < 1:
        num_cpus = 1
    
    return num_cpus

# async def get_df_from_db(stock, collection_of_cache_name, start, end):
#     conn = await asyncpg.connect(
#         user='myuser', password='mysecretpassword',
#         database='mydb', host='localhost', port=5432
#     )

#     query = f"""
#     SELECT "datetime", "date_number", "time_number", "datetime_number", "close" {collection_of_cache_name}
#     FROM "{stock}_15"
#     --WHERE datetime >= now() - interval '365 day'
#     WHERE DATETIME BETWEEN '{start}' AND '{end}'
#     ORDER BY datetime ASC
#     """

#     rows = await conn.fetch(query)  # fetch returns a list of asyncpg.Record objects
#     await conn.close()

#     # Convert to list of dicts for pandas DataFrame
#     data = [dict(row) for row in rows]
#     df = pd.DataFrame(data)
#     return df

def get_df_from_db(engine, stock, collection_of_cache_name, start, end):
    

    query = f"""
    SELECT "datetime", "date_number", "time_number", "datetime_number", "close" {collection_of_cache_name}
    FROM "{stock}_15"
    --WHERE datetime >= now() - interval '365 day'
    WHERE DATETIME BETWEEN '{start}' AND '{end}'
    ORDER BY datetime ASC
    """

   
    df = pd.read_sql_query(query, engine)
    return df

def get_df_from_part(stock, collection_of_cache_name, start, end):

    c = dictCache.myCache.get(f"{stock}_{start}_{end}_{collection_of_cache_name}")
    if c != None:
        return c

    else:

        start = start.split("-")
        end = end.split("-")

        collection_of_cache_name += ["datetime", "date_number", "time_number", "datetime_number", "close"] 

        dataset_path = f"C:/GauravPersonal/Coding/_Projects/ai-trading-bot/apps/ml-model/combined_df_part/{stock}_15"

        # Specify partitioning='hive' to read partition columns from folder names
        dataset = ds.dataset(dataset_path, format='parquet', partitioning='hive')

        # Now you can filter on partition columns
        # filters = (ds.field('year') >= 2024) & (ds.field('month') >= 4) &  (ds.field('year') <= 2025) & (ds.field('month') <= 1)
        filters = (ds.field('datetime') >= datetime(int(start[0]), int(start[1]), int(start[2]))) & (ds.field('datetime') <= datetime(int(end[0]), int(end[1]), int(end[2])))
        columns_to_read = collection_of_cache_name

        table = dataset.to_table(filter=filters, columns=columns_to_read)
        df = table.to_pandas()
        dictCache.myCache.set(f"{stock}_{start}_{end}", df)
        return df

def run_for_each_stock(date_start, date_end, entry, stock, fast_cache_list, smallest, engine):
# def run_for_each_stock(list_stocks, date_start, date_end, csv_import, entry, entryPrice, quantity, exitCollection, tradeSetup, combine_fastCache ):#,  order_dict, combine_fastCache):
    # initial_time = time.perf_counter()
    # initial_length = 1000000
    # Tracking = pd.DataFrame({
    #     'stock': [''] * initial_length,
    #     "condition" : [False] * initial_length,
    #     'entryDateTime': [''] * initial_length,
        
    # })
    
   
    t = 0
    # print("pre_c_entry", entry)
    pre_c_entry = compile(entry, "<string>", "eval")
    


    
    print(stock)
    print(date_start, date_end)
    
    
    date_start = str(date_start)
    date_end = str(date_end)
    

    # if smallest == "Daily" or smallest == "Weekly" or smallest == "Monthly":
    #     path = f"indicator_process/{stock}_{smallest}"
    
    # elif 1 <= smallest & smallest <= 60*5:
    #     path = f"indicator_process/{stock}_{smallest}min"
    # df = df_saving.read_file(path, col= ["datetime", "date_number", "time_number", "datetime_number", "close"] )
    collection_of_cache_name = []
    for i in range(0, len(fast_cache_list)):
        if fast_cache_list[i][0] == stock:
            
            collection_of_cache_name.append(fast_cache_list[i][3])
            # collection_of_cache_name += f' ,"{fast_cache_list[i][3]}" '
    # print(collection_of_cache_name)

    # df = get_df_from_db(engine ,stock, collection_of_cache_name, 
    #                                 f"{date_start[0:4]}-{date_start[4:6]}-{date_start[6:]}", 
    #                                 f"{date_end[0:4]}-{date_end[4:6]}-{date_end[6:]}"
    #                                 )
    
    df = get_df_from_part(stock, collection_of_cache_name, 
                                    f"{date_start[0:4]}-{date_start[4:6]}-{date_start[6:]}", 
                                    f"{date_end[0:4]}-{date_end[4:6]}-{date_end[6:]}")
                                    

    if smallest != "Daily" and smallest != "Weekly" and smallest != "Monthly":
        
        df_time = functions.timeframe_divide_uniqueTime(smallest)
        df_time = df_time[f"uniqueTime_{smallest}"].iloc[-1]
        # df_time = int("".join(df_time.split(":"))) + smallest*100
        df_time = int("".join(df_time.split(":"))) 
    else:
        df_time = None


    
    # try:
    #     date_start_index = df.index.get_loc(df.loc[df["date_number"]  >= date_start].index.tolist()[0])
    #     # print(date_start_index)
    # except:
    #     date_start_index = len(df)-1
    #     # print("ERROR", date_start_index)
    # try:
    #     date_end_index = df.index.get_loc(df.loc[df["date_number"]  <= date_end].index.tolist()[-1]) +1
    #     # print(date_end_index)
    # except:
    #     date_end_index = 0 
    #     # print("ERROR", date_end_inde
    

    date_start_index =0 
    date_end_index = len(df)
    initial_length = date_end_index - date_start_index + 10
    print("initial_length", initial_length)

    stock_array = np.empty(initial_length, dtype=object)
    condition_array = np.zeros(initial_length, dtype=bool)  # efficiently stores booleans
    entryDateTime_array = np.empty(initial_length, dtype=object)
# __________________________________________________________________________

    
    # collection_of_cache_name = ""
    # for i in range(0, len(fast_cache_list)):
    #     if fast_cache_list[i][0] == stock:
            
    #         # collection_of_cache_name.append(fast_cache_list[i][3])
    #         collection_of_cache_name += f' ,"{fast_cache_list[i][3]}" '
    # print(collection_of_cache_name)
    # __________________________________________________________________________

    # conn = await asyncpg.connect(
    #     user='myuser', password='mysecretpassword',
    #     database='mydb', host='localhost', port=5432
    # )

    # query = f"""
    # SELECT "datetime", "date_number", "time_number", "datetime_number", "close", {collection_of_cache_name}
    # FROM "{stock}_15"
    # --WHERE datetime >= now() - interval '365 day'
    # WHERE DATETIME BETWEEN '2023-01-01' AND '2026-01-01'
    # ORDER BY datetime ASC
    # """

    # rows = await conn.fetch(query)  # fetch returns a list of asyncpg.Record objects
    # await conn.close()

    # # Convert to list of dicts for pandas DataFrame
    # data = [dict(row) for row in rows]
    # df = pd.DataFrame(data)


    # df = asyncio.run(get_df_from_db(stock, collection_of_cache_name, 
    #                                 f"{date_start[0:4]}-{date_start[4:6]}-{date_start[6:]}", 
    #                                 f"{date_end[0:4]}-{date_end[4:6]}-{date_end[6:]}"))
    # print(df, df.head())
# ______________________________________________________________________
    
    Tracking_index = 0
    # print(df)
    df_data = df.to_numpy()
    data_column = list(df.columns)
    time_index = data_column.index("time_number")
    date_index = data_column.index("date_number")
    datetime_index = data_column.index("datetime_number")
    # print(time_index,date_index,  datetime_index)
    # print(df_data.shape)

    # fastCache_colum_arr, fastCache_colum_name = create_files.return_fastCache_file(fast_cache_list, stock)

    # df_fastCache_colum_arr = np.stack(copy.deepcopy(df_data), axis=1)
    df_fastCache_colum_arr = df_data
    # print("df_fastCache_colum_arr", df_fastCache_colum_arr[0:5])
    fastCache_colum_name = copy.deepcopy(data_column)
    # print("fastCache_colum_name", fastCache_colum_name)
    # print("fastCache_colum_name type", type(fastCache_colum_name))
    Tracking_index = date_end_index - date_start_index
    
    for i in range(date_start_index, date_end_index):
       
        s = str(int(df_data[i][datetime_index]))
        
            
        try:
            
            if ( eval(pre_c_entry, globals(), locals()) ):
                
                # print("True", i- date_start_index, s)
                stock_array[i- date_start_index] = str(stock)
                condition_array[i- date_start_index] = True
                entryDateTime_array[i- date_start_index] = f"{s[6:8]}-{s[4:6]}-{s[0:4]} {s[8:10]}:{s[10:12]}"
           
            else:
                stock_array[i- date_start_index] = str(stock)
                condition_array[i- date_start_index] = False
                entryDateTime_array[i- date_start_index] = f"{s[6:8]}-{s[4:6]}-{s[0:4]} {s[8:10]}:{s[10:12]}"
                
        except Exception as e:
            # print("Error", Tracking_index, e)
            # print(df_fastCache_colum_arr[i][fastCache_colum_name.index(f"15_{stock}_15_=1_close")])
            # print("index of", fastCache_colum_name.index(f"15_{stock}_15_0_low"))
            stock_array[i- date_start_index] = str(stock)
            condition_array[i- date_start_index] = False
            entryDateTime_array[i- date_start_index] = f"{s[6:8]}-{s[4:6]}-{s[0:4]} {s[8:10]}:{s[10:12]}"
            # break
            pass
            
    # print("entryDateTime_array", entryDateTime_array)
    Tracking = pd.DataFrame({
        "stock": stock_array,
        "condition": condition_array,
        "entryDateTime": entryDateTime_array
    })                        
                
# Exit Exit Exit Exit Exit Exit Exit Exit ________________________________________________
            
    
    
    Tracking = Tracking[:Tracking_index]
    
    # elapsed_time = time.perf_counter() - initial_time
    # print("end")
    # print(elapsed_time)
    # print(f"Elapsed time: {elapsed_time * 1_000:.2f} ms")   # Microseconds
    # print(f"Elapsed time: {elapsed_time * 1_000_000:.2f} µs")   # Microseconds
    # print(f"Elapsed time: {elapsed_time * 1_000_000_000:.2f} ns")  # Nanoseconds
    return Tracking
    

# def execute_backtesting_logic_args(args):
#     return run_for_each_stock(*args)


# import json




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


def condition_scanner_1(data, date_ranges):
    print("condition_scanner_1")
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
    # fast_cache = files_check.convert_equation_to_([data["entryPrice"]], list_stocks)
    # combine_fast_cache_list_function(fast_cache)
    # fast_cache = files_check.convert_equation_to_([data["quantity"]], list_stocks)
    # combine_fast_cache_list_function(fast_cache)
    # fast_cache = files_check.convert_equation_to_([data["entry"]], list_stocks)
    # combine_fast_cache_list_function(fast_cache)
    # for x in data["exitCollection"]:
    #     fast_cache = files_check.convert_equation_to_([x["exit"]], list_stocks)
    #     combine_fast_cache_list_function(fast_cache)
    #     fast_cache = files_check.convert_equation_to_([x["exitPrice"]], list_stocks)
    #     combine_fast_cache_list_function(fast_cache)
    # print("fast_cache_list", fast_cache_list)
    smallest = files_check.get_smallest_tf(fast_cache_list)
    print("smallest", smallest)
    for i in range(0, len(fast_cache_list)):
        fast_cache_list[i][3] = f"{smallest}_{fast_cache_list[i][3]}"
        fast_cache_list[i].append(smallest)
    # print("____________________________________")
    # print("fast_cache_list", fast_cache_list)
    file_path = "wait_for_update"
    lock_path = file_path + ".lock"
    lock = FileLock(lock_path)
    functions.check_tf_range(smallest, data['dateRange']["from"], data['dateRange']["to"], date_ranges)
    with lock:
        pass
    # create_files.create_file(fast_cache_list)
    

    #____________________________________ convert to equation logic
    date_start = backtesting_functions.date_str_to_int(data['dateRange']["from"])
    date_end = backtesting_functions.date_str_to_int(data['dateRange']["to"])
    
    entry = backtesting_functions.entry_to_equation([data["entry"]] , None, smallest)
    print("entry")
    print(entry)
    # entryPrice = backtesting_functions.entry_to_equation([data["entryPrice"]] , None, smallest)
    
    # quantity = backtesting_functions.entry_to_equation([data["quantity"]] , None, smallest)
    

    # exitCollection = []
    # for i in data["exitCollection"]:
       
    #     exitCollection.append({
    #         "exit": backtesting_functions.entry_to_equation([i["exit"]] , None, smallest),
    #                            "exitPrice":backtesting_functions.entry_to_equation([i["exitPrice"]] , None, smallest),
    #                            "label": i["label"]
    #                            })


    # if data["scanCategory"] == "":
    
    #     tradeSetup = "intraday_long"
    # else:
    #     tradeSetup = data["scanCategory"] 
    # initial_time = time.perf_counter()
    engine = create_engine("postgresql+psycopg2://myuser:mysecretpassword@localhost:5432/mydb")
    Tracking = pd.DataFrame()
    for t in range(len(list_stocks)):
        result = run_for_each_stock(date_start, date_end, entry, list_stocks[t], fast_cache_list, smallest, engine)
        Tracking = pd.concat([Tracking, result], ignore_index=True)

    # for i in range(0, len(Tracking)):
    #     if Tracking.loc[Tracking.index[i], 'buysell'] == 'buy':
    #         Tracking.loc[Tracking.index[i], 'pnl'] = (Tracking.loc[Tracking.index[i], 'exit'] - Tracking.loc[Tracking.index[i], 'entry'] )* Tracking.loc[Tracking.index[i], 'quantity']
    #     if Tracking.loc[Tracking.index[i], 'buysell'] == 'sell':
    #         Tracking.loc[Tracking.index[i], 'pnl'] = (Tracking.loc[Tracking.index[i], 'entry'] - Tracking.loc[Tracking.index[i], 'exit'] )* Tracking.loc[Tracking.index[i], 'quantity']

    # elapsed_time = time.perf_counter() - initial_time
    # print(elapsed_time)
    # print(f"Elapsed time: {elapsed_time * 1_000:.2f} ms")   # Microseconds
    # print(f"Elapsed time: {elapsed_time * 1_000_000:.2f} µs")   # Microseconds
    # print(f"Elapsed time: {elapsed_time * 1_000_000_000:.2f} ns")  # Nanoseconds
    
    ##  track and delete extra files
    # files_tracking.fastCache_file_tracking_and_deletion(copy.deepcopy(fast_cache_list), unit="Gi", memory_size= 1)
    # column_not_exist = controller.check_column_present(fast_cache_list)
    
    # column_exist = []
    # for i in range(len(fast_cache_list)):
    #     if (fast_cache_list[i] not in column_not_exist 
    #     and fast_cache_list[i][2] != "close" 
    #     and fast_cache_list[i][2] != "high" 
    #     and fast_cache_list[i][2] != "low" 
    #     and fast_cache_list[i][2] != "open"
    #     and fast_cache_list[i][2] != "volume"
    #     and fast_cache_list[i][2] != "datetime"
    #     and fast_cache_list[i][2] != "date_number"
    #     and fast_cache_list[i][2] != "time_number"
    #     and fast_cache_list[i][2] != "datetime_number" ):
            
    #         column_exist.append(fast_cache_list[i])
            
    # files_tracking.stock_column_file_tracking_and_deletion(column_exist , unit="Gi", memory_size= 1)

    
    elapsed_time = time.perf_counter() - initial_time
    print(elapsed_time)
    print(f"Elapsed time: {elapsed_time * 1_000:.2f} ms")   # Microseconds
    print(f"Elapsed time: {elapsed_time * 1_000_000:.2f} µs")   # Microseconds
    print(f"Elapsed time: {elapsed_time * 1_000_000_000:.2f} ns")  # Nanoseconds
    
    # current, peak = tracemalloc.get_traced_memory()
    
    # tracemalloc.stop()
    # memory_check = {
    #     "current_memory": f"{current / 10**6:.2f} MB",
    #     "peak_memory": f"{peak / 10**6:.2f} MB"
    # }
    # print("current_memory",memory_check["current_memory"],"peak_memory", memory_check["peak_memory"])
    
    

    
    
    # Tracking.to_csv("Tracking.csv")



    
   

    
    json_data, max_stocks = convert_df_to_json_and_maxstocks(Tracking)
    print("Max stocks at single timestamp:", max_stocks)
    elapsed_time = time.perf_counter() - initial_time
    print(elapsed_time)
    print(f"Elapsed time: {elapsed_time * 1_000:.2f} ms")   # Microseconds
    print(f"Elapsed time: {elapsed_time * 1_000_000:.2f} µs")   # Microseconds
    print(f"Elapsed time: {elapsed_time * 1_000_000_000:.2f} ns")  # Nanoseconds
    
    # return {"data_result":Tracking.to_json(orient='records')}
    return {"data_result": data_compression.compress_json_for_frontend(json_data), "max_length" : max_stocks}

    
    # # return {"Hello": "World"}