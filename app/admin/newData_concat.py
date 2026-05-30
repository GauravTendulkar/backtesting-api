import pandas as pd
import numpy as np
from pathlib import Path
# from functions import df_saving, timeframe, indicators, json_saving
import concurrent.futures
from filelock import FileLock
import os
from ..backtesting_duckdb import CLEAN_DATA_1MIN, CLEAN_DATA_DAILY, CLEAN_NEW_DATA

def concat_df(old_df, new_df):
    for i in range(1, 100):
        try:
            match_position = new_df.index.get_loc(old_df.index[-i])
            # Slice new_df from the next index after match_position to the end
            
            new_df_slice = new_df.iloc[match_position + 1:]
            
            old_df_slice = old_df.loc[:old_df.index[-i]]
           
            
            # Concatenate df with the new slice
            result_df = pd.concat([old_df_slice, new_df_slice], axis=0)
            
            return result_df

        except KeyError:
            # If the index is not found, you might want to either append all of new_df or handle it differently
            # print(f"Index {old_df.index[-1]} not found in new_df. Appending all of new_df.")
            # result_df = pd.concat([old_df, new_df], axis=0)
            pass
    return old_df

    



def group_data(data):
    # Create a dictionary to store grouped results
    grouped = {}
    
    # Iterate through each row in the input data
    for row in data:
        # Create a tuple of first two elements as key
        key = tuple(row[:2])
        
        # If key doesn't exist, initialize an empty list
        if key not in grouped:
            grouped[key] = []
        
        # Append the sublist from index 3
        grouped[key].append(row[3])
    
    # Convert dictionary to desired list format
    result = []
    for key, value in grouped.items():
        # Create output row: [symbol, timeframe, None, combined_lists]
        result.append([key[0], key[1], value])
    
    return result




def list_files(folder_path):
    """Returns a list of files in the given folder."""
    path = Path(folder_path)
    if not path.exists():
        return f"Error: The folder '{folder_path}' does not exist."
    files = [file.name for file in path.iterdir() if file.is_file()]
    
    files = [file for file in files if "1min" in file]

    return [file.split("_")[0] for file in files]





# def temp_concat_any_timeframe(res):
#             # It can optionally return a value if needed
#     return concat_any_timeframe(res[0], res[1], res[2])

# def run_once_combined():
#     location = "Clean_data/df_columns_exists.json"
#     with json_saving.lock_file(location):
#         stock_list = list_files("Clean_data/newData")
#         print(stock_list)
#         if len(stock_list) == 0:
#             print("No files found in the directory.")
#             return
#         # for stock in stock_list:
#         #     clean_data_concat(stock)
#         # for stock in stock_list:
#         #     cleanData_to_1min_Daily(stock)
#         with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
            
#             executor.map(clean_data_concat, stock_list)
#         with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
            
#             executor.map(cleanData_to_1min_Daily, stock_list)
#         try :
#             loaded_data = json_saving.load_data_thread_safe(location)
#             result = group_data(loaded_data)

#             # for i in range(0, len(result)):
#             #     concat_any_timeframe( result[i][0], result[i][1], result[i][2])
            

            
            
#             with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
        
#                 executor.map(temp_concat_any_timeframe, result)
#             #     results = list(executor.map(temp_concat_any_timeframe, result))
#         except:
#             print("ERROR")
#             pass



def get_dataframe_file_names(folder_name):
    # List all files and directories in a path
    files = os.listdir(folder_name)  # Replace with your path

    files_new = []
    for i in range(0, len(files)):
        if ".csv" in files[i] or ".parquet" in files[i] or ".feather" in files[i] or ".pickle" in files[i]:
            split_name = files[i].split(".")[0].split("_")
            if "min" in split_name[1]:

                files_new.append([split_name[0] , int(split_name[1][:-3])])
            else:
                files_new.append([split_name[0] , split_name[1]])

    return files_new

# def run_once_combined():
#     file_path = "wait_for_update"
#     lock_path = file_path + ".lock"
#     lock = FileLock(lock_path)

#     with lock:
#         stock_list = list_files("Clean_data/newData")
#         # print(stock_list)
#         if len(stock_list) == 0:
#             print("No files found in the directory.")
#             return
       
#         # with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
            
#         #     executor.map(clean_data_concat, stock_list)
#         # with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
            
#         #     executor.map(cleanData_to_1min_Daily, stock_list)

#         for i in range(0, len(stock_list)):
#             clean_data_concat(stock_list[i])
#         # for i in range(0, len(stock_list)):
#         #     cleanData_to_1min_Daily(stock_list[i])


#         files_list = get_dataframe_file_names("indicator_process")
#         for i in range(0, len(files_list)):
#             try:
#                 concat_any_timeframe_delete_indicators(files_list[i][0], files_list[i][1])
#             except:
#                 print("ERROR", files_list[i])
#         # try :
#         #     # loaded_data = json_saving.load_data_thread_safe(location)
#         #     # result = group_data(loaded_data)

