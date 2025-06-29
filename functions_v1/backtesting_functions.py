import pandas as pd
from functions import indicators
from functions.thread_safe_LRU_cache import ThreadSafeLRUCache

import numpy as np
from numba import njit
from functions import df_saving, fastCache_saving
from functions import functions
import os
import re


def date_str_to_int(datepass: str):
    temp = datepass.split("-")
    
    return int(f"{temp[0]}{temp[1]}{temp[2]}")

def if_index_exist(arr_list, arr_number):
    
    try:
        for i in range(0, len(arr_number)):
            # print(arr_number[i])
            if arr_list[arr_number[i]]:
                pass
        return True
    except:
            return False

def entry_to_equation(temp, option, smallest):
    temp_str = ""
    index = 0
    for i in temp:
        if "indicator" in i:
           
            indicator_arr, indicator_shortform = indicators.get_indicator_shortform(None, i["indicator"], 0)
           
            
            if if_index_exist(indicator_arr, [0]):
                
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
                    
                    temp_str += f"functions.ceil({entry_to_equation([indicator_arr[1]], None, smallest)} )"
                elif  indicator_arr[0] == "floor":
                    
                    temp_str += f"functions.floor({entry_to_equation([indicator_arr[1]], None, smallest)} )"
                elif  indicator_arr[0] == "abs":
                    
                    temp_str += f"functions.abs({entry_to_equation([indicator_arr[1]], None, smallest)} )"
                elif  indicator_arr[0] == "log10":
                    
                    temp_str += f"functions.log10({entry_to_equation([indicator_arr[1]], None, smallest)} )"
                elif  indicator_arr[0] == "log":
                    
                    temp_str += f"functions.log({entry_to_equation([indicator_arr[1]], None, smallest)} )"

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

                    
                    # a = f"{indicator_arr[1]}"
                    # string_s = f"list_stocks[t]_{indicator_shortform}_{a}_smallest_df_time_{indicator_arr[0]}"
                    # modified_string = re.sub(r'list_stocks\[t\]', r'{list_stocks[t]}', string_s)
                    # modified_string = re.sub(r'smallest', r'{smallest}', modified_string)
                    # modified_string = re.sub(r'df_time', r'{df_time}', modified_string)
                    # modified_string = 'f"' + modified_string + '"' 
                    
                    # print("********************************")
                    # print(indicator_arr)
                    # print(indicator_shortform)
                    stock = '{stock}'
                    stock = f"{smallest}_{stock}_{indicator_arr[1]}_{indicator_arr[0]}_{indicator_shortform}"
                    modified_string = f'f"{stock}"'
                    # print(stock)
                        
                    temp_str += f"df_fastCache_colum_arr[i][fastCache_colum_name.index({modified_string})]"
                    
                        
            
            temp_str = temp_str + " "
        elif "condition" in i:
            if len(temp) == 1:
                temp_str = temp_str + f"( {entry_to_equation(i["condition"], "condition", smallest)} )"
            else:
                # print(option)
                temp_str = temp_str + f"( {entry_to_equation(i["condition"], "condition", smallest)} )" 
                index += 1
                if index < len(temp):
                    temp_str = temp_str + " " + option + " "

        elif "AND" in i:
            
            temp_str += f"( {entry_to_equation(i['AND'], 'and', smallest)} )"
        elif "OR" in i:
            temp_str += f"( {entry_to_equation(i['OR'], 'or', smallest)} )"
    return temp_str