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
from cache_manager import cache_ts

from functions.thread_safe_LRU_cache import ThreadSafeLRUCache

import redis_cache  
import json
import copy

# cache_bt = ThreadSafeLRUCache(maxsize=128)

def calculate_cpu():

    num_cpus = os.cpu_count()
    
    return num_cpus



def run_for_each_stock(list_stocks, date_start, date_end, csv_import, entry, entryPrice, quantity, exitCollection, order_dict):

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
    })
    
    cache_ts.update_cache(order_dict)
    # print("I",cache_ts.return_all_cache())
    list_stocks = [list_stocks]
    t = 0

    pre_c_entry = compile(entry, "<string>", "eval")
    pre_c_entryPrice = compile(entryPrice, "<string>", "eval")
    pre_c_quantity = compile(quantity, "<string>", "eval")
    pre_c_exitCollection = copy.deepcopy(exitCollection)
    for s in range(len(pre_c_exitCollection)):
        pre_c_exitCollection[s]["exit"] = compile(pre_c_exitCollection[s]["exit"], "<string>", "eval")
        # print(pre_c_exitCollection[s]["exit"])
        pre_c_exitCollection[s]["exitPrice"] = compile(pre_c_exitCollection[s]["exitPrice"], "<string>", "eval")
    

    # pre_c_entry = entry
    # pre_c_entryPrice = entryPrice
    # pre_c_quantity = quantity
    # pre_c_exitCollection = copy.deepcopy(exitCollection)
    


    print(list_stocks[t])
    dict_of_timeframes, dict_of_time = backtesting_functions.get_csv_dict(list_stocks[t], csv_import)
    # print(dict_of_timeframes)
    # print(dict_of_time)
    numeric_values = [x for x in list((dict_of_timeframes.keys())) if isinstance(x, (int, float))]
    # print("numeric_values")
    # print(numeric_values)
    if numeric_values:  # Check if there are any numeric values
        smallest = min(numeric_values)
        # print(f"The smallest number is: {smallest}")
    # path = f"indicator_process/{list_stocks[t]}_{smallest}min.csv"
    # df = pd.read_csv(path,low_memory=False,parse_dates=['datetime'],index_col=['datetime'], usecols=['datetime', 'datetime_number', 'date_number', 'time_number'])
    df = dict_of_timeframes[smallest]
    # path_time = f"Clean_data/uniqueTime_{smallest}.csv"
    # df_time = pd.read_csv(path_time,low_memory=False,index_col=[0])
    df_time = dict_of_time[smallest]
    df_time = df_time[f"uniqueTime_{smallest}"].iloc[-1]
    df_time = int("".join(df_time.split(":")))
    
    try:
        date_start_index = df.index.get_loc(df.loc[df["date_number"]  >= date_start].index.tolist()[0])
        print(date_start_index)
    except:
        date_start_index = 0
    try:
       date_end_index = df.index.get_loc(df.loc[df["date_number"]  <= date_end].index.tolist()[-1])
       print(date_end_index)
    except:
        date_end_index = len(df)-1
        print("ERROR", date_end_index)
    
    
    flag_entry = 0
    flag_exit = 0
    print("hello ************************************** hello")

    # profiler = cProfile.Profile()
    # profiler.enable()  # Start profiling
    # temp_time = 0
    # temp_time_buy = 0
    Tracking_index = 0
    for i in range(date_start_index, date_end_index):
        # initial_time_buy = time.time() 
    
        if True:
             
