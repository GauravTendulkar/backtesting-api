import pandas as pd
import numpy as np
from functions import timeframe, indicators
import os
from filelock import FileLock

## Following function is use to combine other timeframe functions and to run under a single function 

def change_into_any_timeframe(stock, timeframe_value):

    # stock = "AARTIIND"
    # timeframe_value = 1
    # print(f"started {timeframe_value}")

    if timeframe_value == "Daily":
        
        from_ = f"Clean_data/RAW_daily_data_tradingview/{stock}_{"Daily"}.csv"
        to_ = f"indicator_process/{stock}_{"Daily"}.csv"
        
        lock_path = to_ + ".lock"
        lock = FileLock(lock_path)
        with lock:
            if os.path.exists(to_):
                pass
            else:
                # print(f"inlock {timeframe_value}")
                df = pd.read_csv(from_,low_memory=False,parse_dates=['datetime'],index_col=['datetime'])
                df["symbol"] = stock
                df = timeframe.timeframe_Daily(df)
                # df = indicators.convert_date_time_datetime_into_numbers_Daily(df)
                df = indicators.convert_date_time_datetime_into_numbers(df)
                df.to_csv(to_)
        # print(f"outlock {timeframe_value}")
        
    elif timeframe_value == "Weekly" or timeframe_value == "Monthly":
        from_ = f"indicator_process/{stock}_{"Daily"}.csv"
        to_ = f"indicator_process/{stock}_{timeframe_value}.csv"

        lock_path = to_ + ".lock"
        lock = FileLock(lock_path)
        with lock:
            if os.path.exists(to_) == False:
                if os.path.exists(from_) == False:
                    change_into_any_timeframe(stock, "Daily")
                
                df = pd.read_csv(from_,low_memory=False,parse_dates=['datetime'],index_col=['datetime'])
                df = timeframe.convert_daily_weekly_and_monthly(df, timeframe_value)
                df = indicators.convert_date_time_datetime_into_numbers(df)
                df.to_csv(to_)



    elif timeframe_value == 1:
        
        from_ = "Clean_data/1min/"+str(stock)+"_"+str(timeframe_value)+"min.csv"
        to_ = "indicator_process/"+str(stock)+ "_"+str(timeframe_value)+"min.csv"
        # df = pd.DataFrame()
        # df.to_csv(to_)
        lock_path = to_ + ".lock"
        lock = FileLock(lock_path)
        with lock:
            if os.path.exists(to_):
                pass
            else:
                # print(f"inlock {timeframe_value}")
                df = pd.read_csv(from_,low_memory=False,parse_dates=['datetime'],index_col=['datetime'])
                df["symbol"] = stock
                df  = timeframe.timeframe_1min(df)
                df = indicators.convert_date_time_datetime_into_numbers(df)
                df.to_csv(to_)
        # print(f"outlock {timeframe_value}")

    elif 60*5 >= timeframe_value and timeframe_value > 1:

        from_ = "indicator_process/"+str(stock)+"_"+str(1)+"min.csv"
        to_ = "indicator_process/"+str(stock)+ "_"+str(timeframe_value)+"min.csv"
        # df = pd.DataFrame()
        # df.to_csv(to_)
        lock_path = to_ + ".lock"
        lock = FileLock(lock_path)
        with lock:
            if os.path.exists(to_):
                pass
            else:
                # print(f"inlock {timeframe_value}")
                try:
                    df = pd.read_csv(from_,low_memory=False,parse_dates=['datetime'],index_col=['datetime'])
                except:
                    df = pd.read_csv("Clean_data/1min/"+str(stock)+"_"+str(1)+"min.csv",low_memory=False,parse_dates=['datetime'],index_col=['datetime'])
                    df["symbol"] = stock
                    
                    change_into_any_timeframe(stock, 1)
                    # print("1 min tf created")
                    # df.to_csv(from_)
                    
                    df = pd.read_csv(from_,low_memory=False,parse_dates=['datetime'],index_col=['datetime'])
                    

                df["symbol"] = stock
                df  = timeframe.convert_1min_anymin(df, timeframe_value)
                # print(f"{timeframe_value} min tf created")
                df = indicators.convert_date_time_datetime_into_numbers(df)
                df.to_csv(to_)
        # print(f"outlock {timeframe_value}")
    # print(f"Ended {timeframe_value}")

    

#__________________________________________________________
#
#
def apply_indicators(stock, timeframe_value ,shortform_indicator, arr):

    if timeframe_value == "Daily" or timeframe_value == "Weekly" or timeframe_value == "Monthly":
        path = f"indicator_process/{stock}_{timeframe_value}.csv"
    
    elif 1 <= timeframe_value & timeframe_value <= 60*5:
        path = f"indicator_process/"+str(stock)+ "_"+str(timeframe_value)+"min.csv"
    
        

    if os.path.exists(path):
        # df = pd.read_csv(path,low_memory=False,parse_dates=['datetime'],index_col=['datetime'])
        df_list = pd.read_csv(path, nrows=0).columns.tolist()

        if shortform_indicator not in df_list:
        
            lock_path = path + ".lock"
            lock = FileLock(lock_path)
            with lock:
                df = pd.read_csv(path,low_memory=False,parse_dates=['datetime'],index_col=['datetime'])
                # print("df.columns")
                # print(shortform_indicator)
                if shortform_indicator not in df.columns:
                    # print(arr)
                    # print("indicator not in df.columns", shortform_indicator)
                    
                    df = indicators.get_indicator_shortform(df, arr, 1)
                    # print(df)
                    # df = indicators.sma_generator(df, arr[1], arr[2])
                    df.to_csv(path)
            
    else:
        
        change_into_any_timeframe(stock, timeframe_value)
        apply_indicators(stock,timeframe_value ,shortform_indicator, arr)

# fastest way to check the columns if exists_________________________________________

def is_column_present(stock, timeframe_value ,shortform_indicator):

    if timeframe_value == "Daily" or timeframe_value == "Weekly" or timeframe_value == "Monthly":
        path = f"indicator_process/{stock}_{timeframe_value}.csv"
    
    elif 1 <= timeframe_value & timeframe_value <= 60*5:
        path = f"indicator_process/"+str(stock)+ "_"+str(timeframe_value)+"min.csv"
    
        

    if os.path.exists(path):
        # df = pd.read_csv(path,low_memory=False,parse_dates=['datetime'],index_col=['datetime'])
        df_list = pd.read_csv(path, nrows=0).columns.tolist()

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
    return temp
    
    
    



