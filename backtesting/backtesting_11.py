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
import math
from cache_manager import cache_ts, cache_for_nparray

from functions.thread_safe_LRU_cache import ThreadSafeLRUCache

import redis_cache  
import json
import copy



def calculate_cpu():

    num_cpus = os.cpu_count()
    
    return num_cpus



def run_for_each_stock(list_stocks, date_start, date_end, csv_import, entry, entryPrice, quantity, exitCollection, tradeSetup, order_dict, combine_fastCache):
    initial_time = time.time()
    
    initial_length = 10000
    Tracking = np.empty((initial_length, 11), dtype=object)  # Preallocate memory
    Tracking[:] = ''

    cache_ts.update_cache(order_dict)
    
    list_stocks = [list_stocks]
    t = 0

    # 🚀 Convert expressions to lambdas
    entry_lambda = eval(f"lambda trading_time, trading_date, df_row: {entry}")
    entryPrice_lambda = eval(f"lambda trading_time, trading_date, df_row: {entryPrice}")
    quantity_lambda = eval(f"lambda trading_time, trading_date, df_row: {quantity}")

    pre_c_exitCollection = copy.deepcopy(exitCollection)
    for s in range(len(pre_c_exitCollection)):
        pre_c_exitCollection[s]["exit"] = eval(f"lambda trading_time, trading_date, df_row: {pre_c_exitCollection[s]['exit']}")
        pre_c_exitCollection[s]["exitPrice"] = eval(f"lambda trading_time, trading_date, df_row: {pre_c_exitCollection[s]['exitPrice']}")

    buysell = "buy" if tradeSetup in ["long", "intraday_long"] else "sell"

    # 🚀 Load CSV Data Efficiently
    dict_of_timeframes, dict_of_time = backtesting_functions.get_csv_dict(list_stocks[t], csv_import)
    numeric_values = [x for x in dict_of_timeframes.keys() if isinstance(x, (int, float))]
    smallest = min(numeric_values) if numeric_values else "Daily"

    df = dict_of_timeframes[smallest]
    df_time = None if smallest in ["Daily", "Weekly", "Monthly"] else int("".join(dict_of_time[smallest][f"uniqueTime_{smallest}"].iloc[-1].split(":")))

    try:
        date_start_index = df.index.get_loc(df[df["date_number"] >= date_start].index[0])
    except:
        date_start_index = len(df) - 1
    try:
        date_end_index = df.index.get_loc(df[df["date_number"] <= date_end].index[-1]) + 1
    except:
        date_end_index = 0

    flag_entry, flag_exit, Tracking_index = 0, 0, 0
    df_data = df.to_numpy()
    data_columns = {col: idx for idx, col in enumerate(df.columns)}

    # 🚀 Precompute FastCache Values
    fastCache_colum_name, fastCache_colum_arr = [], []
    for j in range(len(combine_fastCache)):
        fastCache_arr, fastCache_name = eval(combine_fastCache[j], globals(), locals())
        fastCache_colum_name.append(fastCache_name)
        fastCache_colum_arr.append(fastCache_arr)

    df_fastCache_colum_arr = np.hstack(tuple(fastCache_colum_arr))

    # 🚀 Main Loop
    for i in range(date_start_index, date_end_index):
        trading_time = str(int(df_data[i][data_columns["time_number"]]))
        trading_date = str(df_data[i][data_columns["date_number"]])

        if flag_entry == 1:
            try:
                if entry_lambda(trading_time, trading_date, df_data[i]):
                    Tracking[Tracking_index] = [
                        str(list_stocks[t]),
                        buysell,
                        f'{trading_date[:4]}-{trading_date[4:6]}-{trading_date[6:8]}',
                        entryPrice_lambda(trading_time, trading_date, df_data[i]),
                        f'{trading_time[-6:-4]}:{trading_time[-4:-2]}',
                        "",
                        0,
                        "",
                        round(quantity_lambda(trading_time, trading_date, df_data[i]), 0),
                        0,
                        ""
                    ]
                    flag_entry, flag_exit = 0, 1
            except:
                pass

        elif flag_exit == 1:
            for exit_obj in pre_c_exitCollection:
                if exit_obj["exit"](trading_time, trading_date, df_data[i]):
                    Tracking[Tracking_index][5:11] = [
                        f'{trading_date[:4]}-{trading_date[4:6]}-{trading_date[6:8]}',
                        exit_obj["exitPrice"](trading_time, trading_date, df_data[i]),
                        f'{trading_time[-6:-4]}:{trading_time[-4:-2]}',
                        exit_obj["label"],
                        0,
                        ""
                    ]
                    flag_exit, flag_entry = 0, 0
                    break

            # 🚀 Universal Exit
            if smallest not in ["Daily", "Weekly", "Monthly"] and tradeSetup not in ["long", "short"]:
                if int(trading_time) == df_time and flag_exit == 1:
                    Tracking[Tracking_index][5:11] = [
                        f'{trading_date[:4]}-{trading_date[4:6]}-{trading_date[6:8]}',
                        df_fastCache_colum_arr[i][fastCache_colum_name.index(f"{list_stocks[t]}_close_{smallest}_{smallest}_{df_time}_0")],
                        f'{trading_time[-6:-4]}:{trading_time[-4:-2]}',
                        "universal exit",
                        0,
                        ""
                    ]
                    flag_entry, flag_exit = 0, 0

            if flag_exit == 0:
                Tracking_index += 1

    # 🚀 Convert Numpy Array to DataFrame
    columns = ["stock", "buysell", "date", "entry", "entryTime", "exit_date", "exit", "exitTime", "quantity", "pnl", "sl"]
    Tracking_df = pd.DataFrame(Tracking[:Tracking_index], columns=columns)

    # 🚀 Fetch Cached Data
    ca = cache_ts.return_all_cache()
    ca_for_nparray = cache_for_nparray.return_all_cache()
    print("Cache size:", cache_ts.get_cache_size())

    return Tracking_df, ca, ca_for_nparray
    

