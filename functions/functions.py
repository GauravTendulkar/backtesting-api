import pandas as pd
from functions import functions
import numpy as np
from datetime import date,datetime
import math
import numba
import pytz
import os
from filelock import FileLock
from dateutil.relativedelta import relativedelta
from fastapi import HTTPException

def timeframe_divide_uniqueTime(n):
    try:
        uniqueTime_temp = pd.read_csv('Clean_data/uniqueTime_'+str(n)+".csv",low_memory=False,index_col=[0])
        return uniqueTime_temp
    except:
        
        uniqueTime = pd.read_csv("Clean_data/uniqueTime.csv",low_memory=False,index_col=[0])
        uniqueTime_temp = pd.DataFrame()
        for i in range(1, 376, n):
            # print(uniqueTime.loc[uniqueTime.index[i],'uniqueTime'])
            uniqueTime_temp = pd.concat([uniqueTime_temp, pd.DataFrame([{'uniqueTime_'+str(n): uniqueTime.loc[uniqueTime.index[i],'uniqueTime'] }])],ignore_index=True)
            uniqueTime_temp.to_csv('Clean_data/uniqueTime_'+str(n)+".csv")
        return uniqueTime_temp
    


# import math
# import numpy as np
# a = 123
# b = np.array([1, 2, 4, 10])
# print(math.ceil(a))
# print(math.floor(a))
# print(math.fabs(a))
# print(math.log10(a))
# print(math.log(a))

def ceil(data):
    return math.ceil(data)

def floor(data):
    return math.floor(data)

def abs(data):
    return math.fabs(data)

def log10(data):
    return math.log10(data)

def log(data):
    return math.log(data)


def count_previous_entry_intraday(Tracking, date):
        return (Tracking["date_number"] == date).sum()





def latest_file(fileName, length = 100):
    file_name = "indicator_process/fast_cache/_latest_file.csv"
    lock = FileLock(f"{file_name}.lock")  # Create a lock file

    with lock:  # Ensure only one thread accesses the file at a time
        os.makedirs(os.path.dirname(file_name), exist_ok=True)

        # Load existing CSV or create an empty DataFrame
        if os.path.exists(file_name):
            df = pd.read_csv(file_name, low_memory=False, index_col=0)
        else:
            df = pd.DataFrame(columns=["datetime", "fileName"])

        # Get current timestamp as an integer
        current_time = int(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y%m%d%H%M%S"))

        # Convert datetime column to int if not empty
        if not df.empty:
            df["datetime"] = df["datetime"].astype(int)

        # Update timestamp if filename exists, else add a new entry
        if fileName in df["fileName"].values:
            df.loc[df["fileName"] == fileName, "datetime"] = current_time
        else:
            df = pd.concat([df, pd.DataFrame([{"datetime": current_time, "fileName": fileName}])], ignore_index=True)

        # Sort by datetime (latest first)
        df = df.sort_values(by="datetime", ascending=False).reset_index(drop=True)

        # Identify old files to delete if they exceed the length limit
        if len(df) >= length:
            files_to_delete = df.iloc[length:]["fileName"].tolist()
            df = df.iloc[:length]  # Keep only the latest 'length' records

            # Delete the old CSV files
            for file in files_to_delete:
                file_path = f"indicator_process/fast_cache/{file}.csv"
                if os.path.exists(file_path):
                    os.remove(file_path)  # Delete only the extra older files
        
        # Save updated file list
        df.to_csv(file_name, index=True)
        # time.sleep(5)
        # print(df)

def get_smallest_tf(data):
    get_smallest_tf = []
    for i in range(0, len(data)):
        if isinstance(data[i][1], int):
            get_smallest_tf.append(data[i][1])
    if len(get_smallest_tf) > 0:
        get_smallest_tf = min(get_smallest_tf)
    else:
        for i in range(0, len(data)):
            if isinstance(data[i][1], str):
                get_smallest_tf.append(data[i][1])
        if len(get_smallest_tf) > 0:
            if "Daily" in get_smallest_tf :
                get_smallest_tf = "Daily"
            elif "Weekly" in get_smallest_tf :
                get_smallest_tf = "Weekly"
            elif "Monthly" in get_smallest_tf :
                get_smallest_tf = "Monthly"
    return get_smallest_tf 


def check_tf_range(tf, start_date, end_date):
    date_format = "%Y-%m-%d"
    try:
        start = datetime.strptime(start_date, date_format)
        end = datetime.strptime(end_date, date_format)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    
    # print(end - relativedelta(years=3))
    # print(end - relativedelta(months=3) >= start)
    
    limit = {
        1 : end - relativedelta(months=6),
        2 : end - relativedelta(months=6),
        3 : end - relativedelta(months=6),
        5 : end - relativedelta(years=1),
        10 : end - relativedelta(years=10),
        15 : end - relativedelta(years=10),
        30 : end - relativedelta(years=5),
        60 : end - relativedelta(years=5),
        120 : end - relativedelta(years=10),
        180 : end - relativedelta(years=10),
        240 : end - relativedelta(years=10),
        "Daily" : end - relativedelta(years=10),
        "Weekly" : end - relativedelta(years=10),
        "Monthly" : end - relativedelta(years=10),

    }

    # print("tf ************", tf)

    if limit[tf] <= start:
        pass
    else:
        # raise HTTPException(status_code=400, detail="Date range exceeds the allowed limit of 1 year.")
        raise HTTPException(
            status_code=400,
            detail=f"Date range exceeds the allowed limit for timeframe '{tf}'. "
                   f"Minimum allowed start date: {limit[tf].strftime('%d-%m-%Y')}"
        )
    

def check_stock_files_if_exists(stocks_list):
    stocks_list_temp = []

    files = [f for f in os.listdir('Clean_data/1min') if os.path.isfile(os.path.join('Clean_data/1min', f))]
    temp_1min = []
    for i in range(0, len(files)):
        temp_1min.append(files[i].split("_")[0])

    # print(temp_1min)
    temp_Daily = []
    files = [f for f in os.listdir('Clean_data/RAW_daily_data_tradingview') if os.path.isfile(os.path.join('Clean_data/RAW_daily_data_tradingview', f))]
    for i in range(0, len(files)):
        temp_Daily.append(files[i].split("_")[0])
    # print(temp_Daily)

    for i in range(0, len(stocks_list)):
        
        if stocks_list[i] in temp_1min:
            stocks_list_temp.append(stocks_list[i])

    for i in range(0, len(stocks_list)):
        
        if stocks_list[i] in temp_Daily:
            if stocks_list[i] not in stocks_list_temp:
                stocks_list_temp.append(stocks_list[i])
    
    return stocks_list_temp