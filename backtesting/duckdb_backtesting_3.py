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
# import tracemalloc
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

# from functions_duckdb.duckdb_obj_pool import duckdb_conn
from functions_duckdb.sqllite_memory_db import TrackingDB
import sqlite3
from functions_duckdb.functions import check_tf_range as f_ddb_check_tf_range
import fastapi



# from functions_duckdb  import workers 
# conn_sqlite =  sqlite3.connect(":memory:")
# duckdb_conn = duckdb.connect(database="database_duckdb/stocks.duckdb")
# duckdb_conn
# sl_db = TrackingDB()
# create  = CreateFiles(duckdb_conn = duckdb_conn, stock_list=[])

# def work(x):
#     print("Running in process:", os.getpid())
#     return x * 2

# exec0 = workers.EXEC0
# exec1 = workers.EXEC1
# f0 = exec0.submit(work, 10)
# f1 = exec1.submit(work, 20)

# print(f0.result())
# print(f1.result())


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
def duckdb_backtesting_3(data, date_ranges,stock_list,  create, duckdb_conn, sl_db):
    # tracemalloc.start()
    # print("duckdb_backtesting_1")
    init = time.perf_counter_ns()
    sl_db.init_table()
    print("init_table",(time.perf_counter_ns() - init)/1000/1000, "ms")
    # print("Running in process:", os.getpid())
   
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
    init = time.perf_counter_ns()
    # list_stocks = functions.check_stock_files_if_exists(list_stocks)
    print(list_stocks)
    

    btf_obj = BackTestingFunction(stock_list=list_stocks)
    btf_obj.convert_req_data_to_list([data["entry"]], tag = "entry")
    btf_obj.convert_req_data_to_list([data["entryPrice"]], tag = "entryPrice")
    btf_obj.convert_req_data_to_list([data["quantity"]], tag = "quantity")
    for index, x in enumerate(data["exitCollection"]):
        btf_obj.convert_req_data_to_list([x["exit"]], tag = f"exitCollection_{index}_exit")
        btf_obj.convert_req_data_to_list([x["exitPrice"]], tag = f"exitCollection_{index}_exitPrice")
        


   
    # create  = CreateFiles(duckdb_conn = duckdb_conn, stock_list=list_stocks)
    create.manual_init(duckdb_conn = duckdb_conn, stock_list=list_stocks)
    print("___________")
    create.accumulate_request_data(btf_obj.tags["entry"])
    create.accumulate_request_data(btf_obj.tags["entryPrice"])
    create.accumulate_request_data(btf_obj.tags["quantity"])
    for index, x in enumerate(data["exitCollection"]):
        create.accumulate_request_data(btf_obj.tags[f"exitCollection_{index}_exit"])
        create.accumulate_request_data(btf_obj.tags[f"exitCollection_{index}_exitPrice"])

    # print(create.raw_data_list)
    print("___________")
    # print(create.unique_indicator_columns)
    print("___________")
    

    create.create_indicators_and_candles()

    


    

    obj = BacktestingTable(stock_list=list_stocks)
    obj.accumulate_request_data(btf_obj.tags["entry"])
    obj.accumulate_request_data(btf_obj.tags["entryPrice"])
    obj.accumulate_request_data(btf_obj.tags["quantity"])
    for index, x in enumerate(data["exitCollection"]):
        obj.accumulate_request_data(btf_obj.tags[f"exitCollection_{index}_exit"])
        obj.accumulate_request_data(btf_obj.tags[f"exitCollection_{index}_exitPrice"])
    
    # start_date = '2020-01-01'
    # end_date = '2021-01-01'

    start_date = data['dateRange']['from']
    end_date = data['dateRange']['to']
    
    
    
    btf_obj.find_special_functions([data["entry"]] , "entry")
    btf_obj.find_special_functions([data["entryPrice"]] , "entryPrice")
    btf_obj.find_special_functions([data["quantity"]] , "quantity")
    for index, x in enumerate(data["exitCollection"]):
        btf_obj.find_special_functions([x["exit"]], f"exitCollection_{index}_exit")
        btf_obj.find_special_functions([x["exitPrice"]], f"exitCollection_{index}_exitPrice")
    

    obj.collect_depth_zero_uniqueid = btf_obj.collect_depth_zero_uniqueid
    obj.collect_all_cte_tables = btf_obj.collect_all_cte_tables 
    
    # check date range for the role
    date_ranges_output = f_ddb_check_tf_range(obj.smallest_tf, data['dateRange']["from"], data['dateRange']["to"], date_ranges)
    # print("date_ranges_output")
    
    if date_ranges_output is not None and "exception" in date_ranges_output:
        
        # print(type(date_ranges_output) == fastapi.exceptions.HTTPException)
        return date_ranges_output
            
    



    
    final_text = obj.final_query(start_date, end_date)
    print("df query data creation time" , (time.perf_counter_ns() - init)/1000/1000)
    with open("w_output.txt", "w") as file:
        file.write(final_text)
    init = time.perf_counter_ns()
    try:
        df = duckdb_conn.sql(final_text).fetchnumpy()
    except:
        return pd.DataFrame()
    print("df fetching time" , (time.perf_counter_ns() - init)/1000/1000, "ms")
    print("df fetching time" , (time.perf_counter_ns() - init)/1000/1000/1000, "s")
    print(f"df fetching time  / stock {len(list_stocks)}" , (time.perf_counter_ns() - init)/1000/1000/len(list_stocks), "ms")
    init = time.perf_counter_ns()

    print(data['dateRange'])

    
    print("________________")
    
    # print(df.keys())
    new_Df = pd.DataFrame(df)
    new_Df.to_csv("w_BT_Table.csv")
    # print(df)


    # entry = btf_obj.entry_to_equation([data["entry"]] , None, obj.smallest_tf)
    entry = btf_obj.entry_to_equation([data["entry"]] , None, obj.smallest_tf)
    entryPrice = btf_obj.entry_to_equation([data["entryPrice"]] , None, obj.smallest_tf)
    quantity = btf_obj.entry_to_equation([data["quantity"]] , None, obj.smallest_tf)
    exitCollection = []
    for i in data["exitCollection"]:
       
        exitCollection.append({
            "exit": btf_obj.entry_to_equation([i["exit"]] , None, obj.smallest_tf),
            "exitPrice": btf_obj.entry_to_equation([i["exitPrice"]] , None, obj.smallest_tf),
            "label": i["label"]
                               })



    print("_______________________")
    print(obj.collect_depth_zero_uniqueid)
    # print(obj.create_cte_for_window_functions(15, "SBIN"))
