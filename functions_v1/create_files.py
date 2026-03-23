import os
from functions import fastCache_saving, df_saving, backtesting_functions, functions, controller
import numpy as np  
import pandas as pd
# import polars as pl
import os
from multiprocessing import Pool

path = "fastCache"

os.makedirs(path, exist_ok=True)

def create_fast_cache(stock, tf, column, smallest, candle, shortForm_fastCache):
    # print("candle", candle)
    
    # stock = "INFY"
    # column = "close"
    # tf = 15
    # smallest = 15
    
    # candle = 0
    if candle [:1] == "=":
        pass
    else:
        candle = int(candle)

    arr = {"datetime", "date_number", "time_number", "datetime_number", "close"}
    arr.update({column})
    arr = list(arr)
    # if smallest == "Daily" or smallest == "Weekly" or smallest == "Monthly": 
# tf for column timeframe
    if tf == "Daily" or tf == "Weekly" or tf == "Monthly":
        path = f"indicator_process/{stock}_{tf}"
    
    elif 1 <= tf & tf <= 60*5:
        path = f"indicator_process/{stock}_{tf}min"
    df = df_saving.read_file(path, col= arr )
# smallest
    if smallest == "Daily" or smallest == "Weekly" or smallest == "Monthly":
        path = f"indicator_process/{stock}_{smallest}"
    
    elif 1 <= smallest & smallest <= 60*5:
        path = f"indicator_process/{stock}_{smallest}min"

    df_smallest = df_saving.read_file(path, col= ["datetime_number", "date_number"] )
    df_data = df_smallest.to_numpy()
    data_column = list(df_smallest.columns)
    datetime_index = data_column.index("datetime_number")
    date_index = data_column.index("date_number")
    # print(data_column)

    if smallest == "Daily" or smallest == "Weekly" or smallest == "Monthly": 
        uniqueTime = None
        smallestLastTime = None
    else:
        uniqueTime = functions.timeframe_divide_uniqueTime(smallest)
        smallestLastTime = int("".join(uniqueTime.loc[uniqueTime.index[-1], f"uniqueTime_{smallest}"].split(":")))

    # smallestLastTime = functions.timeframe_divide_uniqueTime(smallest)


    arr = np.empty(len(df_smallest), dtype=np.object_)
    date_arr = np.empty(len(df_smallest), dtype=np.int64)
    for j in range(0, len(df_smallest)):
        arr[j] = backtesting_functions.select_candles_temp(stock, column, int(df_data[j][datetime_index]), df, uniqueTime, tf, df_smallest, smallest, smallestLastTime, candle)
        date_arr[j] = df_data[j][date_index]

    arr = pd.DataFrame({"data" : arr, "date_number" : date_arr})

    arr.index.name = "index"
    fastCache_saving.to_file(arr, f"fastCache/{shortForm_fastCache}")


# def create_fast_cache(stock, tf, column, smallest, candle, shortForm_fastCache):
#     """
#     Builds and saves a fastCache for a stock's indicator column over a given time frame.

#     Parameters:
#     - stock (str): Symbol name
#     - tf (str|int): Time frame for the column (e.g. 'Daily', 15)
#     - column (str): The indicator or field to cache
#     - smallest (str|int): The smallest time frame for intraday alignment
#     - candle (str|int): Candle index or config
#     - shortForm_fastCache (str): Identifier for output cache file
#     """
#     # If candle is a formula (starts with '='), keep as is. Otherwise, convert to int.
#     if not str(candle).startswith("="):
#         candle = int(candle)
    
#     # Ensure we always use the standard columns, plus the requested one
#     col_list = ["datetime", "date_number", "time_number", "datetime_number", "close"]
#     if column not in col_list:
#         col_list.append(column)
    
#     # Build the path for the main DataFrame for the given timeframe
#     if tf in ("Daily", "Weekly", "Monthly"):
#         tf_path = f"indicator_process/{stock}_{tf}"
#     elif isinstance(tf, int) and 1 <= tf <= 60*5:
#         tf_path = f"indicator_process/{stock}_{tf}min"
#     else:
#         raise ValueError(f"Unsupported timeframe: {tf}")
#     print(tf_path)
#     df_tf = df_saving.read_file(tf_path, col=col_list)

