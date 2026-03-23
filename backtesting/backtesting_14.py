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
# import numba
import redis_cache  
import json
import copy
from functions_v1 import files_check, files_tracking, data_compression


def calculate_cpu():

    num_cpus = os.cpu_count() - 1
    if num_cpus < 1:
        num_cpus = 1
    
    return num_cpus
# @numba.jit()
def run_for_each_stock(date_start, date_end, entry, entryPrice, quantity, exitCollection, tradeSetup, stock, fast_cache_list, smallest):
# def run_for_each_stock(list_stocks, date_start, date_end, csv_import, entry, entryPrice, quantity, exitCollection, tradeSetup, combine_fastCache ):#,  order_dict, combine_fastCache):
    # initial_time = time.perf_counter()
    # initial_length = 10000
    # Tracking = pd.DataFrame({
    #     'stock': [''] * initial_length,
    #     'buysell': [''] * initial_length,
    #     'date': [''] * initial_length,
    #     'entryTime': [''] * initial_length,
    #     'entry': [0.0] * initial_length,
    #     'exit_date': [''] * initial_length,
    #     'exitTime': [''] * initial_length,
    #     'exit': [0.0] * initial_length,
    #     'quantity': [0.0] * initial_length,
    #     'pnl': [0.0] * initial_length,
    #     'sl': [''] * initial_length,
    #     'date_number': [0] * initial_length,
    # })
    
   
    t = 0
    # print("pre_c_entry", entry)
    pre_c_entry = compile(entry, "<string>", "eval")
    pre_c_entryPrice = compile(entryPrice, "<string>", "eval") 
    pre_c_quantity = compile(quantity, "<string>", "eval")
    pre_c_exitCollection = copy.deepcopy(exitCollection)
    for s in range(len(pre_c_exitCollection)):
        pre_c_exitCollection[s]["exit"] = compile(pre_c_exitCollection[s]["exit"], "<string>", "eval")
        
        pre_c_exitCollection[s]["exitPrice"] = compile(pre_c_exitCollection[s]["exitPrice"], "<string>", "eval")
    

    
    if tradeSetup == "long":
        buysell = "buy"
    elif tradeSetup == "short":
        buysell = "sell"
    elif tradeSetup == "intraday_long":
        buysell = "buy"
    elif tradeSetup == "intraday_short":
        buysell = "sell"


    
    print(stock)
    
        
    
    # print("smallest", smallest)
    # df = dict_of_timeframes[smallest]

    if smallest == "Daily" or smallest == "Weekly" or smallest == "Monthly":
        path = f"indicator_process/{stock}_{smallest}"
    
    elif 1 <= smallest & smallest <= 60*5:
        path = f"indicator_process/{stock}_{smallest}min"
    df = df_saving.read_file(path, col= ["datetime", "date_number", "time_number", "datetime_number", "close"] )

    if smallest != "Daily" and smallest != "Weekly" and smallest != "Monthly":
        
        df_time = functions.timeframe_divide_uniqueTime(smallest)
        df_time = df_time[f"uniqueTime_{smallest}"].iloc[-1]
        # df_time = int("".join(df_time.split(":"))) + smallest*100
        df_time = int("".join(df_time.split(":"))) 
    else:
        df_time = None
    # print("df_time", df_time)
    
    try:
        date_start_index = df.index.get_loc(df.loc[df["date_number"]  >= date_start].index.tolist()[0])
        # print(date_start_index)
    except:
        date_start_index = len(df)-1
        # print("ERROR", date_start_index)
    try:
        date_end_index = df.index.get_loc(df.loc[df["date_number"]  <= date_end].index.tolist()[-1]) +1
        # print(date_end_index)
    except:
        date_end_index = 0 
        # print("ERROR", date_end_index)
    
    initial_length = date_end_index - date_start_index + 10
    stock_array       = np.empty(initial_length, dtype=object)
    buysell_array     = np.empty(initial_length, dtype=object)
    date_array        = np.empty(initial_length, dtype=object)
    entryTime_array   = np.empty(initial_length, dtype=object)
    entry_array       = np.zeros(initial_length, dtype=float)
    exit_date_array   = np.empty(initial_length, dtype=object)
    exitTime_array    = np.empty(initial_length, dtype=object)
    exit_array        = np.zeros(initial_length, dtype=float)
    quantity_array    = np.zeros(initial_length, dtype=float)
    pnl_array         = np.zeros(initial_length, dtype=float)
    sl_array          = np.empty(initial_length, dtype=object)
    date_number_array = np.zeros(initial_length, dtype=int)
    
    flag_entry = 0
    flag_exit = 0
    

    
    Tracking_index = 0
    # df_data = df.to_numpy()
    df_data = df.to_numpy()
    # df_data = df_data.tolist()     # changes made
    data_column = list(df.columns)
    time_index = data_column.index("time_number")
    date_index = data_column.index("date_number")
    datetime_index = data_column.index("datetime_number")
    # print("data_column", data_column, df_data)
   
    # i = date_end_index - 1
    

    fastCache_colum_arr, fastCache_colum_name = create_files.return_fastCache_file(fast_cache_list, stock)
    # print("fast_cache_list", fast_cache_list)
    # print("fastCache_colum_arr", fastCache_colum_name[0] , len(fastCache_colum_arr[0]),fastCache_colum_name[1],  len(fastCache_colum_arr[1]))
    # print("fastCache_colum_arr", fastCache_colum_arr)
    # df_fastCache_colum_arr = np.hstack(tuple(fastCache_colum_arr))
    # df_fastCache_colum_arr = fastCache_colum_arr
    df_fastCache_colum_arr = np.stack(fastCache_colum_arr, axis=1)
    # df_fastCache_colum_arr = np.column_stack(fastCache_colum_arr)
    
    # print("fastCache_colum_name", df_fastCache_colum_arr, len(df_fastCache_colum_arr))

    # print("fastCache_colum_name", fastCache_colum_name)

    # df_fastCache_colum_arr = df_fastCache_colum_arr.tolist()    # changes made

   
    smallest_close = ""
    for i in range(len(fast_cache_list)):
        if fast_cache_list[i][0] == stock and smallest == fast_cache_list[i][1] and fast_cache_list[i][2] == "close" and fast_cache_list[i][4][0]  == "0"  and smallest == fast_cache_list[i][5]: 
            smallest_close = fast_cache_list[i][3]  

    # print("smallest_close", smallest_close)

