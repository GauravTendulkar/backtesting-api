import pandas as pd
from functions import indicators
from functions.thread_safe_LRU_cache import ThreadSafeLRUCache
import redis_cache  
import json
import numpy as np
from cache_manager import cache_ts, cache_for_nparray
from numba import njit
from functions import df_saving, fastCache_saving
from functions import functions
import os
import re


# cache_ts = ThreadSafeLRUCache(maxsize=128000)

# def if_index_exist(arr_list, number):

#     try:
#         if arr_list[number]:
#             return True
#     except:
#         return False

    
def if_index_exist(arr_list, arr_number):
    
    try:
        for i in range(0, len(arr_number)):
            # print(arr_number[i])
            if arr_list[arr_number[i]]:
                pass
        return True
    except:
            return False
#________________________________________________________________________*********************************
#
#

def get_list_for_generator(data1, list_stocks):
    arr_indicator_generator = []
    arr_fast_cache = []


    def get_indicator_list(data1):

        for i in data1:
            if "indicator" in i:
                # print("___________________")
                indicator_arr, indicator_shortform = indicators.get_indicator_shortform(None, i["indicator"], 0)
                # print("get_list_for_generator", indicator_arr)
                if if_index_exist(indicator_arr, [2]) and (indicator_arr[2] == "sma" 
                    or indicator_arr[2] == "ema"
                    or indicator_arr[2] == "rsi"
                    or indicator_arr[2] == "BBbasis" or indicator_arr[2] == "BBupper" or indicator_arr[2] == "BBlower"
                    or indicator_arr[2] == "close" 
                    or indicator_arr[2] == "high" 
                    or indicator_arr[2] == "low" 
                    or indicator_arr[2] == "open" 
                    or indicator_arr[2] == "volume"
                    or indicator_arr[2] == "macdLine" or indicator_arr[2] == "signalLine" or indicator_arr[2] == "macdHistogram"
                    or indicator_arr[2] == "supertrend"
                    or indicator_arr[2] == "H1" or indicator_arr[2] == "H2" or indicator_arr[2] == "H3" or indicator_arr[2] == "H4" 
                    or indicator_arr[2] == "L1" or indicator_arr[2] == "L2" or indicator_arr[2] == "L3" or indicator_arr[2] == "L4"
                    or indicator_arr[2] == "datetime_number" ):
                        for l in list_stocks:
                            arr = []
                            arr.append(l)
                            arr.append(indicator_arr[1])
                            arr.append(indicator_shortform)
                            arr.append(indicator_arr)
                            # if indicator_arr[2] != "datetime_number":
                                
                            arr_indicator_generator.append(arr)
                            if indicator_arr[1] == "Daily" or indicator_arr[1] == "Weekly" or indicator_arr[1] == "Monthly":
                                a = f"'{indicator_arr[1]}'"
                            else:
                                a = f"{indicator_arr[1]}"
                            

                            if indicator_arr[0][:1] == "=":
                                a =  f"backtesting_functions.select_candles(list_stocks[t], i, '{indicator_shortform}', int(df_data[i][datetime_index]), dict_of_timeframes[{a}], dict_of_time[{a}], {a}, df, smallest, df_time, '{indicator_arr[0]}')"
                            else:
                                a =  f"backtesting_functions.select_candles(list_stocks[t], i, '{indicator_shortform}', int(df_data[i][datetime_index]), dict_of_timeframes[{a}], dict_of_time[{a}], {a}, df, smallest, df_time, {indicator_arr[0]})"
                            
                            arr_fast_cache.append(a)
            # for special functions
                elif if_index_exist(indicator_arr, [0]):  
                    
                    if  indicator_arr[0] == "max": 
                        # print("[indicator_arr[2]]", [indicator_arr[2]])
                        get_indicator_list([indicator_arr[2]])
                        get_indicator_list([{'indicator': [{'value': indicator_arr[2]["indicator"][0]["value"]}, {'value': indicator_arr[2]["indicator"][1]["value"]}, {'value': 'datetime_number'}]}])
                    elif  indicator_arr[0] == "min": 
                        # print("[indicator_arr[2]]", [indicator_arr[2]])
                        get_indicator_list([indicator_arr[2]])
                        get_indicator_list([{'indicator': [{'value': indicator_arr[2]["indicator"][0]["value"]}, {'value': indicator_arr[2]["indicator"][1]["value"]}, {'value': 'datetime_number'}]}])

                    elif  indicator_arr[0] == "ceil":
                        get_indicator_list([indicator_arr[1]])
                    elif  indicator_arr[0] == "floor":
                        get_indicator_list([indicator_arr[1]])
                    elif  indicator_arr[0] == "abs":
                        get_indicator_list([indicator_arr[1]])
                    elif  indicator_arr[0] == "log10":
                        get_indicator_list([indicator_arr[1]])
                    elif  indicator_arr[0] == "log":
                        get_indicator_list([indicator_arr[1]])
                    
                    
                        # print("indicator_arr", [indicator_arr[1]])
                # elif if_index_exist(indicator_arr, [0]):  
                    
                else:
            
                    pass
                    # print("hello")
                

            elif "condition" in i:
                # print(i["condition"])
                get_indicator_list(i["condition"])
            elif "AND" in i:
                # print(i["AND"])
                get_indicator_list(i["AND"])

            elif "OR" in i:
                # print(i["OR"])
                get_indicator_list(i["OR"])
            
    get_indicator_list(data1)

    temp = []
    for i in range(0, len(arr_indicator_generator)):

        if arr_indicator_generator[i] not in temp:
            temp.append(arr_indicator_generator[i])
    return temp, arr_fast_cache
    # return temp

