
import pandas as pd
import numpy as np
from functions import timeframe, indicators
import os
from filelock import FileLock
from functions import df_saving

indicator_folder_path = "functions_duckdb/indicator_files"
os.makedirs(f"{indicator_folder_path}", exist_ok=True)


def min_to_hour(df, data):
    input = {
        1 : '1min',
        2: '2min',
        3: '3min',
        5: '5min',
        10: '10min',
        15: '15min',
        30: '30min',
        60: '1h',
        120: '2h',
        180: '3h',
        240: '4h',

    }
    data_15m = df.resample(
        input[data],
        offset='9h15min'
    ).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume' : 'sum'
    })

    data_15m = data_15m.dropna(subset=['open', 'high', 'low', 'close', 'volume'])

    return data_15m


def change_into_any_timeframe(stock, timeframe_value):

    # stock = "AARTIIND"
    # timeframe_value = 1
    # print(f"started {timeframe_value}")

    if timeframe_value == "Daily":
        
        from_ = f"Clean_data/RAW_daily_data_tradingview/{stock}_{"Daily"}"
        to_ = f"{indicator_folder_path}/{stock}_{"Daily"}"
        
        
        with df_saving.lock_file(to_):
            if df_saving.if_path_exist(to_):
                pass
            else:
                # print(f"inlock {timeframe_value}")
                df = df_saving.read_file(from_, extension=".csv")
                df["symbol"] = stock
                df = timeframe.timeframe_Daily(df)
                # df = indicators.convert_date_time_datetime_into_numbers_Daily(df)
                df = indicators.convert_date_time_datetime_into_numbers(df)
                
                df_saving.to_file(df, to_)
        df_saving.remove_lock(to_)
        # print(f"outlock {timeframe_value}")
        
    elif timeframe_value == "Weekly" or timeframe_value == "Monthly":
        from_ = f"{indicator_folder_path}/{stock}_{"Daily"}"
        to_ = f"{indicator_folder_path}/{stock}_{timeframe_value}"

        
        with df_saving.lock_file(to_):
            if df_saving.if_path_exist(to_) == False:
                if df_saving.if_path_exist(from_) == False:
                    change_into_any_timeframe(stock, "Daily")
                
                df = df_saving.read_file(from_)
                df = timeframe.convert_daily_weekly_and_monthly(df, timeframe_value)
                df = indicators.convert_date_time_datetime_into_numbers(df)
                
                df_saving.to_file(df, to_)

        df_saving.remove_lock(to_)

    elif timeframe_value == 1:
        
        from_ = "Clean_data/1min/"+str(stock)+"_"+str(timeframe_value)+"min"
        to_ = f"{indicator_folder_path}/"+str(stock)+ "_"+str(timeframe_value)+"min"
        
        
        
        with df_saving.lock_file(to_):
            if df_saving.if_path_exist(to_):
                pass
            else:
                # print(f"inlock {timeframe_value}")
                df = df_saving.read_file(from_, extension=".csv")
                df["symbol"] = stock
                # df  = timeframe.timeframe_1min(df)
                df  =  min_to_hour(df, timeframe_value)
                # df = indicators.convert_date_time_datetime_into_numbers(df)
                
                df_saving.to_file(df, to_)
        # print(f"outlock {timeframe_value}")
        df_saving.remove_lock(to_)
    elif 60*5 >= timeframe_value and timeframe_value > 1:

        from_ = f"{indicator_folder_path}/"+str(stock)+"_"+str(1)+"min"
        to_ = f"{indicator_folder_path}/"+str(stock)+ "_"+str(timeframe_value)+"min"
        
        # print("Working")
        
        with df_saving.lock_file(to_):
            if df_saving.if_path_exist(to_):
                pass
            else:
                # print(f"inlock {timeframe_value}")
                try:
                    df = df_saving.read_file(from_)
                    # print("hello")
                except:
                    df = df_saving.read_file("Clean_data/1min/"+str(stock)+"_"+str(1)+"min", extension=".csv")
                    # df["symbol"] = stock
                    # print(df)
                    change_into_any_timeframe(stock, 1)
                    
                    
                    # print("1 min tf created")
                    
                    
                    df = df_saving.read_file(from_)
                    

                # df["symbol"] = stock
                # df  = timeframe.convert_1min_anymin(df, timeframe_value)
                df  =  min_to_hour(df, timeframe_value)
                # print(f"{timeframe_value} min tf created")
                # df = indicators.convert_date_time_datetime_into_numbers(df)
                
                df_saving.to_file(df, to_)
        # print(f"outlock {timeframe_value}") 
    # print(f"Ended {timeframe_value}")
        df_saving.remove_lock(to_)




def apply_indicators(stock, timeframe_value ,shortform_indicator, arr):

    if timeframe_value == "Daily" or timeframe_value == "Weekly" or timeframe_value == "Monthly":
        path = f"{indicator_folder_path}/{stock}_{timeframe_value}"
    
    elif 1 <= timeframe_value and timeframe_value <= 60*5:
        path = f"{indicator_folder_path}/{stock}_{timeframe_value}min"
    
    # print(path)  
    # print(stock, timeframe_value ,shortform_indicator, arr)

    if df_saving.if_path_exist(path) :
        # print(df_saving.if_path_exist(path), path)
        df_list = df_saving.get_columns(path)
        
        if shortform_indicator not in df_list:
            with df_saving.lock_file(path):
                
                df = df_saving.read_file(path)
                
                if shortform_indicator not in df.columns:

                    df = indicators.get_indicator_shortform(df, arr, 1)      
                    df_saving.to_file(df, path)
            df_saving.remove_lock(path)
            
    else:
        change_into_any_timeframe(stock, timeframe_value)
        # apply_indicators(stock,timeframe_value ,shortform_indicator, arr)



def is_column_present(stock, timeframe_value ,shortform_indicator):
    # print("timeframe_value________________________", timeframe_value, type(timeframe_value))
    if timeframe_value == "Daily" or timeframe_value == "Weekly" or timeframe_value == "Monthly":
        path = f"{indicator_folder_path}/{stock}_{timeframe_value}"
    
    elif 1 <= timeframe_value and timeframe_value <= 60*5:
        path = f"{indicator_folder_path}/"+str(stock)+ "_"+str(timeframe_value)+"min"
    
        
    
    if df_saving.if_path_exist(path):
        
        df_list = df_saving.get_columns(path)
        
        if shortform_indicator not in df_list:
            return False
        else:
            return True
    else:
        return False

def check_column_present(arr_list):
    temp = []
    for i in range(0, len(arr_list)):
        if is_column_present(arr_list[i][0], arr_list[i][1] ,arr_list[i][2]) == False:
            temp.append(arr_list[i])
    # print("check_column_present",temp)
    return temp