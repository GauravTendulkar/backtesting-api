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

def calculate_cpu():

    num_cpus = os.cpu_count()
    
    return num_cpus


def execute_backtesting_logic(df, date_start, date_end,  entry, list_stocks, t, entryPrice, exitCollection, quantity, dict_of_timeframes, dict_of_time, df_time, smallest):
    
    Tracking = pd.DataFrame()
    Tracking['stock'] = ''
    Tracking['buysell'] =""
    Tracking['date'] =""
    Tracking['entryTime'] = ''
    Tracking['entry'] = 0.0
    Tracking['exit_date'] =""
    Tracking['exitTime'] = ''
    Tracking['exit'] = 0.0
    Tracking['quantity'] = 0.0
    Tracking['pnl'] = 0.0
    Tracking['sl'] = ''
    
    flag_entry = 0
    flag_exit = 0
    for i in range(date_start, date_end):
            
        
        if True:
            if  df.loc[df.index[i], "time_number"] == 91500:
                flag_entry = 1
            
            if flag_entry ==  1:
                # print("yes)")
                entry_t = backtesting_functions.select_candles('time_number', df['datetime_number'].iloc[i] ,dict_of_timeframes[smallest], dict_of_time[smallest], smallest,0 )
                
                try:
                    
                    if ( eval(entry) ):
                        
                        Tracking = pd.concat([Tracking, pd.DataFrame([{
                        'stock': str(list_stocks[t]),
                        'buysell': 'buy',
                        'date': f'{str(df.loc[df.index[i], "date_number"])[0:4]}-{str(df.loc[df.index[i], "date_number"])[4:6]}-{str(df.loc[df.index[i], "date_number"])[6:8]}',
                        'entry':  eval(entryPrice),#backtesting_functions.select_candles('close', df['datetime_number'].iloc[i] ,dict_of_timeframes[15], dict_of_time[15], 15,0 ), 
                        'entryTime': f'{str(entry_t)[-6:-4]}:{str(entry_t)[-4:-2]}',
                        'exit_date' :"",
                        'exit':0,
                        'exitTime':'',
                        'quantity': round( eval(quantity) ,0), 
                        'pnl':0,
                        'sl':'',
                        
                        
                    }])],ignore_index=True)
                        
                        flag_entry = 0
                        flag_exit = 1
                except Exception as e:
                    # print(e)
                    pass
            elif flag_exit == 1:
                exit_t = backtesting_functions.select_candles('time_number', df['datetime_number'].iloc[i] ,dict_of_timeframes[smallest], dict_of_time[smallest], smallest,0 )
                
                for exitCollection_index in range(len(exitCollection)):
                    # print("len(exitCollection)", eval(exitCollection[i]["exit"]))
                    if eval(exitCollection[exitCollection_index]["exit"]):
                        Tracking.loc[Tracking.index[-1], 'exit'] = eval(exitCollection[exitCollection_index]["exitPrice"])  #float(Tracking.loc[Tracking.index[-1], 'entry'] *(1-0.015*1))
                        Tracking.loc[Tracking.index[-1], 'exitTime'] = f'{str(exit_t)[-6:-4]}:{str(exit_t)[-4:-2]}'
                        Tracking.loc[Tracking.index[-1], 'sl'] = exitCollection[exitCollection_index]["label"]
                        Tracking.loc[Tracking.index[-1], 'exit_date'] = f'{str(df.loc[df.index[i], "date_number"])[0:4]}-{str(df.loc[df.index[i], "date_number"])[4:6]}-{str(df.loc[df.index[i], "date_number"])[6:8]}'
                        flag_exit = 0
                        flag_entry = 0
                        # print("break")
                        break
                # universal exit
                # print(df.loc[df.index[i], "time_number"])
                if  df.loc[df.index[i], "time_number"] == df_time and flag_exit == 1:
                    # print("hey")
                    Tracking.loc[Tracking.index[-1], 'exit'] = float(backtesting_functions.select_candles('close', df['datetime_number'].iloc[i] ,dict_of_timeframes[smallest], dict_of_time[smallest], smallest,0 )  )
                    Tracking.loc[Tracking.index[-1], 'exitTime'] = f'{str(df.loc[df.index[i], "time_number"])[-6:-4]}:{str(df.loc[df.index[i], "time_number"])[-4:-2]}'
                    Tracking.loc[Tracking.index[-1], 'sl'] = 'universal exit'
                    Tracking.loc[Tracking.index[-1], 'exit_date'] = f'{str(df.loc[df.index[i], "date_number"])[0:4]}-{str(df.loc[df.index[i], "date_number"])[4:6]}-{str(df.loc[df.index[i], "date_number"])[6:8]}'    
                    flag_entry = 0
                    flag_exit = 0
    
    return Tracking