#________________________________________________________________________
#
# output
# [[15, ['close']], ['Daily', ['high']]]

def convert_data_for_csv_loading(a):
    temp = {}

    # Iterate through the list `a`
    for i in range(len(a)):
        key = a[i][1]  # The second element ('Daily', 120, etc.)
        value = a[i][2]  # The third element ("sma9_close")

        # If key exists in the dictionary, append only unique values
        if key in temp:
            if value not in temp[key]:
                temp[key].append(value)
        else:
            temp[key] = [value]  # If key doesn't exist, create a new list

    # Convert the dictionary to the desired output format (list of lists)
    result = [[key, values] for key, values in temp.items()]
    return result
#________________________________________________________________________
#
# to convert array into dict of dataframes(multi time frame data in single dict)
#
def get_csv_dict(stock, csv_import):
    temp = {}
    temp_time = {}

    for i in range(0, len(csv_import)):
        
        if isinstance(csv_import[i][0], int):
            if 1 <= csv_import[i][0] and csv_import[i][0] < 60*5:
                arr = {"datetime", "date_number", "time_number", "datetime_number", "close"}
                arr.update(csv_import[i][1])
                arr = list(arr)
                path = f"indicator_process/{stock}_{csv_import[i][0]}min"
                # temp[csv_import[i][0]] = pd.read_csv(path,low_memory=False,parse_dates=['datetime'],index_col=['datetime'], usecols=arr)
                temp[csv_import[i][0]] = df_saving.read_file(path, col=arr)
                path_time = f"Clean_data/uniqueTime_{csv_import[i][0]}.csv"
                # temp_time[csv_import[i][0]] = pd.read_csv(path_time,low_memory=False,index_col=[0])
                temp_time[csv_import[i][0]] = pd.read_csv(path_time,low_memory=False,index_col=[0])
                
                

        elif isinstance(csv_import[i][0], str):
            if csv_import[i][0] == "Daily" or csv_import[i][0] == "Weekly" or csv_import[i][0] == "Monthly":
                arr = {"datetime", "date_number", "time_number", "datetime_number", "close"}
                arr.update(csv_import[i][1])
                arr = list(arr)
                path = f"indicator_process/{stock}_{csv_import[i][0]}"
                # temp[csv_import[i][0]] = pd.read_csv(path,low_memory=False,parse_dates=['datetime'],index_col=['datetime'], usecols=arr)
                temp[csv_import[i][0]] = df_saving.read_file(path, col=arr)
                
                temp_time[csv_import[i][0]] = None
                
    return temp, temp_time

#________________________________________________________________________*********************************
#
# returns entry in form of equation

