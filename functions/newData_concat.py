import pandas as pd
import numpy as np
from pathlib import Path
from functions import df_saving, timeframe, indicators, json_saving
import concurrent.futures
from filelock import FileLock
import os

def concat_df(old_df, new_df):
    for i in range(1, 100):
        try:
            match_position = new_df.index.get_loc(old_df.index[-i])
            # Slice new_df from the next index after match_position to the end
            # print("match_position", match_position)
            # print(old_df.index[-i])
            new_df_slice = new_df.iloc[match_position + 1:]
            # print(new_df_slice.index[-1])
            old_df_slice = old_df.loc[:old_df.index[-i]]
            # print("new", new_df_slice.index[0])
            # print("old", old_df_slice.index[-1])
            
            # Concatenate df with the new slice
            result_df = pd.concat([old_df_slice, new_df_slice], axis=0)
            # print("new" ,result_df.index[-1])
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



# def concat_any_timeframe(stock, timeframe_value, list_of_indicators):

#     if timeframe_value == "Daily":
        
        

#         path_indicator_process = f"indicator_process/{stock}_Daily"
#         path_clean = f"Clean_data/RAW_daily_data_tradingview/{stock}_Daily"
        
        
#         with df_saving.lock_file(path_indicator_process):
#             if df_saving.if_path_exist(path_indicator_process) and df_saving.if_path_exist(path_clean):
#                 df_indicator_process = df_saving.read_file(path_indicator_process)
#                 df_indicator_process_length = len(df_indicator_process)
            
#                 df_clean = df_saving.read_file(path_clean, extension=".csv")
#                 df_clean["symbol"] = stock
#                 df_clean = timeframe.timeframe_Daily(df_clean)

#                 df = concat_df(df_indicator_process, df_clean)
#                 df = indicators.convert_date_time_datetime_into_numbers(df)

#                 for i in range(0, len(list_of_indicators)):
#                     df = indicators.get_indicator_shortform(df, list_of_indicators[i], 1)
#                 # print(df)
#                 df_saving.to_file(df, path_indicator_process)
        
#             elif df_saving.if_path_exist(path_clean):
#                 df_clean = df_saving.read_file(path_clean, extension=".csv")
#                 df_clean["symbol"] = stock
#                 df_clean = timeframe.timeframe_Daily(df_clean)

#                 df = indicators.convert_date_time_datetime_into_numbers(df_clean)

#                 for i in range(0, len(list_of_indicators)):
#                     df = indicators.get_indicator_shortform(df, list_of_indicators[i], 1)
                
#                 df_saving.to_file(df, path_indicator_process)
        
#     elif timeframe_value == "Weekly" or timeframe_value == "Monthly":
#         # from_ = f"indicator_process/{stock}_{"Daily"}"
#         # to_ = f"indicator_process/{stock}_{timeframe_value}"

#         path_indicator_process = f"indicator_process/{stock}_{timeframe_value}"
#         path_indicator_process_Daily = f"indicator_process/{stock}_Daily"


#         with df_saving.lock_file(path_indicator_process):
#             if df_saving.if_path_exist(path_indicator_process) and df_saving.if_path_exist(path_indicator_process_Daily):
#                 df_indicator_process_Daily = df_saving.read_file(path_indicator_process_Daily)
#                 df_indicator_process_Daily["symbol"] = stock
#                 df_indicator_process_Daily = timeframe.convert_daily_weekly_and_monthly(df_indicator_process_Daily, timeframe_value)
#                 # df_old_length = len(df_indicator_process_Daily)
            
#                 df_indicator_process = df_saving.read_file(path_indicator_process)
                

#                 df = concat_df(df_indicator_process, df_indicator_process_Daily)
#                 df = indicators.convert_date_time_datetime_into_numbers(df)

#                 for i in range(0, len(list_of_indicators)):
#                     df = indicators.get_indicator_shortform(df, list_of_indicators[i], 1)
#                 # print(df)
#                 df_saving.to_file(df, path_indicator_process)
#             elif df_saving.if_path_exist(path_indicator_process_Daily) :
#                 df_indicator_process_Daily = df_saving.read_file(path_indicator_process_Daily)
#                 df_indicator_process_Daily["symbol"] = stock
#                 df_indicator_process_Daily = timeframe.convert_daily_weekly_and_monthly(df_indicator_process_Daily, timeframe_value)
                
#                 df = indicators.convert_date_time_datetime_into_numbers(df_indicator_process_Daily)

#                 for i in range(0, len(list_of_indicators)):
#                     df = indicators.get_indicator_shortform(df, list_of_indicators[i], 1)
        