# Entry Entry Entry Entry Entry Entry Entry____________________________________
            if  df.loc[df.index[i], "time_number"] == 91500:
                
                get_cache = redis_cache.get_cache((list_stocks[t], int(df.loc[df.index[i], "date_number"]), str(entry), str(entryPrice), str(quantity), str(exitCollection)))
                
                # get_cache = None
                if get_cache is not None:
                    # print(get_cache, list_stocks[t], int(df.loc[df.index[i], "date_number"]))
                    if get_cache == "None":
                        flag_entry = 0
                        flag_exit = 0
                    else:
                        # get_cache = dict(get_cache)
                        get_cache = json.loads(get_cache.replace("'", '"'))
                        Tracking.loc[Tracking_index] = {
                        "stock": get_cache["stock"],
                        "buysell": get_cache["buysell"],
                        "date": get_cache["date"],
                        "entry": get_cache["entry"],
                        "entryTime": get_cache["entryTime"],
                        "exit_date": get_cache["exit_date"],
                        "exit": get_cache["exit"],
                        "exitTime": get_cache["exitTime"],
                        "quantity": get_cache["quantity"],
                        "pnl": get_cache["pnl"],
                        "sl": get_cache["sl"],
                    }
                        flag_entry = 0
                        flag_exit = 0
                        if flag_entry == 0 and flag_exit == 0:
                            Tracking_index = Tracking_index + 1
                            # return get_cache
                else:
                    flag_entry = 1
            
            if flag_entry ==  1:
                # print("yes)")
                entry_t = backtesting_functions.select_candles(list_stocks[t], 'time_number', df['datetime_number'].iloc[i] ,dict_of_timeframes[smallest], dict_of_time[smallest], smallest,0 )
                dn = str(df.loc[df.index[i], "date_number"])
                try:
                    
                  
                    if ( eval(pre_c_entry, globals(), locals()) ):
                       
                        Tracking.loc[Tracking_index] = {
                        'stock': str(list_stocks[t]),
                        'buysell': 'buy',
                        'date': f'{dn[0:4]}-{dn[4:6]}-{dn[6:8]}',
                        'entry':  eval(pre_c_entryPrice, globals(), locals()),
                        'entryTime': f'{str(int(entry_t))[-6:-4]}:{str(int(entry_t))[-4:-2]}',
                        'exit_date' :"",
                        'exit':0,
                        'exitTime':'',
                        'quantity': round( eval(pre_c_quantity, globals(), locals()) ,0), 
                        'pnl':0,
                        'sl':'',
                    }
                        
                        flag_entry = 0
                        flag_exit = 1


                except Exception as e:
                    # print(i)
                    # print("ERROR 2",e)
                    pass
                if  df.loc[df.index[i], "time_number"] == df_time:
                    # print("none save ", df.loc[df.index[i], "date_number"] )
                    # cache_bt.set(None, list_stocks[t], int(df.loc[df.index[i], "date_number"]) )
                    redis_cache.set_cache((list_stocks[t], int(df.loc[df.index[i], "date_number"]), str(entry), str(entryPrice), str(quantity), str(exitCollection)), "None")
                    pass
                # temp_time_buy = temp_time_buy +  (time.time() - initial_time_buy)