def entry_to_equation(temp, option):
    temp_str = ""
    index = 0
    for i in temp:
        if "indicator" in i:
            # print('i["indicator"]', i["indicator"])
            indicator_arr, indicator_shortform = indicators.get_indicator_shortform(None, i["indicator"], 0)
            # print("indicator_shortform")
            # print(indicator_shortform)
            
            if if_index_exist(indicator_arr, [0]):
                # print("len(indicator_arr)", indicator_arr, indicator_shortform)
                if indicator_arr[0] == "entry":
                    # temp_str += "float(Tracking.loc[Tracking.index[-1], 'entry'])"
                    temp_str += "float(Tracking.loc[Tracking_index, 'entry'])"
                elif indicator_arr[0] == "time":
                    # temp_str += "float(Tracking.loc[Tracking.index[-1], 'entry'])"
                    temp_str += "int(df_data[i][time_index]/100)"
                elif indicator_arr[0] == "countPrevTrades":
                    temp_str += "functions.count_previous_entry_intraday(Tracking, int(df_data[i][date_index]))"

                elif indicator_arr[0] == "number":
                
                    # print("*******************")
                    # print("len(indicator_arr) == 1",indicator_arr, indicator_shortform)
                    temp_str += f"{indicator_arr[1]}"
                elif indicator_arr[0] == "+" or indicator_arr[0] == "-" or indicator_arr[0] == "/" or indicator_arr[0] == "*" :
                    temp_str += f"{indicator_arr[0]}"
                elif indicator_arr[0] == "(" or indicator_arr[0] == ")" :
                    temp_str += f"{indicator_arr[0]}"
                elif indicator_arr[0] == "<" or indicator_arr[0] == "<=" or indicator_arr[0] == ">" or indicator_arr[0] == ">=" or indicator_arr[0] == "==" or indicator_arr[0] == "!=":
                    temp_str += f"{indicator_shortform}"
                 
                elif  indicator_arr[0] == "ceil":
                    
                    temp_str += f"functions.ceil({entry_to_equation([indicator_arr[1]], None)} )"
                elif  indicator_arr[0] == "floor":
                    
                    temp_str += f"functions.floor({entry_to_equation([indicator_arr[1]], None)} )"
                elif  indicator_arr[0] == "abs":
                    
                    temp_str += f"functions.abs({entry_to_equation([indicator_arr[1]], None)} )"
                elif  indicator_arr[0] == "log10":
                    
                    temp_str += f"functions.log10({entry_to_equation([indicator_arr[1]], None)} )"
                elif  indicator_arr[0] == "log":
                    
                    temp_str += f"functions.log({entry_to_equation([indicator_arr[1]], None)} )"

                elif  indicator_arr[0] == "max":
                   
                    print("indicator_arr", indicator_arr)
                    indicator_arr_t, indicator_shortform_t = indicators.get_indicator_shortform(None, indicator_arr[2]["indicator"], 0)
                    iarr = indicator_arr[2]["indicator"][1]["value"]
                    if iarr == "Daily" or iarr == "Weekly" or iarr == "Monthly":
                        a = f"'{iarr}'"
                    else:
                        a = f"{iarr}"
                    temp
                    temp_str += f"backtesting_functions.find_max_df( '{indicator_shortform_t}',{indicator_arr[1]}, dict_of_timeframes[{a}] , {entry_to_equation([{'indicator': [{'value': indicator_arr[2]["indicator"][0]["value"]}, {'value': indicator_arr[2]["indicator"][1]["value"]}, {'value': 'datetime_number'}]}], None)} )"
                elif  indicator_arr[0] == "min":
                   
                    print("indicator_arr", indicator_arr)
                    indicator_arr_t, indicator_shortform_t = indicators.get_indicator_shortform(None, indicator_arr[2]["indicator"], 0)
                    iarr = indicator_arr[2]["indicator"][1]["value"]
                    if iarr == "Daily" or iarr == "Weekly" or iarr == "Monthly":
                        a = f"'{iarr}'"
                    else:
                        a = f"{iarr}"
                    temp
                    temp_str += f"backtesting_functions.find_min_df( '{indicator_shortform_t}',{indicator_arr[1]}, dict_of_timeframes[{a}] , {entry_to_equation([{'indicator': [{'value': indicator_arr[2]["indicator"][0]["value"]}, {'value': indicator_arr[2]["indicator"][1]["value"]}, {'value': 'datetime_number'}]}], None)} )"
                        

            if if_index_exist(indicator_arr, [2]):
                if (indicator_arr[2] == "close" 
                or indicator_arr[2] == "high" 
                or indicator_arr[2] == "low"
                or indicator_arr[2] == "open" 
                or indicator_arr[2] == "volume"
                or indicator_arr[2] == "sma"
                or indicator_arr[2] == "ema"
                or indicator_arr[2] == "rsi"
                or indicator_arr[2] == "BBbasis"
                or indicator_arr[2] == "BBupper"
                or indicator_arr[2] == "BBlower"
                or indicator_arr[2] == "macdLine"
                or indicator_arr[2] == "signalLine"
                or indicator_arr[2] == "macdHistogram"
                or indicator_arr[2] == "supertrend"
                or indicator_arr[2] == "H1" or indicator_arr[2] == "H2" or indicator_arr[2] == "H3" or indicator_arr[2] == "H4" 
                or indicator_arr[2] == "L1" or indicator_arr[2] == "L2" or indicator_arr[2] == "L3" or indicator_arr[2] == "L4"
                or indicator_arr[2] == "datetime_number"):

                    # if indicator_arr[2] == "datetime_number":
                    #     indicator_shortform = "datetime_number"
                    a = f"{indicator_arr[1]}"
                    string_s = f"list_stocks[t]_{indicator_shortform}_{a}_smallest_df_time_{indicator_arr[0]}"
                    modified_string = re.sub(r'list_stocks\[t\]', r'{list_stocks[t]}', string_s)
                    modified_string = re.sub(r'smallest', r'{smallest}', modified_string)
                    modified_string = re.sub(r'df_time', r'{df_time}', modified_string)
                    modified_string = 'f"' + modified_string + '"' 
                    # print("modified_string", modified_string)
                        
                    temp_str += f"df_fastCache_colum_arr[i][fastCache_colum_name.index({modified_string})]"
                    # if indicator_arr[1] == "Daily" or indicator_arr[1] == "Weekly" or indicator_arr[1] == "Monthly":
                    #     a = f"'{indicator_arr[1]}'"
                    # else:
                    #     a = f"{indicator_arr[1]}"
                    

                    # if indicator_arr[0][:1] == "=":
                        
                    #     temp_str +=  f"backtesting_functions.select_candles(list_stocks[t], i, '{indicator_shortform}', int(df_data[i][datetime_index]), dict_of_timeframes[{a}], dict_of_time[{a}], {a}, df, smallest, df_time, '{indicator_arr[0]}')"
                        
                    # else:
                        
                    #     temp_str +=  f"backtesting_functions.select_candles(list_stocks[t], i, '{indicator_shortform}', int(df_data[i][datetime_index]), dict_of_timeframes[{a}], dict_of_time[{a}], {a}, df, smallest, df_time, {indicator_arr[0]})"
                        
                        
                    


        
            
            temp_str = temp_str + " "
        elif "condition" in i:
            if len(temp) == 1:
                temp_str = temp_str + f"( {entry_to_equation(i["condition"], "condition")} )"
            else:
                # print(option)
                temp_str = temp_str + f"( {entry_to_equation(i["condition"], "condition")} )" 
                index += 1
                if index < len(temp):
                    temp_str = temp_str + " " + option + " "

        elif "AND" in i:
            
            temp_str += f"( {entry_to_equation(i['AND'], 'and')} )"
        elif "OR" in i:
            temp_str += f"( {entry_to_equation(i['OR'], 'or')} )"
    return temp_str

