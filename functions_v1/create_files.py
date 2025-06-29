import os
from functions import fastCache_saving, df_saving, backtesting_functions, functions, controller
import numpy as np  
import pandas as pd


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
    else:
        uniqueTime = functions.timeframe_divide_uniqueTime(smallest)

    smallestLastTime = functions.timeframe_divide_uniqueTime(smallest)
    smallestLastTime = int("".join(uniqueTime.loc[uniqueTime.index[-1], f"uniqueTime_{smallest}"].split(":")))


    arr = np.empty(len(df_smallest), dtype=np.object_)
    date_arr = np.empty(len(df_smallest), dtype=np.int64)
    for j in range(0, len(df_smallest)):
        arr[j] = backtesting_functions.select_candles_temp(stock, column, int(df_data[j][datetime_index]), df, uniqueTime, tf, df_smallest, smallest, smallestLastTime, candle)
        date_arr[j] = df_data[j][date_index]

    arr = pd.DataFrame({"data" : arr, "date_number" : date_arr})

    arr.index.name = "index"
    fastCache_saving.to_file(arr, f"fastCache/{shortForm_fastCache}")



def create_file(file_list):
    path = "fastCache"
    os.makedirs(path, exist_ok=True)        # create directory if it doesn't exist
    for i in range(len(file_list)):        
        if fastCache_saving.if_path_exist(f"{path}/{file_list[i][3]}") == False:     # check if cache file not exixts
            stock = file_list[i][0]
            timeframe_value = file_list[i][1]
            if timeframe_value == "Daily" or timeframe_value == "Weekly" or timeframe_value == "Monthly":
                path = f"indicator_process/{stock}_{timeframe_value}"
            
            elif 1 <= timeframe_value and timeframe_value <= 60*5:
                path = f"indicator_process/"+str(stock)+ "_"+str(timeframe_value)+"min"
            if df_saving.if_path_exist(path) == True:
                check = controller.is_column_present(file_list[i][0], file_list[i][1] ,file_list[i][2])      # check if column not exists
                if check == False:
                
            
                    controller.apply_indicators(file_list[i][0], file_list[i][1] ,file_list[i][2], file_list[i][4])       # create columns 
                
                    print("Created", file_list[i][2], controller.is_column_present(file_list[i][0], file_list[i][1] ,file_list[i][2]))
                    create_fast_cache(file_list[i][0], file_list[i][1], file_list[i][2], file_list[i][5], file_list[i][4][0], file_list[i][3])
                else:
                    create_fast_cache(file_list[i][0], file_list[i][1], file_list[i][2], file_list[i][5], file_list[i][4][0], file_list[i][3])
            else:
                controller.apply_indicators(file_list[i][0], file_list[i][1] ,file_list[i][2], file_list[i][4])       # create columns    
                create_fast_cache(file_list[i][0], file_list[i][1], file_list[i][2], file_list[i][5], file_list[i][4][0], file_list[i][3])
                
        else:
            print("File already exists", file_list[i][3])
            stock = file_list[i][0]
            timeframe_value = file_list[i][1]
            if timeframe_value == "Daily" or timeframe_value == "Weekly" or timeframe_value == "Monthly":
                path_column = f"indicator_process/{stock}_{timeframe_value}"
            
            elif 1 <= timeframe_value and timeframe_value <= 60*5:
                path_column = f"indicator_process/"+str(stock)+ "_"+str(timeframe_value)+"min"
            
            if df_saving.if_path_exist(path_column) == True:
                df_last_date = df_saving.read_file(path_column, col=["date_number"])
                df_last_date = df_last_date.loc[df_last_date.index[-1] ,"date_number"]
                print("df_last_date", df_last_date)
                # df_length = df_last_date.loc[df_last_date.index[-1] ,"date_number"]

                df_cache_last_date = fastCache_saving.read_file(f"{path}/{file_list[i][3]}")
                df_cache_last_date = df_cache_last_date.loc[df_cache_last_date.index[-1] ,"date_number"]
                print("df_cache_last_date", df_cache_last_date)
                if df_last_date > df_cache_last_date:
                    check = controller.is_column_present(file_list[i][0], file_list[i][1] ,file_list[i][2])      # check if column not exists
                    if check == False:
                    
                
                        controller.apply_indicators(file_list[i][0], file_list[i][1] ,file_list[i][2], file_list[i][4])       # create columns 
                    
                        print("Created", file_list[i][2], controller.is_column_present(file_list[i][0], file_list[i][1] ,file_list[i][2]))
                        create_fast_cache(file_list[i][0], file_list[i][1], file_list[i][2], file_list[i][5], file_list[i][4][0], file_list[i][3])
                    else:
                        create_fast_cache(file_list[i][0], file_list[i][1], file_list[i][2], file_list[i][5], file_list[i][4][0], file_list[i][3])

            else:
                controller.apply_indicators(file_list[i][0], file_list[i][1] ,file_list[i][2], file_list[i][4])       # create columns    
                create_fast_cache(file_list[i][0], file_list[i][1], file_list[i][2], file_list[i][5], file_list[i][4][0], file_list[i][3])







def return_fastCache_file(fast_cache_list, stock):
    collection_of_cache = []
    collection_of_cache_name = []
    for i in range(len(fast_cache_list)):
        if fast_cache_list[i][0] == stock:
            # fastCache_saving.read_file()
            file_path = f"fastCache/{fast_cache_list[i][3]}"
            file = fastCache_saving.read_file(file_path)
            file = file["data"]
            file = file.to_numpy()
            
            collection_of_cache.append(file)
            collection_of_cache_name.append(fast_cache_list[i][3])
    return collection_of_cache, collection_of_cache_name