#     context = {  # Only what you need
#     "df_data": df_data,
#     "i": i,
#     "df_fastCache_colum_arr" : df_fastCache_colum_arr,
#     "fastCache_colum_name": fastCache_colum_name,
#     "date_number_array" : date_number_array,
#     "time_index" : time_index,
#     "date_index" : date_index,
    
#     # any other variables needed in your expressions
# }

    is_high_tf      = smallest in {"Daily", "Weekly", "Monthly"}
    is_long_short   = tradeSetup in {"long", "short"}
    is_intraday_mode= not is_high_tf and not is_long_short
    is_intraday_long_short = tradeSetup in {"intraday_long", "intraday_short"}
    # print("***********", is_high_tf, is_long_short, is_intraday_mode, is_intraday_long_short)
    
    for i in range(date_start_index, date_end_index):
        
        time_val = df_data[i][time_index]
        date_val = df_data[i][date_index]
        # print(int(df_data[i][date_index]), functions.count_previous_entry_weekly(date_number_array, int(df_data[i][date_index])) == 0 )
        # local_vars = locals()
        if is_intraday_mode:
            if flag_exit == 0:
                flag_entry = 1
        if (is_high_tf or is_long_short) and flag_entry == 0 and flag_exit == 0:
            flag_entry = 1

        # No entry at last intraday candle
        if is_intraday_mode and time_val == df_time:
            flag_entry = 0

        if flag_entry == 1:
            try:
                local_vars = locals()
                if eval(pre_c_entry, globals(), local_vars):
                    trading_time = f"{int(time_val):06d}"
                    trading_date = f"{int(date_val)}"
                    stock_array[Tracking_index]      = str(stock)
                    buysell_array[Tracking_index]    = str(buysell)
                    date_array[Tracking_index]       = f"{trading_date[0:4]}-{trading_date[4:6]}-{trading_date[6:8]}"
                    entry_array[Tracking_index]      = eval(pre_c_entryPrice, globals(), local_vars)
                    entryTime_array[Tracking_index]  = f"{trading_time[-6:-4]}:{trading_time[-4:-2]}"
                    quantity_array[Tracking_index]   = round(eval(pre_c_quantity, globals(), local_vars), 0)
                    date_number_array[Tracking_index]= int(date_val)
                    flag_entry = 0
                    flag_exit = 1
            except Exception as e:
                # print(i)
                # print("ERROR 2", e)
                pass

        elif flag_exit == 1:
            local_vars = locals()
            for exit_index, exit_item in enumerate(exitCollection):
                if eval(pre_c_exitCollection[exit_index]["exit"], globals(), local_vars):
                    trading_time = f"{int(time_val):06d}"
                    trading_date = f"{int(date_val)}"
                    exit_array[Tracking_index]       = eval(pre_c_exitCollection[exit_index]["exitPrice"], globals(), local_vars)
                    exitTime_array[Tracking_index]   = f"{trading_time[-6:-4]}:{trading_time[-4:-2]}"
                    sl_array[Tracking_index]         = exit_item["label"]
                    exit_date_array[Tracking_index]  = f"{trading_date[0:4]}-{trading_date[4:6]}-{trading_date[6:8]}"
                    flag_exit = 0
                    flag_entry = 0
                    break

            # Universal exit
            if is_intraday_mode and is_intraday_long_short and int(str(int(time_val))) == df_time and flag_exit == 1:
                trading_time_temp = f"{int(time_val):06d}"
                trading_date = f"{int(date_val)}"
                col_idx = fastCache_colum_name.index(smallest_close)
                exit_array[Tracking_index]     = float(df_fastCache_colum_arr[i][col_idx])
                exitTime_array[Tracking_index] = f"{trading_time_temp[-6:-4]}:{trading_time_temp[-4:-2]}"
                # print("Universal exit",smallest_close,  float(df_fastCache_colum_arr[i][col_idx]), trading_date, trading_time_temp)
                sl_array[Tracking_index]       = "universal exit"
                exit_date_array[Tracking_index]= f"{trading_date[0:4]}-{trading_date[4:6]}-{trading_date[6:8]}"
                flag_entry = 0
                flag_exit = 0

            if flag_exit == 0:
                Tracking_index += 1

    # Build your dataframe using only the actual number of rows you filled:
    # Tracking = pd.DataFrame({
    #     'stock': stock_array[:Tracking_index],
    #     'buysell': buysell_array[:Tracking_index],
    #     'date': date_array[:Tracking_index],
    #     'entryTime': entryTime_array[:Tracking_index],
    #     'entry': entry_array[:Tracking_index],
    #     'exit_date': exit_date_array[:Tracking_index],
    #     'exitTime': exitTime_array[:Tracking_index],
    #     'exit': exit_array[:Tracking_index],
    #     'quantity': quantity_array[:Tracking_index],
    #     'pnl': pnl_array[:Tracking_index],
    #     'sl': sl_array[:Tracking_index],
    #     # 'date_number': date_number_array[:Tracking_index],
    # })

    Tracking = pd.DataFrame({
        'stock': stock_array[:Tracking_index],
        'buysell': buysell_array[:Tracking_index],
        'entry_date': date_array[:Tracking_index],
        'entry_time': entryTime_array[:Tracking_index],
        'entry': entry_array[:Tracking_index],
        'exit_date': exit_date_array[:Tracking_index],
        'exit_time': exitTime_array[:Tracking_index],
        'exit': exit_array[:Tracking_index],
        'quantity': quantity_array[:Tracking_index],
        'pnl': pnl_array[:Tracking_index],
        'sl': sl_array[:Tracking_index],
        # 'date_number': date_number_array[:Tracking_index],
    })

    return Tracking
    