# Exit Exit Exit Exit Exit Exit Exit Exit ________________________________________________
            elif flag_exit == 1:
                # initial_time = time.time()
                exit_t = backtesting_functions.select_candles(list_stocks[t], 'time_number', df['datetime_number'].iloc[i] ,dict_of_timeframes[smallest], dict_of_time[smallest], smallest,0 )
                dn = str(df.loc[df.index[i], "date_number"])
                for exitCollection_index in range(len(exitCollection)):
                    # print("len(exitCollection)", eval(exitCollection[i]["exit"]))
                    if eval(pre_c_exitCollection[exitCollection_index]["exit"], globals(), locals()):
                        Tracking.loc[Tracking_index, 'exit'] = eval(pre_c_exitCollection[exitCollection_index]["exitPrice"], globals(), locals())  #float(Tracking.loc[Tracking.index[-1], 'entry'] *(1-0.015*1))
                        Tracking.loc[Tracking_index, 'exitTime'] = f'{str(int(exit_t))[-6:-4]}:{str(int(exit_t))[-4:-2]}'
                        Tracking.loc[Tracking_index, 'sl'] = exitCollection[exitCollection_index]["label"]
                        Tracking.loc[Tracking_index, 'exit_date'] = f'{dn[0:4]}-{dn[4:6]}-{dn[6:8]}'
                        flag_exit = 0
                        flag_entry = 0
                        # print("break")
                        dict_cache = {
                        "stock": Tracking.loc[Tracking_index, "stock"],
                        "buysell": Tracking.loc[Tracking_index, "buysell"],
                        "date": Tracking.loc[Tracking_index, "date"],
                        "entry": float(Tracking.loc[Tracking_index, "entry"]),
                        "entryTime": Tracking.loc[Tracking_index, "entryTime"],
                        "exit_date": Tracking.loc[Tracking_index, "exit_date"],
                        "exit": float(Tracking.loc[Tracking_index, "exit"]),
                        "exitTime": Tracking.loc[Tracking_index, "exitTime"],
                        "quantity": float(Tracking.loc[Tracking_index, "quantity"]),
                        "pnl": float(Tracking.loc[Tracking_index, "pnl"]),
                        "sl": Tracking.loc[Tracking_index, "sl"],
                    }
                        # print(dict_cache)
                        
                        redis_cache.set_cache((list_stocks[t], int(df.loc[df.index[i], "date_number"]), str(entry), str(entryPrice), str(quantity), str(exitCollection)), json.dumps(dict_cache))
                        
                        break
                # universal exit
                # print(df.loc[df.index[i], "time_number"])
                # if  df.loc[df.index[i], "time_number"] == df_time and flag_exit == 1:
                if exit_t == df_time and flag_exit == 1:
                    # print("hey")
                    Tracking.loc[Tracking_index, 'exit'] = float(backtesting_functions.select_candles(list_stocks[t], 'close', df['datetime_number'].iloc[i] ,dict_of_timeframes[smallest], dict_of_time[smallest], smallest,0 )  )
                    Tracking.loc[Tracking_index, 'exitTime'] = f'{str(int(exit_t))[-6:-4]}:{str(int(exit_t))[-4:-2]}'
                    Tracking.loc[Tracking_index, 'sl'] = 'universal exit'
                    Tracking.loc[Tracking_index, 'exit_date'] = f'{dn[0:4]}-{dn[4:6]}-{dn[6:8]}'    
                    dict_cache = {
                        "stock": Tracking.loc[Tracking_index, "stock"],
                        "buysell": Tracking.loc[Tracking_index, "buysell"],
                        "date": Tracking.loc[Tracking_index, "date"],
                        "entry": float(Tracking.loc[Tracking_index, "entry"]),
                        "entryTime": Tracking.loc[Tracking_index, "entryTime"],
                        "exit_date": Tracking.loc[Tracking_index, "exit_date"],
                        "exit": float(Tracking.loc[Tracking_index, "exit"]),
                        "exitTime": Tracking.loc[Tracking_index, "exitTime"],
                        "quantity": float(Tracking.loc[Tracking_index, "quantity"]),
                        "pnl": float(Tracking.loc[Tracking_index, "pnl"]),
                        "sl": Tracking.loc[Tracking_index, "sl"],
                    }
                    # print(dict_cache)
                    # cache_bt.set(dict_cache, list_stocks[t], int(df.loc[df.index[i], "date_number"]) )
                    redis_cache.set_cache((list_stocks[t], int(df.loc[df.index[i], "date_number"]), str(entry), str(entryPrice), str(quantity), str(exitCollection)), json.dumps(dict_cache))
                    flag_entry = 0
                    flag_exit = 0
                if flag_entry == 0 and flag_exit == 0:
                    Tracking_index = Tracking_index + 1
                # temp_time = temp_time +  (time.time() - initial_time)
    # profiler.disable()
    # profiler.print_stats(sort='time')  
    
    # print("temp_time", temp_time)
    # minutes, seconds = divmod(temp_time, 60)
    # print(f"Elapsed time: {int(minutes)} minutes and {int(seconds)} seconds")
    # print("temp_time_buy", temp_time_buy)
    # minutes, seconds = divmod(temp_time_buy, 60)
    # print(f"Elapsed time: {int(minutes)} minutes and {int(seconds)} seconds")
    # print(cache_ts.return_all_cache())
    ca = cache_ts.return_all_cache()
    # print("ca", ca)
    Tracking = Tracking[:Tracking_index]
    return Tracking , ca
    # return Tracking 

def execute_backtesting_logic_args(args):
    return run_for_each_stock(*args)

def long_running_7(data):
    print("long_running_7")
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
    # tracemalloc.start()
    current, peak = tracemalloc.get_traced_memory()
    memory_check = {
        "current_memory": f"{current / 10**6:.2f} MB",
        "peak_memory": f"{peak / 10**6:.2f} MB"
    }
    print("start current_memory",memory_check["current_memory"],"start peak_memory", memory_check["peak_memory"])

    initial_time = time.time()
    list_stocks = [
                "AARTIIND", 
                #    "ABB", 
                # "ABCAPITAL", 
                # "ABFRL", 
                # "ACC",
                # "ONGC"
                   ]
    