#________________________________________________________________________
#
#
avoid_indicators = ["H1", "H2","H3","H4", "L1", "L2","L3","L4", 
                    "CPRPP", "CPRBC", "CPRTC", "pivotR1", "pivotR2", "pivotR3", "pivotR4", "pivotS1", "pivotS2", "pivotS3", "pivotS4"]
#________________________________________________________________________
# def select_candles(stock, i, column, row, df, uniqueTime, tf, df_smallest,  smallest, smallestLastTime, candle):
    # print("candle out")
    # @njit
def select_candles_temp(stock, column, row, df, uniqueTime, tf, df_smallest, smallest, smallestLastTime,  candle):
    

    if tf == "Monthly":
        # print("Weekly", row)
        # row = row // 10**6
        return select_column_row_Monthly(column, row, df, df_smallest, smallest, candle)
    elif tf == "Weekly":
        # print("Weekly", row)
        # row = row // 10**6
        return select_column_row_Weekly(column, row, df, df_smallest, smallest, candle)
    
    
    
    elif tf == "Daily":
        
        # print("Daily", int(str(row)[8:]), smallestLastTime, int(str(row)[8:]) >= smallestLastTime)
        if candle == 0:
            if column in avoid_indicators:
                row = row // 10**6
                    
                get_cache = cache_ts.get(stock, column, row, tf, candle)
                # print(get_cache)
                if get_cache != "Not Found":
                    return get_cache
                return_value = select_column_row_Daily(column, row, df, candle)
                cache_ts.set(return_value, stock, column, row, tf, candle )
                return return_value
            
            if smallestLastTime is None and smallest == "Daily":
                row = row // 10**6
                return select_column_row_Daily(column, row, df, candle)
            if int(str(row)[8:]) >= smallestLastTime :#and isinstance(smallest, int):
                row = row // 10**6
            
                return select_column_row_Daily(column, row, df, candle)
                
            return None
        
        else:
            row = row // 10**6
                
            get_cache = cache_ts.get(stock, column, row, tf, candle)
            # print(get_cache)
            if get_cache != "Not Found":
                return get_cache
            return_value = select_column_row_Daily(column, row, df, candle)
            cache_ts.set(return_value, stock, column, row, tf, candle )
            return return_value
        
        # return select_column_row_Daily(column, row, df, candle)
    else:
        # try:
        if isinstance(candle, int):
            if candle <= 0:
                
                return select_column_row(column, row, df,uniqueTime, tf, smallest, candle)
            
                # get_cache = cache_ts.get(stock, column, row, tf, candle)
                # # print(get_cache)
                # if get_cache != "Not Found":
                #     return get_cache
                # return_value = select_column_row(column, row, df,uniqueTime, tf, candle)
                # cache_ts.set(return_value, stock, column, row, tf, candle )
                # return return_value
                
            

        if isinstance(candle, str):
            
            if candle.startswith("=-"):
                row = row // 10**6
                get_cache = cache_ts.get(stock, column, row, tf, candle)
                # print(get_cache)
                if get_cache != "Not Found":
                    return get_cache
                return_value = select_column_row_for_prev_const_candle(column, row, df, uniqueTime, candle)
                cache_ts.set(return_value, stock, column, row, tf, candle )
                return return_value
            
            elif candle.startswith("="):

                # print(column, row, tf, candle)
                target_time = cache_ts.get(tf, candle)
                
                if target_time == "Not Found":
                    
                    target_time = int("".join(uniqueTime.iloc[int(candle[1:]) - 1, 0].split(":")))
                    cache_ts.set(tf, candle )
                return_value = select_column_row_for_current_const_candle( column, row, df, uniqueTime, candle, target_time, stock, tf)
                # cache_ts.set(return_value, column, row, tf, candle )
                # print(return_value)
                return return_value
    
    
    # get_cache_1 = cache_for_nparray.get((stock, column, tf, smallest, smallestLastTime, candle))
    # try:
    #     return get_cache_1[i]

    # except:
    #     if get_cache_1 == "Not Found":
    #         df_data = df_smallest.to_numpy()
    #         data_column = list(df_smallest.columns)
    #         datetime_index = data_column.index("datetime_number")
    #         # print(int(df_data[0][datetime_index]), list(df_smallest.columns), data_column.index("datetime_number"), (stock, column, tf, smallest, smallestLastTime, candle))

    #         arr = np.empty(len(df_smallest), dtype=np.float64)

    #         for j in range(0, len(df_smallest)):
    #             arr[j] = select_candles_temp(stock, column, int(df_data[j][datetime_index]), df, uniqueTime, tf, df_smallest, smallest, smallestLastTime, candle)
    #             # print(df_data[j][datetime_index], arr[j])
    #         cache_for_nparray.set(arr, (stock, column, tf, smallest, smallestLastTime, candle))
    #         print("Not Found")
    #         return arr[i]

    
    # try:
    #     path = f"indicator_process/fast_cache/{stock}_{column}_{tf}_{smallest}_{smallestLastTime}_{candle}"
    #     file_path = f"{path}.csv"
    #     if os.path.exists(file_path):
    #         file = pd.read_csv(f"{path}.csv" , low_memory=False,index_col=["index"])
    #         file = file.to_numpy()
    #         file[i]
    #         print("pass", file[i])
    #     else:
    #         df_data = df_smallest.to_numpy()
    #         data_column = list(df_smallest.columns)
    #         datetime_index = data_column.index("datetime_number")
    #         arr = np.empty(len(df_smallest), dtype=np.float64)

    #         for j in range(0, len(df_smallest)):
    #             arr[j] = select_candles_temp(stock, column, int(df_data[j][datetime_index]), df, uniqueTime, tf, df_smallest, smallest, smallestLastTime, candle)
    #         arr = pd.DataFrame(arr)
    #         # arr = arr.rename(index={"Unnamed: 0": 'index'})
    #         arr.index.name = "index"
    #         # print(arr)
    #         arr.to_csv(f"{path}.csv")
    #         if os.path.exists(file_path):
    #             file = pd.read_csv(f"{path}.csv" , low_memory=False,index_col=["index"])
    #             file = file.to_numpy()
    #             file[i]
    #         print("created", f"{stock}_{column}_{tf}_{smallest}_{smallestLastTime}_{candle}")


    # except Exception as e:

    #     print("Fail", e)
    #     pass

    # return file, f"{stock}_{column}_{tf}_{smallest}_{smallestLastTime}_{candle}"