def execute_backtesting_logic_args(args):
    return run_for_each_stock(*args)


def long_running_14(data, date_ranges):
    print("long_running_14")
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

    elapsed_time = time.perf_counter() - initial_time
    print(elapsed_time)
    print(f"Elapsed time: {elapsed_time * 1_000:.2f} ms")   # Microseconds
    print(f"Elapsed time: {elapsed_time * 1_000_000:.2f} µs")   # Microseconds
    print(f"Elapsed time: {elapsed_time * 1_000_000_000:.2f} ns")  # Nanoseconds

    fast_cache_list = []
    def combine_fast_cache_list_function(iter_list):
        for i in range(0, len(iter_list)):

            if iter_list[i] not in fast_cache_list:
                fast_cache_list.append(iter_list[i])

    fast_cache = files_check.convert_equation_to_([data["entry"]], list_stocks)
    combine_fast_cache_list_function(fast_cache)
    fast_cache = files_check.convert_equation_to_([data["entryPrice"]], list_stocks)
    combine_fast_cache_list_function(fast_cache)
    fast_cache = files_check.convert_equation_to_([data["quantity"]], list_stocks)
    combine_fast_cache_list_function(fast_cache)
    # print(data["entry"])
    # fast_cache = files_check.convert_equation_to_([data["entry"]], list_stocks)
    # combine_fast_cache_list_function(fast_cache)
    for x in data["exitCollection"]:
        fast_cache = files_check.convert_equation_to_([x["exit"]], list_stocks)
        combine_fast_cache_list_function(fast_cache)
        fast_cache = files_check.convert_equation_to_([x["exitPrice"]], list_stocks)
        combine_fast_cache_list_function(fast_cache)
    
    # print("fast_cache_list", fast_cache_list)
    smallest = files_check.get_smallest_tf(fast_cache_list)
    # print("smallest", smallest)
    
    fast_cache = files_check.convert_equation_to_([{'indicator': [{'value': '0'}, {'value': smallest}, {'value': 'close'}]}], list_stocks)
    combine_fast_cache_list_function(fast_cache)
    elapsed_time = time.perf_counter() - initial_time
    print(elapsed_time)
    print(f"Elapsed time: {elapsed_time * 1_000:.2f} ms")   # Microseconds
    print(f"Elapsed time: {elapsed_time * 1_000_000:.2f} µs")   # Microseconds
    print(f"Elapsed time: {elapsed_time * 1_000_000_000:.2f} ns")  # Nanoseconds
    
    for i in range(0, len(fast_cache_list)):
        fast_cache_list[i][3] = f"{smallest}_{fast_cache_list[i][3]}"
        fast_cache_list[i].append(smallest)
    # print("____________________________________")
    print("fast_cache_list", fast_cache_list)
    file_path = "wait_for_update"
    lock_path = file_path + ".lock"
    lock = FileLock(lock_path)
    functions.check_tf_range(smallest, data['dateRange']["from"], data['dateRange']["to"], date_ranges)
    elapsed_time = time.perf_counter() - initial_time
    print(elapsed_time)
    print(f"Elapsed time: {elapsed_time * 1_000:.2f} ms")   # Microseconds
    print(f"Elapsed time: {elapsed_time * 1_000_000:.2f} µs")   # Microseconds
    print(f"Elapsed time: {elapsed_time * 1_000_000_000:.2f} ns")  # Nanoseconds
    # with lock:
        # pass
    create_files.create_file(fast_cache_list)
    print("fast_cache_list")
    print(fast_cache_list)
    #____________________________________ convert to equation logic
    date_start = backtesting_functions.date_str_to_int(data['dateRange']["from"])
    date_end = backtesting_functions.date_str_to_int(data['dateRange']["to"])
    
    entry = backtesting_functions.entry_to_equation([data["entry"]] , None, smallest)
    print("entry")
    print(entry)
    entryPrice = backtesting_functions.entry_to_equation([data["entryPrice"]] , None, smallest)
    
    quantity = backtesting_functions.entry_to_equation([data["quantity"]] , None, smallest)
    

    exitCollection = []
    for i in data["exitCollection"]:
       
        exitCollection.append({
            "exit": backtesting_functions.entry_to_equation([i["exit"]] , None, smallest),
                               "exitPrice":backtesting_functions.entry_to_equation([i["exitPrice"]] , None, smallest),
                               "label": i["label"]
                               })


    if data["scanCategory"] == "":
    
        tradeSetup = "intraday_long"
    else:
        tradeSetup = data["scanCategory"] 
    print("*************")
    elapsed_time = time.perf_counter() - initial_time
    print(elapsed_time)
    print(f"Elapsed time: {elapsed_time * 1_000:.2f} ms")   # Microseconds
    print(f"Elapsed time: {elapsed_time * 1_000_000:.2f} µs")   # Microseconds
    print(f"Elapsed time: {elapsed_time * 1_000_000_000:.2f} ns")  # Nanoseconds

    # initial_time = time.perf_counter()
    Tracking = pd.DataFrame()
    for t in range(len(list_stocks)):
        result = run_for_each_stock(date_start, date_end, entry, entryPrice, quantity, exitCollection, tradeSetup, list_stocks[t], fast_cache_list, smallest)
        Tracking = pd.concat([Tracking, result], ignore_index=True)