#__________________________________________________________
    print("entry")
    # print(entry)
    print("exitCollection")
    # print(exitCollection)
    
    # pre_c_entry = compile(entry, "<string>", "eval")
    pre_c_entry = compile(entry, "<string>", "eval")
    pre_c_entryPrice = compile(entryPrice, "<string>", "eval")
    pre_c_quantity = compile(quantity, "<string>", "eval")
    pre_c_exitCollection = copy.deepcopy(exitCollection)
    for s in range(len(pre_c_exitCollection)):
        pre_c_exitCollection[s]["exit"] = compile(pre_c_exitCollection[s]["exit"], "<string>", "eval")
        pre_c_exitCollection[s]["exitPrice"] = compile(pre_c_exitCollection[s]["exitPrice"], "<string>", "eval")


    if data["scanCategory"] == "":
    
        tradeSetup = "intraday_long"
    else:
        tradeSetup = data["scanCategory"] 
    if tradeSetup == "long":
        buysell = "buy"
    elif tradeSetup == "short":
        buysell = "sell"
    elif tradeSetup == "intraday_long":
        buysell = "buy"
    elif tradeSetup == "intraday_short":
        buysell = "sell"

    
    # initial_length = len(df["datetime"])
    
    # result["stock"] = np.empty(initial_length, dtype=object)
    # result["condition"] = np.zeros(initial_length, dtype=bool)  # efficiently stores booleans
    # result["entryDateTime"] = np.empty(initial_length, dtype=object)

    # Tracking = {
    #     'stock': stock_array[:Tracking_index],
    #     'buysell': buysell_array[:Tracking_index],
    #     'entry_date': date_array[:Tracking_index],
    #     'entry_time': entryTime_array[:Tracking_index],
    #     'entry': entry_array[:Tracking_index],
    #     'exit_date': exit_date_array[:Tracking_index],
    #     'exit_time': exitTime_array[:Tracking_index],
    #     'exit': exit_array[:Tracking_index],
    #     'quantity': quantity_array[:Tracking_index],
    #     'pnl': pnl_array[:Tracking_index],
    #     'sl': sl_array[:Tracking_index],
    #     # 'date_number': date_number_array[:Tracking_index],
    # }
    
    # sl_db = TrackingDB()
    is_high_tf      = obj.smallest_tf in {"Daily", "Weekly", "Monthly"}
    is_long_short   = tradeSetup in {"long", "short"}
    is_intraday_mode= not is_high_tf and not is_long_short
    is_intraday_long_short = tradeSetup in {"intraday_long", "intraday_short"}
    flag_entry = 0
    flag_exit = 0

    for i in range(0, len(df["datetime"])):
        
        if df["start_symbol"][i] == 1:
            flag_entry = 0
            flag_exit = 0
        if is_intraday_mode:
            if flag_exit == 0 and df["start"][i] == 1:
                flag_entry = 1
        if (is_high_tf or is_long_short) and flag_entry == 0 and flag_exit == 0:
            flag_entry = 1

        # No entry at last intraday candle
        if is_intraday_mode and df["end"][i] == 1:
            flag_entry = 0
        
        if flag_entry == 1:
            try:
                date_str = str(df["datetime"][i])
                date_str = f"{date_str[0:10]} {date_str[11:19]}"
                # previous_position = sl_db.previous_position(df['symbol'][i], mode = 'count', date = f'{date_str[0:10]}')
                
                if eval(pre_c_entry, globals(), locals()):
                    
                    # date_str = str(df["datetime"][i])
                    # date_str = f"{date_str[0:10]} {date_str[11:19]}"
                    sl_db.insert_entry(datetime = date_str,
                                        symbol= df["symbol"][i],
                                        price= eval(pre_c_entryPrice, globals(), locals()),
                                        quantity= round(eval(pre_c_quantity, globals(), locals()), 0), 
                                        buysell_setup = str(buysell),
                                        label= "Not Defined"  )
                    flag_entry = 0
                    flag_exit = 1
                    
            except Exception as e:
                # print(i)
                # print("ERROR 2", e)
                pass

        elif flag_exit == 1:
            
            for exit_index, exit_item in enumerate(exitCollection):
                if eval(pre_c_exitCollection[exit_index]["exit"], globals(), locals()):
                    
                    date_str = str(df["datetime"][i])
                    date_str = f"{date_str[0:10]} {date_str[11:19]}"
                    sl_db.exit_percentage_quantity(datetime = date_str, 
                             symbol= df["symbol"][i], 
                             price= eval(pre_c_exitCollection[exit_index]["exitPrice"], globals(), locals()) , 
                             label= exit_item["label"], 
                             percentage = 100)
                    flag_exit = 0
                    flag_entry = 1
                    break

            # Universal exit
            if is_intraday_mode and is_intraday_long_short and df["end"][i] == 1 and flag_exit == 1:
                
                date_str = str(df["datetime"][i])
                date_str = f"{date_str[0:10]} {date_str[11:19]}"
                sl_db.exit_percentage_quantity(datetime = date_str, 
                             symbol= df["symbol"][i], 
                             price= df["close"][i], 
                             label= "universal exit", 
                             percentage = 100)
                flag_entry = 0
                flag_exit = 0

        if df["end_symbol"][i] == 1 and flag_exit == 1:
            date_str = str(df["datetime"][i])
            date_str = f"{date_str[0:10]} {date_str[11:19]}"
            sl_db.exit_percentage_quantity(datetime = date_str, 
                             symbol= df["symbol"][i], 
                             price= df["close"][i], 
                             label= "last candle exit", 
                             percentage = 100)
            flag_entry = 0
            flag_exit = 0



    Tracking = sl_db.create_result_table()
    print("backtesting time" , (time.perf_counter_ns() - init)/1000/1000, "ms")   
    print(f"backtesting time/ stock {len(list_stocks)}" , (time.perf_counter_ns() - init)/1000/1000/len(list_stocks) , "ms")   
    # print(Tracking)
    # Tracking.to_csv("Tracking.csv")
    if len(Tracking) > 0:
        Tracking = Tracking.rename(columns={'exit_label': 'sl'})
        Tracking = Tracking.drop(columns=['entry_label'])

    print("Total Time",(time.perf_counter_ns() - init_all)/1000/1000, "ms")
    print("Total Time",(time.perf_counter_ns() - init_all)/1000/1000/1000, "s")
    print(f"Total Time / stock {len(list_stocks)}" ,(time.perf_counter_ns() - init_all)/1000/1000/len(list_stocks), "ms")
    # current, peak = tracemalloc.get_traced_memory()
    # tracemalloc.stop()
    # memory_check = {
    #     "current_memory": f"{current / 10**6:.2f} MB",
    #     "peak_memory": f"{peak / 10**6:.2f} MB"
    # }
    # print("start current_memory",memory_check["current_memory"],"start peak_memory", memory_check["peak_memory"])

    return Tracking
    # return {"data_result": data_compression.compress_json_for_frontend(Tracking.to_json(orient='records'))}
    
    # print(result)
    # Tracking = pd.DataFrame(result)
    # json_data, max_stocks = convert_df_to_json_and_maxstocks(Tracking)
    # print("Max stocks at single timestamp:", max_stocks)
    # print("Time taken total", (time.perf_counter_ns() - init_all)/1000/1000)
    # return {"data_result": data_compression.compress_json_for_frontend(json_data), "max_length" : max_stocks}


    