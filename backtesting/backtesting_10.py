from fastapi import FastAPI, Request, APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from functions import timeframe, controller, indicators, backtesting_functions, functions, json_saving
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

    num_cpus = os.cpu_count() - 1
    if num_cpus < 1:
        num_cpus = 1
    
    return num_cpus



def run_for_each_stock(list_stocks, date_start, date_end, csv_import, entry, entryPrice, quantity, exitCollection, tradeSetup, combine_fastCache ):#,  order_dict, combine_fastCache):
    # initial_time = time.time()
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
    
    # cache_ts.update_cache(order_dict)
    
    for i in range(0, len(combine_fastCache)):
        combine_fastCache[i] = compile(combine_fastCache[i], "<string>", "eval")

    list_stocks = [list_stocks]
    t = 0
    print("pre_c_entry", entry)
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


    
    print(list_stocks[t])
    dict_of_timeframes, dict_of_time = backtesting_functions.get_csv_dict(list_stocks[t], csv_import)
    
    numeric_values = [x for x in list((dict_of_timeframes.keys())) if isinstance(x, (int, float))]
    print("numeric_values", numeric_values)
    if numeric_values:  
        smallest = min(numeric_values)
    elif "Daily" in dict_of_timeframes :
        smallest = "Daily"
    elif "Weekly" in dict_of_timeframes :
        smallest = "Weekly"
    elif "Monthly" in dict_of_timeframes :
        smallest = "Monthly"
        
    
    print("smallest", smallest)
    df = dict_of_timeframes[smallest]

    if smallest != "Daily" and smallest != "Weekly" and smallest != "Monthly":
        
        df_time = dict_of_time[smallest]
        df_time = df_time[f"uniqueTime_{smallest}"].iloc[-1]
        # df_time = int("".join(df_time.split(":"))) + smallest*100
        df_time = int("".join(df_time.split(":"))) 
    else:
        df_time = None
    
    try:
        date_start_index = df.index.get_loc(df.loc[df["date_number"]  >= date_start].index.tolist()[0])
        print(date_start_index)
    except:
        date_start_index = len(df)-1
        print("ERROR", date_start_index)
    try:
        date_end_index = df.index.get_loc(df.loc[df["date_number"]  <= date_end].index.tolist()[-1]) +1
        print(date_end_index)
    except:
        date_end_index = 0 
        print("ERROR", date_end_index)
    
    
    flag_entry = 0
    flag_exit = 0
    

    
    Tracking_index = 0
    df_data = df.to_numpy()
    data_column = list(df.columns)
    time_index = data_column.index("time_number")
    date_index = data_column.index("date_number")
    datetime_index = data_column.index("datetime_number")
    # int(df_data[i][time_index])
    

    # def count_previous_entry_intraday(Tracking, date):
    #     return (Tracking["date_number"] == date).sum()

# ____________________________________________________________________________________________________________
    
        # try:
        #     eval(pre_c_entry, globals(), locals())
        #     eval(pre_c_entryPrice, globals(), locals())
        #     eval(pre_c_quantity, globals(), locals())
        #     for exitCollection_index in range(len(exitCollection)):
                        
        #         eval(pre_c_exitCollection[exitCollection_index]["exit"], globals(), locals())
        # except:
        #     pass
    initial_time = time.time()
    i = date_end_index - 1
    
    fastCache_colum_name = []
    fastCache_colum_arr = []
    for j in range(0, len(combine_fastCache)):
        fastCache_colum_arr_var, fastCache_colum_name_var = eval(combine_fastCache[j], globals(), locals())
        fastCache_colum_name.append(fastCache_colum_name_var)
        fastCache_colum_arr.append(fastCache_colum_arr_var)

    if f"{list_stocks[t]}_{'close'}_{smallest}_{smallest}_{df_time}_{0}" not in fastCache_colum_name:
        fastCache_colum_arr_var, fastCache_colum_name_var = backtesting_functions.select_candles(list_stocks[t], i, 'close', int(df['datetime_number'].iloc[i]) ,dict_of_timeframes[smallest], dict_of_time[smallest], smallest, df, smallest, df_time, 0 )
        fastCache_colum_name.append(fastCache_colum_name_var)
        fastCache_colum_arr.append(fastCache_colum_arr_var)

    

    df_fastCache_colum_arr = np.hstack(tuple(fastCache_colum_arr))

    # df_fastCache_colum_arr[i][fastCache_colum_name.index("time_number")]
    # df_fastCache_colum_arr[i][fastCache_colum_name.index(f"{list_stocks[t]}_{'close'}_{smallest}_{smallest}_{df_time}_{0}")]
    print("fastCache_colum_name", fastCache_colum_name)

    elapsed_time = time.time() - initial_time
    print(elapsed_time)
    minutes, seconds = divmod(elapsed_time, 60)
    print(f"****Elapsed time for per stock: {int(minutes)} minutes and {int(seconds)} seconds")
    
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
                        'stock': str(list_stocks[t]),
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
                        Tracking.loc[Tracking_index, 'exit'] = float(df_fastCache_colum_arr[i][fastCache_colum_name.index(f"{list_stocks[t]}_{'close'}_{smallest}_{smallest}_{df_time}_{0}")]  )
                        
                        Tracking.loc[Tracking_index, 'exitTime'] = f'{trading_time_temp[-6:-4]}:{trading_time_temp[-4:-2]}'
                        Tracking.loc[Tracking_index, 'sl'] = 'universal exit'
                        Tracking.loc[Tracking_index, 'exit_date'] = f'{trading_date[0:4]}-{trading_date[4:6]}-{trading_date[6:8]}'    
                        
                        flag_entry = 0
                        flag_exit = 0
                
                if flag_exit == 0:
                    Tracking_index = Tracking_index + 1
    
    Tracking.drop(columns=['date_number'], inplace=True)

    ca = cache_ts.return_all_cache()
    ca_for_nparray = cache_for_nparray.return_all_cache()
    print("get_cache_size", cache_ts.get_cache_size())
    Tracking = Tracking[:Tracking_index]
    # return Tracking , ca, ca_for_nparray
    return Tracking
    