def select_candles(stock, i, column, row, df, uniqueTime, tf, df_smallest,  smallest, smallestLastTime, candle):
    
    try:
        path = f"indicator_process/fast_cache/{stock}_{column}_{tf}_{smallest}_{smallestLastTime}_{candle}"
        file_path = f"{path}"
        if fastCache_saving.if_path_exist(file_path):
            file = fastCache_saving.read_file(file_path)
            # file = pd.read_csv(f"{path}.csv" , low_memory=False,index_col=["index"])
            file = file.to_numpy()
            file[i]
            print("pass", file[i])
        else:
            with fastCache_saving.lock_file(file_path):
                if fastCache_saving.if_path_exist(file_path) == False:
                    df_data = df_smallest.to_numpy()
                    data_column = list(df_smallest.columns)
                    datetime_index = data_column.index("datetime_number")
                    arr = np.empty(len(df_smallest), dtype=np.float64)

                    for j in range(0, len(df_smallest)):
                        arr[j] = select_candles_temp(stock, column, int(df_data[j][datetime_index]), df, uniqueTime, tf, df_smallest, smallest, smallestLastTime, candle)
                    arr = pd.DataFrame(arr)
                    # arr = arr.rename(index={"Unnamed: 0": 'index'})
                    arr.index.name = "index"
                    # print(arr)
                    fastCache_saving.to_file(arr, file_path)

                    # arr.to_csv(f"{path}.csv")
                if fastCache_saving.if_path_exist(file_path):
                    # file = pd.read_csv(f"{path}.csv" , low_memory=False,index_col=["index"])
                    file = fastCache_saving.read_file(file_path)
                    file = file.to_numpy()
                    file[i]
                print("created", f"{stock}_{column}_{tf}_{smallest}_{smallestLastTime}_{candle}")


    except Exception as e:

        print("Fail", f"{stock}_{column}_{tf}_{smallest}_{smallestLastTime}_{candle}")

        path = f"indicator_process/fast_cache/{stock}_{column}_{tf}_{smallest}_{smallestLastTime}_{candle}"
        file_path = f"{path}"
        if fastCache_saving.if_path_exist(file_path):
            file = fastCache_saving.read_file(file_path)
            # file = pd.read_csv(f"{path}.csv" , low_memory=False,index_col=["index"])
            file = file.to_numpy()

            df_data = df_smallest.to_numpy()
            data_column = list(df_smallest.columns)
            datetime_index = data_column.index("datetime_number")

            new_length = len(df_smallest)
            num_to_add = new_length - len(file)
            empty_values = np.empty(num_to_add, dtype=np.float64)
            arr = np.append(file, empty_values)
            # print("length", len(file), new_length)


            for j in range(len(file), len(df_smallest)):
                # print(stock, column, int(df_data[j][datetime_index]))
                arr[j] = select_candles_temp(stock, column, int(df_data[j][datetime_index]), df, uniqueTime, tf, df_smallest, smallest, smallestLastTime, candle)
            arr = pd.DataFrame(arr)
                    # arr = arr.rename(index={"Unnamed: 0": 'index'})
            arr.index.name = "index"
                    
            fastCache_saving.to_file(arr, file_path)

            if fastCache_saving.if_path_exist(file_path):
                # file = pd.read_csv(f"{path}.csv" , low_memory=False,index_col=["index"])
                file = fastCache_saving.read_file(file_path)
                file = file.to_numpy()
                file[i]

            # df_data = df_smallest.to_numpy()
            # data_column = list(df_smallest.columns)
            # datetime_index = data_column.index("datetime_number")
            # arr = np.empty(len(df_smallest), dtype=np.float64)



        
    functions.latest_file(f"{stock}_{column}_{tf}_{smallest}_{smallestLastTime}_{candle}", 1000)

    return file, f"{stock}_{column}_{tf}_{smallest}_{smallestLastTime}_{candle}"

        
            
        
    

    # return_value = select_candles_temp(stock, column, row, df, uniqueTime, tf, df_smallest, smallest, smallestLastTime, candle)

    # return return_value

        