#     Tracking = pd.DataFrame()

# # Prepare argument list for each task
#     tasks = [
#         (date_start, date_end, entry, entryPrice, quantity, exitCollection, tradeSetup, stock, fast_cache_list, smallest)
#         for stock in list_stocks
#     ]

#     with concurrent.futures.ProcessPoolExecutor() as executor:
#         results = executor.map(execute_backtesting_logic_args, tasks)
#     Tracking = pd.concat(list(results), ignore_index=True)

    # for i in range(0, len(Tracking)):
    #     if Tracking.loc[Tracking.index[i], 'buysell'] == 'buy':
    #         Tracking.loc[Tracking.index[i], 'pnl'] = (Tracking.loc[Tracking.index[i], 'exit'] - Tracking.loc[Tracking.index[i], 'entry'] )* Tracking.loc[Tracking.index[i], 'quantity']
    #     if Tracking.loc[Tracking.index[i], 'buysell'] == 'sell':
    #         Tracking.loc[Tracking.index[i], 'pnl'] = (Tracking.loc[Tracking.index[i], 'entry'] - Tracking.loc[Tracking.index[i], 'exit'] )* Tracking.loc[Tracking.index[i], 'quantity']

    
    Tracking['pnl'] = np.where(
    Tracking['buysell'] == 'buy',
    (Tracking['exit'] - Tracking['entry']) * Tracking['quantity'],
    np.where(
        Tracking['buysell'] == 'sell',
        (Tracking['entry'] - Tracking['exit']) * Tracking['quantity'],
        0
    )
)
    # elapsed_time = time.perf_counter() - initial_time
    # print(elapsed_time)
    # print(f"Elapsed time: {elapsed_time * 1_000:.2f} ms")   # Microseconds
    # print(f"Elapsed time: {elapsed_time * 1_000_000:.2f} µs")   # Microseconds
    # print(f"Elapsed time: {elapsed_time * 1_000_000_000:.2f} ns")  # Nanoseconds
    
    ##  track and delete extra files
    # files_tracking.fastCache_file_tracking_and_deletion(copy.deepcopy(fast_cache_list), unit="Mi", memory_size= 1024 *10)
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
            
    # files_tracking.stock_column_file_tracking_and_deletion(column_exist , unit="Mi", memory_size= 1024 *10)

    
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
    

    
    
    Tracking.to_csv("Tracking.csv")
    # print(Tracking.to_json(orient='records'))
    return {"data_result": data_compression.compress_json_for_frontend(Tracking.to_json(orient='records'))}
    # # return {"Hello": "World"}