#     # Build the path for the smallest timeframe alignment
#     if smallest in ("Daily", "Weekly", "Monthly"):
#         smallest_path = f"indicator_process/{stock}_{smallest}"
#         uniqueTime = None
#         smallestLastTime = None
#     elif isinstance(smallest, int) and 1 <= smallest <= 60*5:
#         smallest_path = f"indicator_process/{stock}_{smallest}min"
#         uniqueTime = functions.timeframe_divide_uniqueTime(smallest)
#         smallestLastTime = int("".join(uniqueTime.loc[uniqueTime.index[-1], f"uniqueTime_{smallest}"].split(":")))
#     else:
#         raise ValueError(f"Unsupported smallest timeframe: {smallest}")

#     df_smallest = df_saving.read_file(smallest_path, col=["datetime_number", "date_number"])
#     df_smallest_np = df_smallest.to_numpy()
#     datetime_idx = list(df_smallest.columns).index("datetime_number")
#     date_idx = list(df_smallest.columns).index("date_number")

#     # Pre-allocate output arrays
#     data_array = np.empty(len(df_smallest), dtype=object)
#     date_array = np.empty(len(df_smallest), dtype=np.int64)

#     # Build the fast cache data by iterating over each row
#     for j in range(len(df_smallest)):
#         current_datetime = int(df_smallest_np[j][datetime_idx])
#         # Call to fast candle selection logic (from your backtesting_functions)
#         data_array[j] = backtesting_functions.select_candles_temp(
#             stock, column, current_datetime, df_tf,
#             uniqueTime, tf, df_smallest, smallest, smallestLastTime, candle
#         )
#         date_array[j] = df_smallest_np[j][date_idx]

#     # Save as DataFrame and output using fastCache_saving
#     fast_cache_df = pd.DataFrame({"data": data_array, "date_number": date_array})
#     fast_cache_df.index.name = "index"
#     fastCache_saving.to_file(fast_cache_df, f"fastCache/{shortForm_fastCache}")


# def create_file(file_list):
#     path = "fastCache"
#     os.makedirs(path, exist_ok=True)        # create directory if it doesn't exist
#     for i in range(len(file_list)):        
#         if fastCache_saving.if_path_exist(f"{path}/{file_list[i][3]}") == False:     # check if cache file not exixts
#             stock = file_list[i][0]
#             timeframe_value = file_list[i][1]
#             if timeframe_value == "Daily" or timeframe_value == "Weekly" or timeframe_value == "Monthly":
#                 path = f"indicator_process/{stock}_{timeframe_value}"
            
#             elif 1 <= timeframe_value and timeframe_value <= 60*5:
#                 path = f"indicator_process/"+str(stock)+ "_"+str(timeframe_value)+"min"
#             if df_saving.if_path_exist(path) == True:
#                 check = controller.is_column_present(file_list[i][0], file_list[i][1] ,file_list[i][2])      # check if column not exists
#                 if check == False:
                
            
#                     controller.apply_indicators(file_list[i][0], file_list[i][1] ,file_list[i][2], file_list[i][4])       # create columns 
                
#                     # print("Created", file_list[i][2], controller.is_column_present(file_list[i][0], file_list[i][1] ,file_list[i][2]))
#                     create_fast_cache(file_list[i][0], file_list[i][1], file_list[i][2], file_list[i][5], file_list[i][4][0], file_list[i][3])
#                 else:
#                     create_fast_cache(file_list[i][0], file_list[i][1], file_list[i][2], file_list[i][5], file_list[i][4][0], file_list[i][3])
#             else:
#                 controller.apply_indicators(file_list[i][0], file_list[i][1] ,file_list[i][2], file_list[i][4])       # create columns    
#                 create_fast_cache(file_list[i][0], file_list[i][1], file_list[i][2], file_list[i][5], file_list[i][4][0], file_list[i][3])
                
#         else:
#             # print("File already exists", file_list[i][3])
#             stock = file_list[i][0]
#             timeframe_value = file_list[i][1]
#             if timeframe_value == "Daily" or timeframe_value == "Weekly" or timeframe_value == "Monthly":
#                 path_column = f"indicator_process/{stock}_{timeframe_value}"
            