def execute_backtesting_logic_args(args):
    return execute_backtesting_logic(*args)

def long_running_3(data):
    print("long_running_3")
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
    current, peak = tracemalloc.get_traced_memory()
    memory_check = {
        "current_memory": f"{current / 10**6:.2f} MB",
        "peak_memory": f"{peak / 10**6:.2f} MB"
    }
    print("start current_memory",memory_check["current_memory"],"start peak_memory", memory_check["peak_memory"])

    initial_time = time.time()
    list_stocks = [
                "AARTIIND", 
                "ABB", 
                "ABCAPITAL", 
                "ABFRL",
                "ACC"
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

    stocks, timeframes, params, arr = zip(*combine_iter_list)
    # print(stocks, timeframes)
    
    with concurrent.futures.ProcessPoolExecutor(calculate_cpu()) as executor:
        
        executor.map(controller.apply_indicators, stocks, timeframes, params, arr)


    
# #________________________________________
# # 
    csv_import = backtesting_functions.convert_data_for_csv_loading(combine_iter_list)
    # print("csv_import")
    # print(csv_import)
    date_start = backtesting_functions.date_str_to_int(data['dateRange']["from"])
    date_end = backtesting_functions.date_str_to_int(data['dateRange']["to"])
    print("date_start", date_start, "date_end" , date_end)
    entry = backtesting_functions.entry_to_equation([data["entry"]] , None)
    # print("entry")
    # print(entry)
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

    # Tracking = pd.DataFrame()
    # Tracking['stock'] = ''
    # Tracking['buysell'] =""
    # Tracking['date'] =""
    # Tracking['entryTime'] = ''
    # Tracking['entry'] = 0.0
    # Tracking['exit_date'] =""
    # Tracking['exitTime'] = ''
    # Tracking['exit'] = 0.0
    # Tracking['quantity'] = 0.0
    # Tracking['pnl'] = 0.0
    # Tracking['sl'] = ''
    
    #___________________________________________________________________
    for t in range(0,len(list_stocks)):
        dict_of_timeframes, dict_of_time = backtesting_functions.get_csv_dict(list_stocks[t], csv_import)
        # print(dict_of_timeframes)
        # print(dict_of_time)
        numeric_values = [x for x in list((dict_of_timeframes.keys())) if isinstance(x, (int, float))]
        # print("numeric_values")
        # print(numeric_values)
        if numeric_values:  # Check if there are any numeric values
            smallest = min(numeric_values)
            # print(f"The smallest number is: {smallest}")

        path = f"indicator_process/{list_stocks[t]}_{smallest}min.csv"
        df = pd.read_csv(path,low_memory=False,parse_dates=['datetime'],index_col=['datetime'], usecols=['datetime', 'datetime_number', 'date_number', 'time_number'])
        
        path_time = f"Clean_data/uniqueTime_{smallest}.csv"
        df_time = pd.read_csv(path_time,low_memory=False,index_col=[0])
        df_time = df_time[f"uniqueTime_{smallest}"].iloc[-1]
        df_time = int("".join(df_time.split(":")))
        # print("df_time", df_time)
        

        
        # print("date_start", df.index.get_loc(df.loc[df["date_number"]  == date_start].index.tolist()[0]))

        # print("date_end", df.index.get_loc(df.loc[df["date_number"]  == date_end].index.tolist()[-1]))
        try:
            date_start = df.index.get_loc(df.loc[df["date_number"]  == date_start].index.tolist()[0])
            # print("date_start", date_start)
        except:
            date_start = 0
        try:
            date_end = df.index.get_loc(df.loc[df["date_number"]  == date_end].index.tolist()[-1])
            # print("date_end", date_end)
        except:
            # print("ERROR date_end")
            
            date_end = len(df)-1
            # print(date_end)

        

        def divide_range(t1, t2, parts):
            result = int(math.ceil((t2-t1)/parts))
            temp = []
            for i in range(parts + 1):
                # print(i)
                if i == 0:
                    temp.append(t1)
                elif 0 < i and i < parts:
                    temp.append(t1 + result*i)
                elif i == parts:
                    temp.append(t2)
            # print("temp", temp)
            for i in range(1, len(temp)):
                # print("temp", temp[i])
                # print(df.loc[df.index[temp[i]], "time_number"])
                loop = True
                while loop:
                    
                    if df.loc[df.index[temp[i]], "time_number"] == df_time:
                        # print( "if", df.loc[df.index[temp[i]], "time_number"])
                        loop = False
                    if loop :
                        temp[i] = temp[i] + 1
            temp_arr = []
            for i in range(1, len(temp)):
                
                temp_arr.append([temp[i-1], temp[i]])
            
            
            param1, param2 = zip(*temp_arr)

            return param1, param2
        
        
        
        # print(divide_range(date_start, date_end, 2))
        data_start_index, data_end_index = divide_range(date_start, date_end, 2)
        # print("hello ************************************** hello")
        # print(data_start_index)
        # temp = []
        # for h in range(0, len(data_start_index)):
        #     temp.append([df, entry, list_stocks, t, entryPrice, exitCollection, quantity, dict_of_timeframes, dict_of_time, df_time, smallest])

        # df, entry, list_stocks, t, entryPrice, exitCollection, quantity, dict_of_timeframes, dict_of_time, df_time, smallest = zip(*temp)

        # print("t", t)

        args = [
    (
        df,
        data_start_index[i],
        data_end_index[i],
        entry,
        list_stocks,
        t,
        entryPrice,
        exitCollection,
        quantity,
        dict_of_timeframes,
        dict_of_time,
        df_time,
        smallest
    )
    for i in range(len(data_start_index))
]
        
       # Execute the tasks using ProcessPoolExecutor
        Tracking = pd.DataFrame()
        with concurrent.futures.ProcessPoolExecutor() as executor:
            try:
                # Use map with a standalone function
                results = executor.map(execute_backtesting_logic_args, args)
                
                # Combine all results into the Tracking DataFrame
                for result in results:
                    Tracking = pd.concat([Tracking, result], ignore_index=True)
            except Exception as e:
                # print(f"An error occurred: {e}")
                Tracking = pd.DataFrame()  # Handle errors gracefully


    for i in range(0, len(Tracking)):
        if Tracking.loc[Tracking.index[i], 'buysell'] == 'buy':
            Tracking.loc[Tracking.index[i], 'pnl'] = (Tracking.loc[Tracking.index[i], 'exit'] - Tracking.loc[Tracking.index[i], 'entry'] )* Tracking.loc[Tracking.index[i], 'quantity']

        if Tracking.loc[Tracking.index[i], 'buysell'] == 'sell':
            Tracking.loc[Tracking.index[i], 'pnl'] = (Tracking.loc[Tracking.index[i], 'entry'] - Tracking.loc[Tracking.index[i], 'exit'] )* Tracking.loc[Tracking.index[i], 'quantity']    
      
    
    print("time taken", (time.time() - initial_time))
    current, peak = tracemalloc.get_traced_memory()
    
    tracemalloc.stop()
    memory_check = {
        "current_memory": f"{current / 10**6:.2f} MB",
        "peak_memory": f"{peak / 10**6:.2f} MB"
    }
    print("current_memory",memory_check["current_memory"],"peak_memory", memory_check["peak_memory"])
    # print("Tracking")
    # print()

    

    Tracking.to_csv("Tracking.csv")
    # print(Tracking.to_json(orient='records'))
    print("Finised")
    return {"data_result":Tracking.to_json(orient='records')}
    # # return {"Hello": "World"}