#                 df_saving.to_file(df, path_indicator_process)

# #**************************************
#     elif timeframe_value == 1:
        
        
#         path_indicator_process = f"indicator_process/{stock}_1min"
#         path_clean = f"Clean_data/1min/{stock}_1min"
                
#         with df_saving.lock_file(path_indicator_process):
#             if df_saving.if_path_exist(path_indicator_process) and df_saving.if_path_exist(path_clean):
#                 df_clean = df_saving.read_file(path_clean, extension=".csv")
#                 df_clean["symbol"] = stock
#                 df_clean = timeframe.timeframe_1min(df_clean)

#                 df_indicator_process = df_saving.read_file(path_indicator_process)
                
#                 df = concat_df(df_indicator_process, df_clean)
#                 df = indicators.convert_date_time_datetime_into_numbers(df)

#                 for i in range(0, len(list_of_indicators)):
#                     df = indicators.get_indicator_shortform(df, list_of_indicators[i], 1)
                
#                 df_saving.to_file(df, path_indicator_process)
#             elif df_saving.if_path_exist(path_clean) :
#                 df_clean = df_saving.read_file(path_clean, extension=".csv")
#                 df_clean["symbol"] = stock
#                 df_clean = timeframe.timeframe_1min(df_clean)

#                 df = indicators.convert_date_time_datetime_into_numbers(df_clean)

#                 for i in range(0, len(list_of_indicators)):
#                     df = indicators.get_indicator_shortform(df, list_of_indicators[i], 1)
                
#                 df_saving.to_file(df, path_indicator_process)

#     elif 60*5 >= timeframe_value and timeframe_value > 1:

#         # path_old = "indicator_process/"+str(stock)+"_"+str(timeframe_value)+"min"
#         # path_new = "Clean_data/newData/"+str(stock)+"_"+str(1)+"min"
        
#         path_indicator_process_1min = f"indicator_process/{stock}_1min"
#         path_indicator_process = f"indicator_process/{stock}_{timeframe_value}min"

        
        
#         with df_saving.lock_file(path_indicator_process):
#             if df_saving.if_path_exist(path_indicator_process) and df_saving.if_path_exist(path_indicator_process_1min):
#                 df_indicator_process = df_saving.read_file(path_indicator_process)
#                 # df_old_length = len(df_old)

#                 # create new data to required tf
#                 df_indicator_process_1min = df_saving.read_file(path_indicator_process_1min)
#                 df_indicator_process_1min["symbol"] = stock
#                 # df_new = timeframe.timeframe_1min(df_new)
#                 df_indicator_process_1min = timeframe.convert_1min_anymin(df_indicator_process_1min, timeframe_value)
                
#                 # concat new and old df
#                 df = concat_df(df_indicator_process, df_indicator_process_1min)
#                 df = indicators.convert_date_time_datetime_into_numbers(df)
                
#                 # apply indicators
#                 for i in range(0, len(list_of_indicators)):
#                     # print(list_of_indicators[i])
#                     df = indicators.get_indicator_shortform(df, list_of_indicators[i], 1)
                
#                 df_saving.to_file(df, path_indicator_process)

#             elif df_saving.if_path_exist(path_indicator_process_1min) :
#                 df_indicator_process_1min = df_saving.read_file(path_indicator_process_1min)
#                 df_indicator_process_1min["symbol"] = stock
#                 # df_new = timeframe.timeframe_1min(df_new)
#                 df_indicator_process_1min = timeframe.convert_1min_anymin(df_indicator_process_1min, timeframe_value)

#                 df = indicators.convert_date_time_datetime_into_numbers(df_indicator_process_1min)

#                 for i in range(0, len(list_of_indicators)):
#                     # print(list_of_indicators[i])
#                     df = indicators.get_indicator_shortform(df, list_of_indicators[i], 1)
                
#                 df_saving.to_file(df, path_indicator_process)