#             elif 1 <= timeframe_value and timeframe_value <= 60*5:
#                 path_column = f"indicator_process/"+str(stock)+ "_"+str(timeframe_value)+"min"
            
#             if df_saving.if_path_exist(path_column) == True:
#                 df_last_date = df_saving.read_file(path_column, col=["date_number"])
#                 df_last_date = df_last_date.loc[df_last_date.index[-1] ,"date_number"]
#                 # print("df_last_date", df_last_date)
#                 # df_length = df_last_date.loc[df_last_date.index[-1] ,"date_number"]

#                 df_cache_last_date = fastCache_saving.read_file(f"{path}/{file_list[i][3]}")
#                 df_cache_last_date = df_cache_last_date.loc[df_cache_last_date.index[-1] ,"date_number"]
#                 # print("df_cache_last_date", df_cache_last_date)
#                 if df_last_date > df_cache_last_date:
#                     check = controller.is_column_present(file_list[i][0], file_list[i][1] ,file_list[i][2])      # check if column not exists
#                     if check == False:
                    
                
#                         controller.apply_indicators(file_list[i][0], file_list[i][1] ,file_list[i][2], file_list[i][4])       # create columns 
                    
#                         # print("Created", file_list[i][2], controller.is_column_present(file_list[i][0], file_list[i][1] ,file_list[i][2]))
#                         create_fast_cache(file_list[i][0], file_list[i][1], file_list[i][2], file_list[i][5], file_list[i][4][0], file_list[i][3])
#                     else:
#                         create_fast_cache(file_list[i][0], file_list[i][1], file_list[i][2], file_list[i][5], file_list[i][4][0], file_list[i][3])

#             else:
#                 controller.apply_indicators(file_list[i][0], file_list[i][1] ,file_list[i][2], file_list[i][4])       # create columns    
#                 create_fast_cache(file_list[i][0], file_list[i][1], file_list[i][2], file_list[i][5], file_list[i][4][0], file_list[i][3])


# def create_file(file_list):
#     """Create fastCache files for each entry in file_list if needed."""
#     cache_dir = "fastCache"
#     os.makedirs(cache_dir, exist_ok=True)  # Ensure the fastCache directory exists

#     for entry in file_list:
#         cache_path = f"{cache_dir}/{entry[3]}"
#         stock = entry[0]
#         timeframe = entry[1]
#         column = entry[2]
#         indicator_args = entry[4]
#         other_args = entry[5]
#         cache_name = entry[3]

#         # Determine correct data path for indicator process
#         if timeframe in ("Daily", "Weekly", "Monthly"):
#             indicator_path = f"indicator_process/{stock}_{timeframe}"
#         elif 1 <= timeframe <= 60 * 5:
#             indicator_path = f"indicator_process/{stock}_{timeframe}min"
#         else:
#             indicator_path = None  # fallback

#         file_missing = not fastCache_saving.if_path_exist(cache_path)

#         if file_missing:
#             if indicator_path and df_saving.if_path_exist(indicator_path):
#                 column_present = controller.is_column_present(stock, timeframe, column)
#                 if not column_present:
#                     controller.apply_indicators(stock, timeframe, column, indicator_args)
#                     create_fast_cache(stock, timeframe, column, other_args, indicator_args[0], cache_name)
#                 else:
#                     create_fast_cache(stock, timeframe, column, other_args, indicator_args[0], cache_name)
#             else:
#                 controller.apply_indicators(stock, timeframe, column, indicator_args)
#                 create_fast_cache(stock, timeframe, column, other_args, indicator_args[0], cache_name)
#         else:
#             # The fastCache file already exists
#             # (Check for updates needed based on date_number)
#             if indicator_path and df_saving.if_path_exist(indicator_path):
#                 df_last = df_saving.read_file(indicator_path, col=["date_number"])
#                 last_date = df_last.loc[df_last.index[-1], "date_number"]

#                 df_cache = fastCache_saving.read_file(cache_path)
#                 cache_last_date = df_cache.loc[df_cache.index[-1], "date_number"]