#________________________________________
    # apply indicators or generator csv files
    combine_iter_list = []
    def combine_iter_list_function(iter_list):
        for i in range(0, len(iter_list)):

            if iter_list[i] not in combine_iter_list:
                combine_iter_list.append(iter_list[i])

    
    iter_list = backtesting_functions.get_list_for_generator([data["entry"]], list_stocks)
    combine_iter_list_function(iter_list)
    iter_list = backtesting_functions.get_list_for_generator([data["entryPrice"]], list_stocks)
    combine_iter_list_function(iter_list)
    iter_list = backtesting_functions.get_list_for_generator([data["quantity"]], list_stocks)
    combine_iter_list_function(iter_list)
    
    for x in data["exitCollection"]:
        iter_list = backtesting_functions.get_list_for_generator([x["exit"]], list_stocks)
        combine_iter_list_function(iter_list)
        iter_list = backtesting_functions.get_list_for_generator([x["exitPrice"]], list_stocks)
        combine_iter_list_function(iter_list)

    # print("combine_iter_list", combine_iter_list)

    combine_iter_list_1 = controller.check_column_present(combine_iter_list)

    # elapsed_time = time.time() - initial_time
    # print(elapsed_time)
    # minutes, seconds = divmod(elapsed_time, 60)
    # print(f"Elapsed time: {int(minutes)} minutes and {int(seconds)} seconds")

    # print("combine_iter_list", combine_iter_list_1)

    if len(combine_iter_list_1) > 0:
        stocks, timeframes, params, arr = zip(*combine_iter_list_1)
        # print(stocks, timeframes)
        
        with concurrent.futures.ProcessPoolExecutor() as executor:
            
            executor.map(controller.apply_indicators, stocks, timeframes, params, arr)

    # elapsed_time = time.time() - initial_time
    # print(elapsed_time)
    # minutes, seconds = divmod(elapsed_time, 60)
    # print(f"Elapsed time: {int(minutes)} minutes and {int(seconds)} seconds")
    
# #________________________________________
# # 
    csv_import = backtesting_functions.convert_data_for_csv_loading(combine_iter_list)
    # print("csv_import")
    # print(csv_import)
    date_start = backtesting_functions.date_str_to_int(data['dateRange']["from"])
    date_end = backtesting_functions.date_str_to_int(data['dateRange']["to"])
    # print("date_start", date_start, "date_end" , date_end)
    entry = backtesting_functions.entry_to_equation([data["entry"]] , None)
    print("entry")
    print(entry)
    entryPrice = backtesting_functions.entry_to_equation([data["entryPrice"]] , None)
    # print("entryPrice")
    # print(entryPrice)

    quantity = backtesting_functions.entry_to_equation([data["quantity"]] , None)
    # print(quantity)

    exitCollection = []
    for i in data["exitCollection"]:
        # print("_______________________________")
        # print(i)
        exitCollection.append({
            "exit": backtesting_functions.entry_to_equation([i["exit"]] , None),
                               "exitPrice":backtesting_functions.entry_to_equation([i["exitPrice"]] , None),
                               "label": i["label"]
                               })
    # print("exitCollection")
    # print(exitCollection)

    args = [(list_stocks[i], date_start, date_end, csv_import, entry, entryPrice, quantity, exitCollection , cache_ts.return_all_cache())
    for i in range(len(list_stocks))
        ]
    
    elapsed_time = time.time() - initial_time
    print(elapsed_time)
    minutes, seconds = divmod(elapsed_time, 60)
    print(f"Elapsed time: {int(minutes)} minutes and {int(seconds)} seconds")

    #___________________________________________________________________
    
    Tracking = pd.DataFrame()
    with concurrent.futures.ProcessPoolExecutor(2) as executor:
        # try:
            # Use map with a standalone function
        results = executor.map(execute_backtesting_logic_args, args)
            
            # Combine all results into the Tracking DataFrame
        for result, order_dict in results:
            Tracking = pd.concat([Tracking, result], ignore_index=True)
            cache_ts.update_cache(order_dict)
    
    # for i in range(0, len(Tracking)):
    #     if Tracking.loc[Tracking.index[i], 'buysell'] == 'buy':
    #         Tracking.loc[Tracking.index[i], 'pnl'] = (Tracking.loc[Tracking.index[i], 'exit'] - Tracking.loc[Tracking.index[i], 'entry'] )* Tracking.loc[Tracking.index[i], 'quantity']
    #     if Tracking.loc[Tracking.index[i], 'buysell'] == 'sell':
    #         Tracking.loc[Tracking.index[i], 'pnl'] = (Tracking.loc[Tracking.index[i], 'entry'] - Tracking.loc[Tracking.index[i], 'exit'] )* Tracking.loc[Tracking.index[i], 'quantity']
                
    Tracking['pnl'] = np.where(
    Tracking['buysell'] == 'buy',
    (Tracking['exit'] - Tracking['entry']) * Tracking['quantity'],  # Condition for 'buy'
    np.where(
        Tracking['buysell'] == 'sell',
        (Tracking['entry'] - Tracking['exit']) * Tracking['quantity'],  # Condition for 'sell'
        0  # Default value if neither 'buy' nor 'sell'
    )
)




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