def concat_any_timeframe_delete_indicators(stock, timeframe_value):

    if timeframe_value == "Daily":
        
        

        path_indicator_process = f"indicator_process/{stock}_Daily"
        path_clean = f"Clean_data/RAW_daily_data_tradingview/{stock}_Daily"
        
        
        with df_saving.lock_file(path_indicator_process):
            if df_saving.if_path_exist(path_indicator_process) and df_saving.if_path_exist(path_clean, extension=".csv"):
                df_indicator_process = df_saving.read_file(path_indicator_process)
                df_indicator_process_length = len(df_indicator_process)
            
                df_clean = df_saving.read_file(path_clean, extension=".csv")
                df_clean["symbol"] = stock
                df_clean = timeframe.timeframe_Daily(df_clean)

                df = concat_df(df_indicator_process, df_clean)
                df = indicators.convert_date_time_datetime_into_numbers(df)
                
                df = df[[ 'symbol', "open" ,"high", "low", "close", "volume", "date_number", "time_number", "datetime_number"]]
                # for i in range(0, len(list_of_indicators)):
                #     df = indicators.get_indicator_shortform(df, list_of_indicators[i], 1)
                # print(df)
                df_saving.to_file(df, path_indicator_process)
        
            elif df_saving.if_path_exist(path_clean, extension=".csv"):
                df_clean = df_saving.read_file(path_clean, extension=".csv")
                df_clean["symbol"] = stock
                df_clean = timeframe.timeframe_Daily(df_clean)

                df = indicators.convert_date_time_datetime_into_numbers(df_clean)
                df = df[[ 'symbol', "open" ,"high", "low", "close", "volume", "date_number", "time_number", "datetime_number"]]
                # for i in range(0, len(list_of_indicators)):
                #     df = indicators.get_indicator_shortform(df, list_of_indicators[i], 1)
                
                df_saving.to_file(df, path_indicator_process)
        df_saving.remove_lock(path_indicator_process)
    elif timeframe_value == "Weekly" or timeframe_value == "Monthly":
        # from_ = f"indicator_process/{stock}_{"Daily"}"
        # to_ = f"indicator_process/{stock}_{timeframe_value}"

        path_indicator_process = f"indicator_process/{stock}_{timeframe_value}"
        path_indicator_process_Daily = f"indicator_process/{stock}_Daily"


        with df_saving.lock_file(path_indicator_process):
            if df_saving.if_path_exist(path_indicator_process) and df_saving.if_path_exist(path_indicator_process_Daily):
                df_indicator_process_Daily = df_saving.read_file(path_indicator_process_Daily)
                df_indicator_process_Daily["symbol"] = stock
                df_indicator_process_Daily = timeframe.convert_daily_weekly_and_monthly(df_indicator_process_Daily, timeframe_value)
                # df_old_length = len(df_indicator_process_Daily)
            
                df_indicator_process = df_saving.read_file(path_indicator_process)
                

                df = concat_df(df_indicator_process, df_indicator_process_Daily)
                df = indicators.convert_date_time_datetime_into_numbers(df)
                
                df = df[[ 'symbol', "open" ,"high", "low", "close", "volume", "date_number", "time_number", "datetime_number"]]
                # for i in range(0, len(list_of_indicators)):
                #     df = indicators.get_indicator_shortform(df, list_of_indicators[i], 1)
                # print(df)
                df_saving.to_file(df, path_indicator_process)
            elif df_saving.if_path_exist(path_indicator_process_Daily) :
                df_indicator_process_Daily = df_saving.read_file(path_indicator_process_Daily)
                df_indicator_process_Daily["symbol"] = stock
                df_indicator_process_Daily = timeframe.convert_daily_weekly_and_monthly(df_indicator_process_Daily, timeframe_value)
                
                df = indicators.convert_date_time_datetime_into_numbers(df_indicator_process_Daily)
                
                df = df[[ 'symbol', "open" ,"high", "low", "close", "volume", "date_number", "time_number", "datetime_number"]]
                # for i in range(0, len(list_of_indicators)):
                #     df = indicators.get_indicator_shortform(df, list_of_indicators[i], 1)
        
                df_saving.to_file(df, path_indicator_process)
        df_saving.remove_lock(path_indicator_process)