def execute_backtesting_logic_args(args):
    return run_for_each_stock(*args)

def long_running_11(data):
    print("long_running_11")
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
    tracemalloc.start()
    print("scanCategory" , data['scanCategory'])
    current, peak = tracemalloc.get_traced_memory()
    memory_check = {
        "current_memory": f"{current / 10**6:.2f} MB",
        "peak_memory": f"{peak / 10**6:.2f} MB"
    }
    print("start current_memory",memory_check["current_memory"],"start peak_memory", memory_check["peak_memory"])

    initial_time = time.time()
    list_stocks = [
                # "AARTIIND", 
                #    "ABB", 
                # "ABCAPITAL", 
                # "ABFRL", 
                # "ACC",
                # "ONGC",
                "INFY"
                   ]
    
#________________________________________
    # apply indicators or generator csv files
    combine_iter_list = []
    def combine_iter_list_function(iter_list):
        for i in range(0, len(iter_list)):

            if iter_list[i] not in combine_iter_list:
                combine_iter_list.append(iter_list[i])

    combine_fastCache = []
    def combine_fastCache_function(iter_list):
        for i in range(0, len(iter_list)):

            if iter_list[i] not in combine_fastCache:
                combine_fastCache.append(iter_list[i])

    
    iter_list, iter_list_fastCache = backtesting_functions.get_list_for_generator([data["entry"]], list_stocks)
    combine_iter_list_function(iter_list)
    combine_fastCache_function(iter_list_fastCache)
    iter_list, iter_list_fastCache = backtesting_functions.get_list_for_generator([data["entryPrice"]], list_stocks)
    combine_iter_list_function(iter_list)
    combine_fastCache_function(iter_list_fastCache)
    iter_list, iter_list_fastCache = backtesting_functions.get_list_for_generator([data["quantity"]], list_stocks)
    combine_iter_list_function(iter_list)
    combine_fastCache_function(iter_list_fastCache)
    
    for x in data["exitCollection"]:
        iter_list, iter_list_fastCache = backtesting_functions.get_list_for_generator([x["exit"]], list_stocks)
        combine_iter_list_function(iter_list)
        combine_fastCache_function(iter_list_fastCache)
        iter_list, iter_list_fastCache = backtesting_functions.get_list_for_generator([x["exitPrice"]], list_stocks)
        combine_iter_list_function(iter_list)
        combine_fastCache_function(iter_list_fastCache)

    print("combine_fastCache", combine_fastCache)

    for i in range(0, len(combine_fastCache)):
        combine_fastCache[i] = compile(combine_fastCache[i], "<string>", "eval")

    print("combine_iter_list", combine_iter_list)

    combine_iter_list_1 = controller.check_column_present(combine_iter_list)

    print("combine_iter_list_1", combine_iter_list_1)

    if len(combine_iter_list_1) > 0:
        stocks, timeframes, params, arr = zip(*combine_iter_list_1)
        # print(stocks, timeframes)
        
        with concurrent.futures.ProcessPoolExecutor() as executor:
            
            executor.map(controller.apply_indicators, stocks, timeframes, params, arr)

    
    