#         #     with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
        
#         #         executor.map(temp_concat_any_timeframe, result)
            
#         # except:
#         #     print("ERROR")
            

       
        

# from functions import newData_concat
# run_once_combined()



def list_files_new_data(folder_path):
    """Returns a list of files in the given folder."""
    path = Path(folder_path)
    if not path.exists():
        return f"Error: The folder '{folder_path}' does not exist."
    files = [file.name for file in path.iterdir() if file.is_file()]
    # print(files)
    one_min_tf = []
    daily_tf = []
    for i in range(0, len(files)):
        extension = ""
        if ".csv" in files[i]:
            extension = "csv"
        elif ".parquet" in files[i]:
            extension = "parquet"

        if "1min" in files[i]:
            one_min_tf.append({"tf" : "1min", "stock" : files[i][0 : files[i].find("_1min")], "extension" : extension})
        elif "Daily" in files[i]:
            daily_tf.append({"tf" : "Daily", "stock" : files[i][0 : files[i].find("_Daily")], "extension" : extension})
    
    # files = [file for file in files if "1min" in file]

    return one_min_tf, daily_tf

import duckdb
import pandas as pd

def run_once_combined_duckdb_helper(stock, 
                                    tf = "1min", 
                                    extension_old = "parquet",
                                    extension_new = "parquet", 
                                    extension_output = "parquet",
                                     conn = duckdb.connect()):

    if stock is None:
        return None


    if tf == "1min":
        path_old = f"{CLEAN_DATA_1MIN}/{stock}_1min.{extension_old}"
        path_new = f"{CLEAN_NEW_DATA}/{stock}_1min.{extension_new}"
    elif tf == "Daily":
        path_old = f"{CLEAN_DATA_DAILY}/{stock}_Daily.{extension_old}"
        path_new = f"{CLEAN_NEW_DATA}/{stock}_Daily.{extension_new}"
    try:
        df_old = conn.execute(f""" 
        SELECT * FROM 
        "{path_old}"
        """).df()
    except:
        df_old = pd.DataFrame()
    try:
        df_new = conn.execute(f""" 
        SELECT * FROM 
        "{path_new}"
        """).df()
    except:
        df_new = pd.DataFrame()

    df_concat = pd.concat([ df_old, df_new])

    if len(df_concat) > 0:
        query = """ 
    SELECT DISTINCT ON (datetime) *
        FROM df_concat
        ORDER BY datetime
        """
        # df_output = conn.execute("""
        
        # """).df()
        if tf == "1min":
            path_old = f"{CLEAN_DATA_1MIN}/{stock}_1min.{extension_output}"
            
        elif tf == "Daily":
            path_old = f"{CLEAN_DATA_DAILY}/{stock}_Daily.{extension_output}"
            
            
        if extension_output == "csv":
            conn.execute(f"COPY ({query}) TO '{path_old}' (HEADER, DELIMITER ',');")
        elif extension_output == "parquet":
            conn.execute(f"COPY ({query}) TO '{path_old}' (FORMAT PARQUET);")



def run_once_combined_duckdb():
    stock_list_1min, stock_list_Daily  = list_files_new_data(f"{CLEAN_NEW_DATA}")
   
    conn = duckdb.connect()

    if len(stock_list_1min) == 0:
        print("No files found in the directory for 1min.")
    else:
        stock_old_data_1min_cache = {}
        stock_old_data_1min, _  = list_files_new_data(f"{CLEAN_DATA_1MIN}")
        for i, item in enumerate(stock_old_data_1min):
            stock_old_data_1min_cache[item["stock"]] = item

        for i, item in enumerate(stock_list_1min):
            extension_old =  "csv"
            if item["stock"] in stock_old_data_1min_cache:
                extension_old = stock_old_data_1min_cache[item["stock"]]["extension"]

            run_once_combined_duckdb_helper(item["stock"], 
                                            tf = "1min", 
                                            extension_old = extension_old,
                                            extension_new = item["extension"], 
                                            extension_output = "parquet",
                                            conn = conn)
    if len(stock_list_Daily) == 0:
        print("No files found in the directory for Daily.")
        
    else:
        stock_old_data_Daily_cache = {}
        _ , stock_old_data_Daily  = list_files_new_data(f"{CLEAN_DATA_DAILY}")
        for i, item in enumerate(stock_old_data_Daily):
            stock_old_data_Daily_cache[item["stock"]] = item

        for i, item in enumerate(stock_list_Daily):
            extension_old =  "csv"
            if item["stock"] in stock_old_data_Daily_cache:
                extension_old = stock_old_data_Daily_cache[item["stock"]]["extension"]
    
            run_once_combined_duckdb_helper(item["stock"], 
                                            tf = "Daily", 
                                            extension_old = extension_old,
                                            extension_new = item["extension"], 
                                            extension_output = "parquet",
                                            conn = conn)