#**************************************
    elif timeframe_value == 1:
        
        
        path_indicator_process = f"indicator_process/{stock}_1min"
        path_clean = f"Clean_data/1min/{stock}_1min"
                
        with df_saving.lock_file(path_indicator_process):
            if df_saving.if_path_exist(path_indicator_process) and df_saving.if_path_exist(path_clean):
                df_clean = df_saving.read_file(path_clean, extension=".csv")
                df_clean["symbol"] = stock
                df_clean = timeframe.timeframe_1min(df_clean)

                df_indicator_process = df_saving.read_file(path_indicator_process)
                
                df = concat_df(df_indicator_process, df_clean)
                df = indicators.convert_date_time_datetime_into_numbers(df)
                
                df = df[[ 'symbol', "open" ,"high", "low", "close", "volume", "date_number", "time_number", "datetime_number"]]
                # for i in range(0, len(list_of_indicators)):
                #     df = indicators.get_indicator_shortform(df, list_of_indicators[i], 1)
                
                df_saving.to_file(df, path_indicator_process)
            elif df_saving.if_path_exist(path_clean) :
                df_clean = df_saving.read_file(path_clean, extension=".csv")
                df_clean["symbol"] = stock
                df_clean = timeframe.timeframe_1min(df_clean)

                df = indicators.convert_date_time_datetime_into_numbers(df_clean)

                df = df[[ 'symbol', "open" ,"high", "low", "close", "volume", "date_number", "time_number", "datetime_number"]]
                # for i in range(0, len(list_of_indicators)):
                #     df = indicators.get_indicator_shortform(df, list_of_indicators[i], 1)
                
                df_saving.to_file(df, path_indicator_process)
        df_saving.remove_lock(path_indicator_process)
    elif 60*5 >= timeframe_value and timeframe_value > 1:

        # path_old = "indicator_process/"+str(stock)+"_"+str(timeframe_value)+"min"
        # path_new = "Clean_data/newData/"+str(stock)+"_"+str(1)+"min"
        
        path_indicator_process_1min = f"indicator_process/{stock}_1min"
        path_indicator_process = f"indicator_process/{stock}_{timeframe_value}min"

        
        
        with df_saving.lock_file(path_indicator_process):
            if df_saving.if_path_exist(path_indicator_process) and df_saving.if_path_exist(path_indicator_process_1min):
                df_indicator_process = df_saving.read_file(path_indicator_process)
                # df_old_length = len(df_old)

                # create new data to required tf
                df_indicator_process_1min = df_saving.read_file(path_indicator_process_1min)
                df_indicator_process_1min["symbol"] = stock
                # df_new = timeframe.timeframe_1min(df_new)
                df_indicator_process_1min = timeframe.convert_1min_anymin(df_indicator_process_1min, timeframe_value)
                
                # concat new and old df
                df = concat_df(df_indicator_process, df_indicator_process_1min)
                df = indicators.convert_date_time_datetime_into_numbers(df)
                
                df = df[[ 'symbol', "open" ,"high", "low", "close", "volume", "date_number", "time_number", "datetime_number"]]
                # apply indicators
                # for i in range(0, len(list_of_indicators)):
                #     # print(list_of_indicators[i])
                #     df = indicators.get_indicator_shortform(df, list_of_indicators[i], 1)
                
                df_saving.to_file(df, path_indicator_process)

            elif df_saving.if_path_exist(path_indicator_process_1min) :
                df_indicator_process_1min = df_saving.read_file(path_indicator_process_1min)
                df_indicator_process_1min["symbol"] = stock
                # df_new = timeframe.timeframe_1min(df_new)
                df_indicator_process_1min = timeframe.convert_1min_anymin(df_indicator_process_1min, timeframe_value)

                df = indicators.convert_date_time_datetime_into_numbers(df_indicator_process_1min)

                df = df[[ 'symbol', "open" ,"high", "low", "close", "volume", "date_number", "time_number", "datetime_number"]]
                # for i in range(0, len(list_of_indicators)):
                #     # print(list_of_indicators[i])
                #     df = indicators.get_indicator_shortform(df, list_of_indicators[i], 1)
                
                df_saving.to_file(df, path_indicator_process)
        df_saving.remove_lock(path_indicator_process)

def clean_data_concat(stock):
    print(stock)
    path_old = f"Clean_data/RAW_daily_data_tradingview/{stock}_Daily"
    path_new = f"Clean_data/newData/{stock}_Daily"

    with df_saving.lock_file(path_old, extension=".csv"):
        # print("path_old", df_saving.if_path_exist(path_old,extension=".csv"))
        # print("path_new", df_saving.if_path_exist(path_new, extension=".csv"))

        if df_saving.if_path_exist(path_old, extension=".csv") and df_saving.if_path_exist(path_new, extension=".csv"):
            df_old = df_saving.read_file(path_old, extension=".csv")
        
            df_new = df_saving.read_file(path_new, extension=".csv")
            
            df_new = concat_df(df_old, df_new)
            
            # print(df_new)
            df_saving.to_file(df_new, path_old,  extension=".csv")
        elif df_saving.if_path_exist(path_new, extension=".csv") :
            df_new = df_saving.read_file(path_new, extension=".csv")
            df_saving.to_file(df_new, path_old,  extension=".csv")
    df_saving.remove_lock(path_old, extension=".csv")
    path_old = f"Clean_data/1min/{stock}_1min"
    path_new = f"Clean_data/newData/{stock}_1min"
    # print("path_old", df_saving.if_path_exist(path_old))
    # print("path_new", df_saving.if_path_exist(path_new))
    with df_saving.lock_file(path_old, extension=".csv"):
        if df_saving.if_path_exist(path_old, extension=".csv") and df_saving.if_path_exist(path_new, extension=".csv"):
            df_old = df_saving.read_file(path_old, extension=".csv")
        
            df_new = df_saving.read_file(path_new, extension=".csv")
            
            df_new = concat_df(df_old, df_new)
            
            # print(df_new)
            df_saving.to_file(df_new, path_old, extension=".csv")
        elif df_saving.if_path_exist(path_new, extension=".csv") :
            df_new = df_saving.read_file(path_new, extension=".csv")
            df_saving.to_file(df_new, path_old, extension=".csv")
    df_saving.remove_lock(path_old, extension=".csv")