#                 if last_date > cache_last_date:
#                     column_present = controller.is_column_present(stock, timeframe, column)
#                     if not column_present:
#                         controller.apply_indicators(stock, timeframe, column, indicator_args)
#                         create_fast_cache(stock, timeframe, column, other_args, indicator_args[0], cache_name)
#                     else:
#                         create_fast_cache(stock, timeframe, column, other_args, indicator_args[0], cache_name)
#             else:
#                 controller.apply_indicators(stock, timeframe, column, indicator_args)
#                 create_fast_cache(stock, timeframe, column, other_args, indicator_args[0], cache_name)




def process_entry(entry): 
    cache_dir = "fastCache"
    cache_path = f"{cache_dir}/{entry[3]}"
    stock = entry[0]
    timeframe = entry[1]
    column = entry[2]
    indicator_args = entry[4]
    other_args = entry[5]
    cache_name = entry[3]

    # Determine correct data path for indicator process
    if timeframe in ("Daily", "Weekly", "Monthly"):
        indicator_path = f"indicator_process/{stock}_{timeframe}"
    elif isinstance(timeframe, int) and 1 <= timeframe <= 60 * 5:
        indicator_path = f"indicator_process/{stock}_{timeframe}min"
    else:
        indicator_path = None  # fallback
    
    file_missing = not fastCache_saving.if_path_exist(cache_path)

    if file_missing:
        if indicator_path and df_saving.if_path_exist(indicator_path):
            column_present = controller.is_column_present(stock, timeframe, column)
            if not column_present:
                controller.apply_indicators(stock, timeframe, column, indicator_args)
                create_fast_cache(stock, timeframe, column, other_args, indicator_args[0], cache_name)
            else:
                create_fast_cache(stock, timeframe, column, other_args, indicator_args[0], cache_name)
        else:
            controller.apply_indicators(stock, timeframe, column, indicator_args)
            create_fast_cache(stock, timeframe, column, other_args, indicator_args[0], cache_name)
    else:
        if indicator_path and df_saving.if_path_exist(indicator_path):
            df_last = df_saving.read_file(indicator_path, col=["date_number"])
            last_date = df_last.loc[df_last.index[-1], "date_number"]

            df_cache = fastCache_saving.read_file(cache_path)
            cache_last_date = df_cache.loc[df_cache.index[-1], "date_number"]

            if last_date > cache_last_date:
            # if True:
                column_present = controller.is_column_present(stock, timeframe, column)
                if not column_present:
                    controller.apply_indicators(stock, timeframe, column, indicator_args)
                    create_fast_cache(stock, timeframe, column, other_args, indicator_args[0], cache_name)
                else:
                    create_fast_cache(stock, timeframe, column, other_args, indicator_args[0], cache_name)
        else:
            controller.apply_indicators(stock, timeframe, column, indicator_args)
            create_fast_cache(stock, timeframe, column, other_args, indicator_args[0], cache_name)

def create_file(file_list, processes=12):
    """Create fastCache files for each entry in file_list using multiprocessing."""
    cache_dir = "fastCache"
    os.makedirs(cache_dir, exist_ok=True)

    # Use Pool to multiprocess entries
    with Pool(processes=processes) as pool:
        pool.map(process_entry, file_list)



def return_fastCache_file(fast_cache_list, stock):
    collection_of_cache = []
    collection_of_cache_name = []
    for i in range(len(fast_cache_list)):
        if fast_cache_list[i][0] == stock:
            # fastCache_saving.read_file()
            file_path = f"fastCache/{fast_cache_list[i][3]}"
            file = fastCache_saving.read_file(file_path)
            # file = pl.read_parquet(f'{file_path}.parquet' ,low_memory=False )
            file = file["data"]
            # file = file.to_numpy()
            
            collection_of_cache.append(file)
            collection_of_cache_name.append(fast_cache_list[i][3])
    return np.array(collection_of_cache), collection_of_cache_name



# def return_fastCache_file(fast_cache_list, stock):
#     # Filter only matching entries
#     matching = [entry for entry in fast_cache_list if entry[0] == stock]
#     collection_of_cache = []
#     collection_of_cache_name = []
#     for entry in matching:
#         file_path = f"fastCache/{entry[3]}"
#         file = fastCache_saving.read_file(file_path)
#         # Only load "data" and convert to numpy once
#         np_array = file["data"]
#         collection_of_cache.append(np_array)
#         collection_of_cache_name.append(entry[3])
#     # .to_numpy()
#     return np.array(collection_of_cache), collection_of_cache_name
