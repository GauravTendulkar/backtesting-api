
import os
from filelock import FileLock
import pytz
from datetime import datetime
import pandas as pd
from functions_v1 import memory
from functions import df_saving


def fastCache_file_tracking_and_deletion(fileName, unit="Mi", memory_size= 10):
    for i in range(len(fileName)):
        fileName[i] = fileName[i][3]
        
        
    tracking_file_name = "fastCache_file_tracking.csv"
    lock = FileLock(f"{tracking_file_name}.lock")  # Create a lock file

    with lock:  
        if os.path.exists(tracking_file_name):
            df = pd.read_csv(tracking_file_name, low_memory=False, index_col=0)
        else:
            df = pd.DataFrame(columns=["datetime", "fileName"])

        # Get current timestamp as an integer
        current_time = int(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y%m%d%H%M%S"))

        # Convert datetime column to int if not empty
        if not df.empty:
            df["datetime"] = df["datetime"].astype(int)

        # Update timestamp if filename exists, else add a new entry
        for i in range(len(fileName)):
            if fileName[i] in df["fileName"].values:
                df.loc[df["fileName"] == fileName[i], "datetime"] = current_time
            else:
                df = pd.concat([df, pd.DataFrame([{"datetime": current_time, "fileName": fileName[i]}])], ignore_index=True)

        # Sort by datetime (latest first)
        df = df.sort_values(by="datetime", ascending=False).reset_index(drop=True)
        
        while memory.sizeof_fmt(memory.get_folder_size("fastCache"), unit=unit)[0] > memory_size :
            if len(df) == 0:
                break
            # print(df.loc[df.index[-1], "fileName"])
            file_path = f"{df.loc[df.index[-1], "fileName"]}.parquet"
            if os.path.exists(file_path):
            
                os.remove(file_path)
            df = df.drop(df.index[-1])
        
    
        df.to_csv(tracking_file_name, index=True)
    
    try:
        os.remove("fastCache_file_tracking.csv.lock")
        
    except:
        pass
    



def remove_column(stock, tf, column):
    if (column != "close" 
    and column != "high" 
    and column != "low" 
    and column != "open"
    and column != "volume"
    and column != "datetime"
    and column != "date_number"
    and column != "time_number"
    and column != "datetime_number" ):
        if tf == "Daily" or tf == "Weekly" or tf == "Monthly":
            path = f"indicator_process/{stock}_{tf}"
        
        elif 1 <= tf & tf <= 60*5:
            path = f"indicator_process/{stock}_{tf}min"
        if df_saving.if_path_exist(path):
            with df_saving.lock_file(path):
                df = df_saving.read_file(path)
                try:
                    df = df.drop(column, axis=1)
                except:
                    pass
                df_saving.to_file(df, path)
            df_saving.remove_lock(path)
        

# remove_column("INFY", 15, "supertrend_10_3")


def stock_column_file_tracking_and_deletion(fileName, unit="Mi", memory_size=10):
    tracking_file_name = "stock_column_file_tracking.csv"
    lock = FileLock(f"{tracking_file_name}.lock")

    with lock:
        # Define consistent column names
        columns = ["datetime", "stock", "tf", "column"]
        
        if os.path.exists(tracking_file_name):
            df = pd.read_csv(tracking_file_name, low_memory=False, index_col=0)
            # Ensure all required columns exist
            for col in columns:
                if col not in df.columns:
                    df[col] = None
        else:
            df = pd.DataFrame(columns=columns)

        current_time = int(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y%m%d%H%M%S"))

        if not df.empty:
            df["datetime"] = df["datetime"].astype(int)

        for file_info in fileName:
            stock = file_info[0]  # Assuming fileName is list of tuples/lists with 3 elements
            tf = str(file_info[1])
            column = file_info[2]
            # Find matching rows
            mask = (df["stock"] == stock) & (df["tf"] == tf) & (df["column"] == column)
            
            if any(mask):
                # Update existing entry
                df.loc[mask, "datetime"] = current_time
            else:
                # Add new entry
                new_entry = pd.DataFrame([{
                    "datetime": current_time,
                    "stock": stock,
                    "tf": tf,
                    "column": column
                }])
                df = pd.concat([df, new_entry], ignore_index=True)

        df = df.sort_values(by="datetime", ascending=False).reset_index(drop=True)
        # df.to_csv(tracking_file_name)
        # print(df)
        while memory.sizeof_fmt(memory.get_folder_size("indicator_process"), unit=unit)[0] > memory_size :
            if len(df) == 0:
                break
            stock = df.loc[df.index[-1], "stock"]
            try:
                tf = int(df.loc[df.index[-1], "tf"])
            except:
                tf = df.loc[df.index[-1], "tf"]
            column = df.loc[df.index[-1], "column"]
            remove_column(stock, tf, column)
            df = df.drop(df.index[-1])
        # print(df)
        # # Save updated file list
        df.to_csv(tracking_file_name, index=True)
    try:
        os.remove("stock_column_file_tracking.csv.lock")
        
    except:
        pass

# stock_column_file_tracking_and_deletion(column_exist , unit="Mi", memory_size= 10)