# #________________________________________
# # 
    csv_import = backtesting_functions.convert_data_for_csv_loading(combine_iter_list)
    
    date_start = backtesting_functions.date_str_to_int(data['dateRange']["from"])
    date_end = backtesting_functions.date_str_to_int(data['dateRange']["to"])
    
    entry = backtesting_functions.entry_to_equation([data["entry"]] , None)
    print("entry")
    print(entry)
    entryPrice = backtesting_functions.entry_to_equation([data["entryPrice"]] , None)
    
    quantity = backtesting_functions.entry_to_equation([data["quantity"]] , None)
    

    exitCollection = []
    for i in data["exitCollection"]:
       
        exitCollection.append({
            "exit": backtesting_functions.entry_to_equation([i["exit"]] , None),
                               "exitPrice":backtesting_functions.entry_to_equation([i["exitPrice"]] , None),
                               "label": i["label"]
                               })
    if data["scanCategory"] == "":
    
        tradeSetup = "intraday_long"
    else:
        tradeSetup = data["scanCategory"] 

    args = [(list_stocks[i], date_start, date_end, csv_import, entry, entryPrice, quantity, exitCollection ,tradeSetup,  cache_ts.return_all_cache(), combine_fastCache)
    for i in range(len(list_stocks))
        ]
    
    elapsed_time = time.time() - initial_time
    print(elapsed_time)
    minutes, seconds = divmod(elapsed_time, 60)
    print(f"Elapsed time: {int(minutes)} minutes and {int(seconds)} seconds")

    #___________________________________________________________________
    
    # Tracking = pd.DataFrame()
    # with concurrent.futures.ProcessPoolExecutor(4) as executor:
        
    #     results = executor.map(execute_backtesting_logic_args, args)
            
    #     for result, ca, ca_for_nparray in results:
    #         Tracking = pd.concat([Tracking, result], ignore_index=True)
    #         cache_ts.update_cache(ca)
    #         cache_for_nparray.update_cache(ca_for_nparray)

    Tracking = pd.DataFrame()
    for arg in args:
    # Call the function with the argument
        result, ca, ca_for_nparray  = execute_backtesting_logic_args(arg)
        # Concatenate the result to the Tracking DataFrame
        Tracking = pd.concat([Tracking, result], ignore_index=True)
        # Update the cache
        cache_ts.update_cache(ca)
        print(ca_for_nparray)
        cache_for_nparray.update_cache(ca_for_nparray)
    
    for i in range(0, len(Tracking)):
        if Tracking.loc[Tracking.index[i], 'buysell'] == 'buy':
            Tracking.loc[Tracking.index[i], 'pnl'] = (Tracking.loc[Tracking.index[i], 'exit'] - Tracking.loc[Tracking.index[i], 'entry'] )* Tracking.loc[Tracking.index[i], 'quantity']
        if Tracking.loc[Tracking.index[i], 'buysell'] == 'sell':
            Tracking.loc[Tracking.index[i], 'pnl'] = (Tracking.loc[Tracking.index[i], 'entry'] - Tracking.loc[Tracking.index[i], 'exit'] )* Tracking.loc[Tracking.index[i], 'quantity']
                
#     Tracking['pnl'] = np.where(
#     Tracking['buysell'] == 'buy',
#     (Tracking['exit'] - Tracking['entry']) * Tracking['quantity'],  # Condition for 'buy'
#     np.where(
#         Tracking['buysell'] == 'sell',
#         (Tracking['entry'] - Tracking['exit']) * Tracking['quantity'],  # Condition for 'sell'
#         0  # Default value if neither 'buy' nor 'sell'
#     )
# )




    elapsed_time = time.time() - initial_time
    print(elapsed_time)
    minutes, seconds = divmod(elapsed_time, 60)
    print(f"Elapsed time: {int(minutes)} minutes and {int(seconds)} seconds")

    current, peak = tracemalloc.get_traced_memory()
    
    tracemalloc.stop()
    memory_check = {
        "current_memory": f"{current / 10**6:.2f} MB",
        "peak_memory": f"{peak / 10**6:.2f} MB"
    }
    print("current_memory",memory_check["current_memory"],"peak_memory", memory_check["peak_memory"])
    

    

    Tracking.to_csv("Tracking.csv")
    # print(Tracking.to_json(orient='records'))
    return {"data_result":Tracking.to_json(orient='records')}
    # # return {"Hello": "World"}