#________________________________________________________________________
# for selecting row and column value of any time frame
# backtesting_functions.select_column_row("time_number", df.loc[df.index[i], "datetime_number"], dict_of_timeframes[15])

# def select_column_row(column, row, df, prev_candles):

#     # Filter the DataFrame to find the row where datetime_number is less than or equal to the specified 'row'
#     filtered_df = df[df['datetime_number'] <= row]
    
#     # Return the last (maximum) datetime_number that satisfies the condition
#     if not filtered_df.empty:
#         try:
#             return filtered_df[column].iloc[-1+prev_candles]
#         except:
#             pass
    
#     return None  # Return None if no matching row is found

# # it takes 40s seconds
# def select_column_row(column, row, df, prev_candles):
#     # Use vectorized operation to find indices where 'datetime_number' is less than or equal to 'row'
#     mask = df['datetime_number'] <= row
#     indices = mask.values.nonzero()[0]  # Get indices where condition is True

#     if indices.size > 0:
#         try:
#             # Compute the target index efficiently
#             target_index = indices[-1] + prev_candles
#             if 0 <= target_index and target_index < len(df):
#                 return df.iloc[target_index][column]
#         except IndexError:
#             pass

# @njit
# def select_column_row_jit(column, row, datetime_numbers, column_values, prev_candles, extraTime):
#     indices = np.where(datetime_numbers <= row)[0]
#     if extraTime :
#         if indices.size > 0:
#             target_index = indices[-1]  + prev_candles
#             if 0 <= target_index and target_index < len(column_values):
#                 return column_values[target_index]
#     else:
#         if indices.size > 0:
#             target_index = indices[-1] -1 + prev_candles
#             if 0 <= target_index and target_index < len(column_values):
#                 return column_values[target_index]
#     return None

# # Wrapper to integrate with Pandas
# # it takes 31.4s seconds
# def select_column_row(column, row, df,uniqueTime, tf, prev_candles):

#     if int(str(row)[8:]) == 91500:
#         return None
#     get_cache = cache_ts.get(f"uniqueTime_{tf}", -1)
#                     # print(get_cache)
#     if get_cache != "Not Found":
        
#         lastValue = get_cache
#     else:
#         # print("lastValue Not Found")
#         lastValue = int("".join(uniqueTime[f"uniqueTime_{tf}"].iloc[-1].split(":")))
#         cache_ts.set(lastValue, f"uniqueTime_{tf}", -1 )

#     # lastValue = int("".join(uniqueTime[f"uniqueTime_{tf}"].iloc[-1].split(":")))
#          # "".join(t.split(":"))
#     extraTime = False
#     if int(str(row)[8:]) > lastValue:
#         extraTime = True
#     datetime_numbers = df['datetime_number'].values
#     column_values = df[column].values
#     return select_column_row_jit(column, row, datetime_numbers, column_values, prev_candles, extraTime)


@njit
def select_column_row_jit(column, row, datetime_numbers, column_values, prev_candles, tf, smallest):
    indices = np.where(datetime_numbers <= row)[0]
    
    if indices.size > 0:
        target_index = indices[-1]  + prev_candles
        if 0 <= target_index and target_index < len(column_values):
            # print(row + smallest*100, ">=" ,datetime_numbers[target_index] + tf*100)
            if row + (smallest*100) >= datetime_numbers[target_index] + tf*100 :
            # if smallest >= tf: 

                return column_values[target_index]
    
    return None

# Wrapper to integrate with Pandas
# it takes 31.4s seconds
def select_column_row(column, row, df, uniqueTime, tf, smallest, prev_candles):

    
    datetime_numbers = df['datetime_number'].values
    column_values = df[column].values
    
    return select_column_row_jit(column, row, datetime_numbers, column_values, prev_candles, tf, smallest)

#________________________________________________________________________
# def select_column_row_Daily(column, row, df, prev_candles):

#     # Filter the DataFrame to find the row where datetime_number is less than or equal to the specified 'row'
#     filtered_df = df[df['date_number'] <= row // 10**6]
    
#     # Return the last (maximum) datetime_number that satisfies the condition
#     if not filtered_df.empty:
#         try:
#             return filtered_df[column].iloc[-1+prev_candles]
#         except:
#             pass
    
#     return None  # Return None if no matching row is found