def execute_backtesting_logic_args(args):
    return run_for_each_stock(*args)

def long_running_10(data):
    print("long_running_10")
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

    

    tracemalloc.start()
    print("scanCategory" , data['scanCategory'])
    current, peak = tracemalloc.get_traced_memory()
    memory_check = {
        "current_memory": f"{current / 10**6:.2f} MB",
        "peak_memory": f"{peak / 10**6:.2f} MB"
    }
    print("start current_memory",memory_check["current_memory"],"start peak_memory", memory_check["peak_memory"])

    initial_time = time.time()
    list_stocks = data['stockList']

    list_stocks = functions.check_stock_files_if_exists(list_stocks)
    print(list_stocks)
    
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

    # print("combine_fastCache", combine_fastCache)

    # for i in range(0, len(combine_fastCache)):
    #     combine_fastCache[i] = compile(combine_fastCache[i], "<string>", "eval")

    print("combine_iter_list", combine_iter_list)

    print("get_smallest_tf", functions.get_smallest_tf(combine_iter_list))

    smallest_tf_combine_iter_list = functions.get_smallest_tf(combine_iter_list)
    functions.check_tf_range(smallest_tf_combine_iter_list, data['dateRange']["from"], data['dateRange']["to"])
        

    combine_iter_list_1 = controller.check_column_present(combine_iter_list)

    print("combine_iter_list_1", combine_iter_list_1)


    # save data for columns it will be used to create columns again

    location = "Clean_data/df_columns_exists.json"
    with json_saving.lock_file(location):
        try:
        
            loaded_data = json_saving.load_data_thread_safe(location)
            for u in range(0, len(combine_iter_list_1)):
                if combine_iter_list_1[u] not in loaded_data:
                    loaded_data.append(combine_iter_list_1[u])
                    
            json_saving.save_data_thread_safe(loaded_data, location)

        except:
            json_saving.save_data_thread_safe(combine_iter_list_1, location)
        
    


    if len(combine_iter_list_1) > 0:
        stocks, timeframes, params, arr = zip(*combine_iter_list_1)
        # print(stocks, timeframes)
        
        with concurrent.futures.ProcessPoolExecutor(max_workers= calculate_cpu() ) as executor:
            
            executor.map(controller.apply_indicators, stocks, timeframes, params, arr)

    
    
# #________________________________________
# # 
    csv_import = backtesting_functions.convert_data_for_csv_loading(combine_iter_list)
    
    date_start = backtesting_functions.date_str_to_int(data['dateRange']["from"])
    date_end = backtesting_functions.date_str_to_int(data['dateRange']["to"])
    
    entry = backtesting_functions.entry_to_equation([data["entry"]] , None)
    print("entry")
    # print(entry)
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

    args = [(list_stocks[i], date_start, date_end, csv_import, entry, entryPrice, quantity, exitCollection ,tradeSetup, combine_fastCache)#,  cache_ts.return_all_cache(), combine_fastCache)
    for i in range(len(list_stocks))
        ]
    
    elapsed_time = time.time() - initial_time
    print(elapsed_time)
    minutes, seconds = divmod(elapsed_time, 60)
    print(f"Elapsed time: {int(minutes)} minutes and {int(seconds)} seconds")

    #___________________________________________________________________
    
    Tracking = pd.DataFrame()
    with concurrent.futures.ProcessPoolExecutor(max_workers= calculate_cpu()) as executor:
        
        results = executor.map(execute_backtesting_logic_args, args)
            
        for result in results:
            Tracking = pd.concat([Tracking, result], ignore_index=True)
            # cache_ts.update_cache(ca)
            # cache_for_nparray.update_cache(ca_for_nparray)

    # Tracking = pd.DataFrame()
    # for arg in args:
    # # Call the function with the argument
    #     result  = execute_backtesting_logic_args(arg)
    #     # Concatenate the result to the Tracking DataFrame
    #     Tracking = pd.concat([Tracking, result], ignore_index=True)
    #     Update the cache
    #     cache_ts.update_cache(ca)
    #     print(ca_for_nparray)
    #     cache_for_nparray.update_cache(ca_for_nparray)
    
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