def cleanData_to_1min_Daily(stock):
    path_clean = f"Clean_data/RAW_daily_data_tradingview/{stock}_Daily"
    path_indicator_process = f"indicator_process/{stock}_Daily"

    with df_saving.lock_file(path_indicator_process, extension=".csv") :
        if df_saving.if_path_exist(path_indicator_process, extension=".csv") and df_saving.if_path_exist(path_clean, extension=".csv"):
            df_clean = df_saving.read_file(path_clean, extension=".csv")
            df_clean["symbol"] = stock
            df_clean = timeframe.timeframe_Daily(df_clean)
        
            df_indicator_process = df_saving.read_file(path_indicator_process)
            
            df = concat_df(df_indicator_process, df_clean)
            df = indicators.convert_date_time_datetime_into_numbers(df)

            df_saving.to_file(df, path_indicator_process)
        elif df_saving.if_path_exist(path_clean, extension=".csv") :

            df_clean = df_saving.read_file(path_clean, extension=".csv")
            df_clean["symbol"] = stock
            df_clean = timeframe.timeframe_Daily(df_clean)
            df = indicators.convert_date_time_datetime_into_numbers(df_clean)

            df_saving.to_file(df, path_indicator_process)
    df_saving.remove_lock(path_indicator_process, extension=".csv")

    path_clean = f"Clean_data/1min/{stock}_1min"
    path_indicator_process = f"indicator_process/{stock}_1min"

    with df_saving.lock_file(path_indicator_process, extension=".csv"):
        if df_saving.if_path_exist(path_indicator_process, extension=".csv") and df_saving.if_path_exist(path_clean, extension=".csv"):
            df_clean = df_saving.read_file(path_clean, extension=".csv")
            df_clean["symbol"] = stock
            df_clean = timeframe.timeframe_1min(df_clean)

            df_indicator_process = df_saving.read_file(path_indicator_process, extension=".csv")
            
            df = concat_df(df_indicator_process, df_clean)
            df = indicators.convert_date_time_datetime_into_numbers(df)
            # print(df_new)
            df_saving.to_file(df, path_indicator_process, extension=".csv")
        elif df_saving.if_path_exist(path_clean, extension=".csv") :
            df_clean = df_saving.read_file(path_clean, extension=".csv")
            df_clean["symbol"] = stock
            df_clean = timeframe.timeframe_1min(df_clean)

            df = indicators.convert_date_time_datetime_into_numbers(df_clean)
            df = indicators.convert_date_time_datetime_into_numbers(df)

            df_saving.to_file(df, path_indicator_process, extension=".csv")
    df_saving.remove_lock(path_indicator_process, extension=".csv")


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

def run_once_combined():
    file_path = "wait_for_update"
    lock_path = file_path + ".lock"
    lock = FileLock(lock_path)

    with lock:
        stock_list = list_files("Clean_data/newData")
        # print(stock_list)
        if len(stock_list) == 0:
            print("No files found in the directory.")
            return
       
        # with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
            
        #     executor.map(clean_data_concat, stock_list)
        # with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
            
        #     executor.map(cleanData_to_1min_Daily, stock_list)

        for i in range(0, len(stock_list)):
            clean_data_concat(stock_list[i])
        # for i in range(0, len(stock_list)):
        #     cleanData_to_1min_Daily(stock_list[i])


        files_list = get_dataframe_file_names("indicator_process")
        for i in range(0, len(files_list)):
            try:
                concat_any_timeframe_delete_indicators(files_list[i][0], files_list[i][1])
            except:
                print("ERROR", files_list[i])
        # try :
        #     # loaded_data = json_saving.load_data_thread_safe(location)
        #     # result = group_data(loaded_data)

        #     with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
        
        #         executor.map(temp_concat_any_timeframe, result)
            
        # except:
        #     print("ERROR")
            

       
        

# from functions import newData_concat
# run_once_combined()