def select_column_row_Daily(column, row, df, prev_candles):
    # Compute the daily row limit directly
    # daily_limit = row // 10**6
    daily_limit = row
    # Use a boolean mask to find rows where 'date_number' is less than or equal to 'daily_limit'
    mask = df['date_number'] <= daily_limit
    indices = mask.values.nonzero()[0]  # Get indices of True values

    if indices.size > 0:
        try:
            # Calculate the target index
            target_index = indices[-1] + prev_candles
            if 0 <= target_index and target_index < len(df):
                return df.iloc[target_index][column]
        except IndexError:
            pass

    return None

#________________________________________________________________________

def select_column_row_Weekly(column, row, df, df_smallest, smallest, prev_candles):
    # get smallest df and get the index of smallest df and increment by one
    
    mask = df_smallest['datetime_number'] <= row
    indices = mask.values.nonzero()[0]
    if indices.size > 0:
        target_index_smallest = indices[-1] + 1
        if 0 <= target_index_smallest and target_index_smallest < len(df_smallest):
            df_smallest_row = df_smallest["datetime_number"].iloc[target_index_smallest]//10**6

    # Compute the daily row limit directly
    daily_limit = row // 10**6
    # daily_limit = row
    # Use a boolean mask to find rows where 'date_number' is less than or equal to 'daily_limit'
    mask = df['date_number'] <= daily_limit
    indices = mask.values.nonzero()[0]  # Get indices of True values

    if indices.size > 0:
        try:
            # Calculate the target index
            target_index = indices[-1] + prev_candles
            # print("Weekly", row, df["datetime_number"].iloc[target_index])

            if 0 <= target_index and target_index < len(df):
                if smallest == "Weekly":
                    return df.iloc[target_index][column]
                elif column in avoid_indicators:
                    return df.iloc[target_index][column]
                elif prev_candles == 0 :
                    try:
                        if df_smallest_row >= df.iloc[indices[-1]+1][column]//10**6:

                            # print("target_index_smallest", row//10**6, df_smallest_row, df.iloc[indices[-1]+1][column]//10**6, df_smallest_row >= df.iloc[indices[-1]+1][column]//10**6)
                            return df.iloc[target_index][column]
                        else:
                            return None
                    except:
                        pass
                    
                else:
                    return df.iloc[target_index][column]
        except IndexError:
            pass

    return None

#________________________________________________________________________

def select_column_row_Monthly(column, row, df, df_smallest, smallest, prev_candles):
    # get smallest df and get the index of smallest df and increment by one
    
    mask = df_smallest['datetime_number'] <= row
    indices = mask.values.nonzero()[0]
    if indices.size > 0:
        target_index_smallest = indices[-1] + 1
        if 0 <= target_index_smallest and target_index_smallest < len(df_smallest):
            df_smallest_row = df_smallest["datetime_number"].iloc[target_index_smallest]//10**6

    # Compute the daily row limit directly
    daily_limit = row // 10**6
    # daily_limit = row
    # Use a boolean mask to find rows where 'date_number' is less than or equal to 'daily_limit'
    mask = df['date_number'] <= daily_limit
    indices = mask.values.nonzero()[0]  # Get indices of True values

    if indices.size > 0:
        try:
            # Calculate the target index
            target_index = indices[-1] + prev_candles
            # print("Weekly", row, df["datetime_number"].iloc[target_index])

            if 0 <= target_index and target_index < len(df):
                if smallest == "Monthly":
                    return df.iloc[target_index][column]
                elif column in avoid_indicators:
                    return df.iloc[target_index][column]
            
                elif prev_candles == 0 :
                    try:
                        if df_smallest_row >= df.iloc[indices[-1]+1][column]//10**6:

                            # print("target_index_smallest", row//10**6, df_smallest_row, df.iloc[indices[-1]+1][column]//10**6, df_smallest_row >= df.iloc[indices[-1]+1][column]//10**6)
                            return df.iloc[target_index][column]
                        else:
                            return None
                    except:
                        pass
                    
                else:
                    return df.iloc[target_index][column]
        except IndexError:
            pass

    return None



#________________________________________________________________________
#
# it can return const candle for current day
#it is like orb candle  =1

# def select_column_row_for_current_const_candle(column, row, df, uniqueTime, current_const_candles):
   
#     # Filter the DataFrame to find the row where datetime_number is less than or equal to the specified 'row'
    
#     time_value = int("".join(uniqueTime[uniqueTime.columns.tolist()[0]].iloc[int(current_const_candles[1:])-1].split(":")))
#     filtered_df = df[(df['time_number'] ==  time_value) & (df['date_number'] ==  row // 10**6)]
    
#     if (time_value < (df[df['datetime_number'] <= row]["time_number"].iloc[-1])):
#         return filtered_df[column].iloc[0]
#     else:
#         return None
    

