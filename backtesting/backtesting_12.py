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
from functions_v1 import files_check, files_tracking


def calculate_cpu():

    num_cpus = os.cpu_count() - 1
    if num_cpus < 1:
        num_cpus = 1
    
    return num_cpus

def run_for_each_stock(date_start, date_end, entry, entryPrice, quantity, exitCollection, tradeSetup, stock, fast_cache_list, smallest):
# def run_for_each_stock(list_stocks, date_start, date_end, csv_import, entry, entryPrice, quantity, exitCollection, tradeSetup, combine_fastCache ):#,  order_dict, combine_fastCache):
    # initial_time = time.perf_counter()
    initial_length = 10000
    Tracking = pd.DataFrame({
        'stock': [''] * initial_length,
        'buysell': [''] * initial_length,
        'date': [''] * initial_length,
        'entryTime': [''] * initial_length,
        'entry': [0.0] * initial_length,
        'exit_date': [''] * initial_length,
        'exitTime': [''] * initial_length,
        'exit': [0.0] * initial_length,
        'quantity': [0.0] * initial_length,
        'pnl': [0.0] * initial_length,
        'sl': [''] * initial_length,
        'date_number': [0] * initial_length,
    })
    
   
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
    
    
    flag_entry = 0
    flag_exit = 0
    

    
    Tracking_index = 0
    df_data = df.to_numpy()
    data_column = list(df.columns)
    time_index = data_column.index("time_number")
    date_index = data_column.index("date_number")
    datetime_index = data_column.index("datetime_number")
   
    i = date_end_index - 1
    

    fastCache_colum_arr, fastCache_colum_name = create_files.return_fastCache_file(fast_cache_list, stock)

    # print("fastCache_colum_arr", fastCache_colum_name[0] , len(fastCache_colum_arr[0]),fastCache_colum_name[1],  len(fastCache_colum_arr[1]))
    # print("fastCache_colum_arr", fastCache_colum_arr)
    # df_fastCache_colum_arr = np.hstack(tuple(fastCache_colum_arr))
    # df_fastCache_colum_arr = fastCache_colum_arr
    df_fastCache_colum_arr = np.stack(fastCache_colum_arr, axis=1)
    # df_fastCache_colum_arr = np.column_stack(fastCache_colum_arr)
    
    # print("fastCache_colum_name", df_fastCache_colum_arr, len(df_fastCache_colum_arr))


   
    smallest_close = ""
    for i in range(len(fast_cache_list)):
        if fast_cache_list[i][0] == stock and smallest == fast_cache_list[i][1] and fast_cache_list[i][2] == "close" and smallest == fast_cache_list[i][5]: 
            smallest_close = fast_cache_list[i][3]  

    for i in range(date_start_index, date_end_index):
        
        if True:
             
# Entry Entry Entry Entry Entry Entry Entry____________________________________
            
            
            if  (smallest != "Daily" and smallest != "Weekly" and smallest != "Monthly" and tradeSetup != "long" and tradeSetup != "short" ) :
                
                
                            
                if flag_exit == 0:
                    flag_entry = 1
## for Daily and higher TF
            if (smallest == "Daily" or smallest == "Weekly" or smallest == "Monthly" or tradeSetup == "long" or tradeSetup == "short") and flag_entry == 0 and flag_exit == 0:
                flag_entry = 1
            
# do not enter if candle is last for intraday
            if df_data[i][time_index]  == df_time and (smallest != "Daily" and smallest != "Weekly" and smallest != "Monthly" and tradeSetup != "long" and tradeSetup != "short" ):
                flag_entry = 0
            if flag_entry ==  1 :
                
                # trading_time = str(int(df_data[i][time_index]))
                # trading_date = str(df_data[i][date_index])
                
                try:
                    
                    if ( eval(pre_c_entry, globals(), locals()) ):
                        trading_time = str(int(df_data[i][time_index]))
                        trading_date = str(df_data[i][date_index])
                       
                        Tracking.loc[Tracking_index] = {
                        'stock': str(stock),
                        'buysell': buysell,
                        'date': f'{trading_date[0:4]}-{trading_date[4:6]}-{trading_date[6:8]}',
                        'entry':  eval(pre_c_entryPrice, globals(), locals()),
                        'entryTime': f'{trading_time[-6:-4]}:{trading_time[-4:-2]}',
                        'exit_date' :"",
                        'exit':0,
                        'exitTime':'',
                        'quantity': round( eval(pre_c_quantity, globals(), locals()) ,0), 
                        'pnl':0,
                        'sl':'',
                        'date_number': int(df_data[i][date_index])
                    }
                        
                        flag_entry = 0
                        flag_exit = 1


                except Exception as e:
                    # print(i)
                    # print("ERROR 2",e)
                    pass
                if smallest != "Daily" and smallest != "Weekly" and smallest != "Monthly" and tradeSetup != "intraday_long" and tradeSetup != "intraday_short":
                    if  df_data[i][time_index]  == df_time:
                        pass
                