def select_column_row_for_current_const_candle(column, row, df, uniqueTime, current_const_candles, target_time, stock, tf):
    # Extract the target time value from uniqueTime
    # target_time = int("".join(uniqueTime.iloc[int(current_const_candles[1:]) - 1, 0].split(":")))
    
    # Compute the target date
    target_date = row // 10**6
    # print(int(str(row)[8:]),"target_time", target_time, int(str(row)[8:]) <= target_time)
    # datetime_row = target_date*10**6 + target_time
    lofic_for_cache =  int(str(row)[8:]) <= target_time
    if lofic_for_cache :
        return None
    # cache_ts.get(, lofic_for_cache)
    get_cache = cache_ts.get(column, target_date, current_const_candles, target_time, lofic_for_cache, stock, tf)
    # print(get_cache)
    if get_cache != "Not Found":
        return get_cache
    
    # Pre-filter the DataFrame for rows matching the time and date
    filtered_indices = df.index[
        (df['time_number'] == target_time) & (df['date_number'] == target_date)
    ]

    if not filtered_indices.empty:
        # Filter rows with datetime_number <= row
        max_time_df = df[df['datetime_number'] <= row]

        if not max_time_df.empty:
            max_time = max_time_df['time_number'].iloc[-1]

            # Return value if target_time is less than max_time
            if target_time < max_time:
                return_value = df.at[filtered_indices[0], column]
                cache_ts.set(return_value, column, target_date, current_const_candles, target_time, lofic_for_cache, stock, tf )
                return return_value

    return None


#________________________________________________________________________
#
#this returns previous days constant candles
# it is like orb for previous days =-1

# def select_column_row_for_prev_const_candle(column, row, df, uniqueTime, prev_const_candles):
   
#     # datetime_value = (row// 10**6 * 1000000) +  int("".join(uniqueTime[uniqueTime.columns.tolist()[0]].iloc[-1].split(":")))
    
#     try:
#         filtered_df = df[(df['time_number'] == int("".join(uniqueTime[uniqueTime.columns.tolist()[0]].iloc[-1].split(":")))) & 
#                         (df['date_number'] <= row// 10**6 )]
        
#         filtered_df = df[df["datetime_number"]<= filtered_df["datetime_number"].iloc[-2]]
#         return filtered_df[column].iloc[-int(prev_const_candles[2:])]
    
#     except:
#         return None

def select_column_row_for_prev_const_candle(column, row, df, uniqueTime, prev_const_candles):
    try:
        # Compute the target time and date values
        last_time_value = int("".join(uniqueTime.iloc[-1, 0].split(":")))
        # target_date = row // 10**6
        target_date = row 
        # print(target_date)

        # Filter rows matching the target time and date conditions
        mask_time_date = (df['time_number'] == last_time_value) & (df['date_number'] <= target_date)
        matching_indices = mask_time_date.values.nonzero()[0]

        if matching_indices.size > 1:
            # Get the second-to-last matching datetime_number
            second_last_datetime_index = matching_indices[-2]
            max_datetime = df.iloc[second_last_datetime_index]['datetime_number']

            # Filter rows where datetime_number is <= max_datetime
            mask_datetime = df['datetime_number'] <= max_datetime
            valid_indices = mask_datetime.values.nonzero()[0]

            if valid_indices.size > 0:
                # Return the specified column value based on prev_const_candles
                target_index = valid_indices[-int(prev_const_candles[2:])]
                return df.iloc[target_index][column]
    except IndexError:
        pass  # Handle cases where indexing goes out of range

    return None

    
#________________________________________________________________________
#
#this returns date in string into int 
# '2024-11-10' --> 20241110
def date_str_to_int(datepass: str):
    temp = datepass.split("-")
    
    return int(f"{temp[0]}{temp[1]}{temp[2]}")

#________________________________________________________________________
#
# def find_max_df(column, prevCandles, df, datetime_number):
#     try:
#         # Assume df is sorted by "datetime_number"
#         # Use searchsorted to find the index where datetime_number would be inserted (right side)
#         idx = df["datetime_number"].searchsorted(datetime_number, side="right")
        
#         # Determine the starting index for the last `prevCandles` rows in the filtered subset
#         start_idx = max(0, idx - prevCandles)
        
#         # Slice the DataFrame from start_idx up to idx and compute the max of the specified column
#         return df.iloc[start_idx:idx][column].max()
#     except :
#         pass

def find_max_df(column, prevCandles, df, datetime_number):
    try:
        # Assume df is sorted by "datetime_number"
        # Use searchsorted to find the index where datetime_number would be inserted (right side)
        idx = df["datetime_number"].searchsorted(datetime_number, side="right")
        
        # Determine the starting index for the last `prevCandles` rows in the filtered subset
        start_idx = max(0, idx - prevCandles)
        
        # Slice the DataFrame from start_idx up to idx and compute the max of the specified column
        return df.iloc[start_idx:idx][column].max()
    except :
        pass

def find_min_df(column, prevCandles, df, datetime_number):
    try:
        # Assume df is sorted by "datetime_number"
        # Use searchsorted to find the index where datetime_number would be inserted (right side)
        idx = df["datetime_number"].searchsorted(datetime_number, side="right")
        
        # Determine the starting index for the last `prevCandles` rows in the filtered subset
        start_idx = max(0, idx - prevCandles)
        
        # Slice the DataFrame from start_idx up to idx and compute the max of the specified column
        return df.iloc[start_idx:idx][column].min()
    except :
        pass