# Exit Exit Exit Exit Exit Exit Exit Exit ________________________________________________
            elif flag_exit == 1:
               
                # trading_time = str(int(df_data[i][time_index]))
                # trading_date = str(df_data[i][date_index])
                
                for exitCollection_index in range(len(exitCollection)):
                    
                    if eval(pre_c_exitCollection[exitCollection_index]["exit"], globals(), locals()):
                        trading_time = str(int(df_data[i][time_index]))
                        trading_date = str(df_data[i][date_index])
                        Tracking.loc[Tracking_index, 'exit'] = eval(pre_c_exitCollection[exitCollection_index]["exitPrice"], globals(), locals())  #float(Tracking.loc[Tracking.index[-1], 'entry'] *(1-0.015*1))
                        Tracking.loc[Tracking_index, 'exitTime'] = f'{trading_time[-6:-4]}:{trading_time[-4:-2]}'
                        Tracking.loc[Tracking_index, 'sl'] = exitCollection[exitCollection_index]["label"]
                        Tracking.loc[Tracking_index, 'exit_date'] = f'{trading_date[0:4]}-{trading_date[4:6]}-{trading_date[6:8]}'
                        flag_exit = 0
                        flag_entry = 0
                        
                   
                        
                        
                        break
    # universal exit
                if smallest != "Daily" and smallest != "Weekly" and smallest != "Monthly" and tradeSetup != "long" and tradeSetup != "short":
                    trading_time = str(int(df_data[i][time_index]))
                    trading_time_temp = str(int(trading_time) )
                    if int(trading_time_temp) == df_time and flag_exit == 1  :
                        trading_date = str(df_data[i][date_index])
                        
                        
                        # Tracking.loc[Tracking_index, 'exit'] = float(backtesting_functions.select_candles(list_stocks[t], i, 'close', df['datetime_number'].iloc[i] + smallest*100 ,dict_of_timeframes[smallest], dict_of_time[smallest], smallest, df, smallest, df_time, 0 )  )
                        Tracking.loc[Tracking_index, 'exit'] = float(df_fastCache_colum_arr[i][fastCache_colum_name.index(smallest_close)]  )
                        
                        Tracking.loc[Tracking_index, 'exitTime'] = f'{trading_time_temp[-6:-4]}:{trading_time_temp[-4:-2]}'
                        Tracking.loc[Tracking_index, 'sl'] = 'universal exit'
                        Tracking.loc[Tracking_index, 'exit_date'] = f'{trading_date[0:4]}-{trading_date[4:6]}-{trading_date[6:8]}'    
                        
                        flag_entry = 0
                        flag_exit = 0
                
                if flag_exit == 0:
                    Tracking_index = Tracking_index + 1
    
    Tracking.drop(columns=['date_number'], inplace=True)
    
    
    Tracking = Tracking[:Tracking_index]
    
    # elapsed_time = time.perf_counter() - initial_time
    # print("end")
    # print(elapsed_time)
    # print(f"Elapsed time: {elapsed_time * 1_000:.2f} ms")   # Microseconds
    # print(f"Elapsed time: {elapsed_time * 1_000_000:.2f} µs")   # Microseconds
    # print(f"Elapsed time: {elapsed_time * 1_000_000_000:.2f} ns")  # Nanoseconds
    return Tracking
    

def execute_backtesting_logic_args(args):
    return run_for_each_stock(*args)


def long_running_12(data, date_ranges):
    print("long_running_12")
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
    create_files.create_file(fast_cache_list)
    

    #____________________________________ convert to equation logic
    date_start = backtesting_functions.date_str_to_int(data['dateRange']["from"])
    date_end = backtesting_functions.date_str_to_int(data['dateRange']["to"])
    
    entry = backtesting_functions.entry_to_equation([data["entry"]] , None, smallest)
    print("entry")
    # print(entry)
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
    # initial_time = time.perf_counter()
    Tracking = pd.DataFrame()
    for t in range(len(list_stocks)):
        result = run_for_each_stock(date_start, date_end, entry, entryPrice, quantity, exitCollection, tradeSetup, list_stocks[t], fast_cache_list, smallest)
        Tracking = pd.concat([Tracking, result], ignore_index=True)

    for i in range(0, len(Tracking)):
        if Tracking.loc[Tracking.index[i], 'buysell'] == 'buy':
            Tracking.loc[Tracking.index[i], 'pnl'] = (Tracking.loc[Tracking.index[i], 'exit'] - Tracking.loc[Tracking.index[i], 'entry'] )* Tracking.loc[Tracking.index[i], 'quantity']
        if Tracking.loc[Tracking.index[i], 'buysell'] == 'sell':
            Tracking.loc[Tracking.index[i], 'pnl'] = (Tracking.loc[Tracking.index[i], 'entry'] - Tracking.loc[Tracking.index[i], 'exit'] )* Tracking.loc[Tracking.index[i], 'quantity']

    # elapsed_time = time.perf_counter() - initial_time
    # print(elapsed_time)
    # print(f"Elapsed time: {elapsed_time * 1_000:.2f} ms")   # Microseconds
    # print(f"Elapsed time: {elapsed_time * 1_000_000:.2f} µs")   # Microseconds
    # print(f"Elapsed time: {elapsed_time * 1_000_000_000:.2f} ns")  # Nanoseconds
    
    ##  track and delete extra files
    files_tracking.fastCache_file_tracking_and_deletion(copy.deepcopy(fast_cache_list), unit="Mi", memory_size= 50)
    column_not_exist = controller.check_column_present(fast_cache_list)
    
    column_exist = []
    for i in range(len(fast_cache_list)):
        if (fast_cache_list[i] not in column_not_exist 
        and fast_cache_list[i][2] != "close" 
        and fast_cache_list[i][2] != "high" 
        and fast_cache_list[i][2] != "low" 
        and fast_cache_list[i][2] != "open"
        and fast_cache_list[i][2] != "volume"
        and fast_cache_list[i][2] != "datetime"
        and fast_cache_list[i][2] != "date_number"
        and fast_cache_list[i][2] != "time_number"
        and fast_cache_list[i][2] != "datetime_number" ):
            
            column_exist.append(fast_cache_list[i])
            
    files_tracking.stock_column_file_tracking_and_deletion(column_exist , unit="Mi", memory_size= 50)

    
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
    # print(Tracking.to_json(orient='records'))
    return {"data_result":Tracking.to_json(orient='records')}
    # # return {"Hello": "World"}