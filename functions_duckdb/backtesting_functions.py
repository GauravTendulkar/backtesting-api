
import pandas as pd
from functions import indicators
from functions.thread_safe_LRU_cache import ThreadSafeLRUCache

import numpy as np
from numba import njit
from functions import df_saving, fastCache_saving
from functions import functions
import os
import re

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
    index_or = 0
    index_and = 0
    if option == "or":
        # print(option, temp)
        pass
    for i in temp:
        if "indicator" in i:
           
            indicator_arr, indicator_shortform = indicators.get_indicator_shortform(None, i["indicator"], 0)
           
            
            if if_index_exist(indicator_arr, [0]):
                
                if indicator_arr[0] == "entry":
                    # temp_str += "float(Tracking.loc[Tracking.index[-1], 'entry'])"
                    # temp_str += "float(Tracking.loc[Tracking_index, 'entry'])"
                    temp_str += "float(entry_array[Tracking_index])"

                elif indicator_arr[0] == "time":
                    # temp_str += "float(Tracking.loc[Tracking.index[-1], 'entry'])"
                    # temp_str += "int(df_data[i][time_index]/100)"
                    temp_str += "df_fastCache_colum_arr['time_int'][i]"
                elif indicator_arr[0] == "countPrevTrades":
                    # temp_str += "functions.count_previous_entry_intraday(Tracking, int(df_data[i][date_index]))"
                    temp_str += "functions.count_previous_entry_intraday_1(date_number_array, int(df_data[i][date_index]))"
                elif indicator_arr[0] == "countPrevTradesWeekly":
                    # temp_str += "functions.count_previous_entry_intraday(Tracking, int(df_data[i][date_index]))"
                    temp_str += "functions.count_previous_entry_weekly(date_number_array, int(df_data[i][date_index]))"
                elif indicator_arr[0] == "countPrevTradesMonthly":
                    # temp_str += "functions.count_previous_entry_intraday(Tracking, int(df_data[i][date_index]))"
                    temp_str += "functions.count_previous_entry_monthly(date_number_array, int(df_data[i][date_index]))"

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
                    # print("abs", indicator_arr[1])
                    temp_str += f"functions.abs({entry_to_equation([indicator_arr[1]], None, smallest)} )"
                elif  indicator_arr[0] == "log10":
                    
                    temp_str += f"functions.log10({entry_to_equation([indicator_arr[1]], None, smallest)} )"
                elif  indicator_arr[0] == "log":
                    
                    temp_str += f"functions.log({entry_to_equation([indicator_arr[1]], None, smallest)} )"

                elif  indicator_arr[0] == "max":
                   
                    # print("indicator_arr", indicator_arr)
                    s = entry_to_equation([indicator_arr[2]], None, smallest)
                    trimmed = s[:s.rfind(']') + 1]

                    temp_str += f"df_fastCache_colum_arr[ i-{indicator_arr[1]}+1 :i+1, {trimmed[26:]}.max()"
                elif  indicator_arr[0] == "min":
                   
                    s = entry_to_equation([indicator_arr[2]], None, smallest)
                    trimmed = s[:s.rfind(']') + 1]

                    temp_str += f"df_fastCache_colum_arr[ i-{indicator_arr[1]}+1 :i+1, {trimmed[26:]}.min()"

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
                or indicator_arr[2] == "CPRPP" or indicator_arr[2] == "CPRBC" or indicator_arr[2] == "CPRTC" 
                or indicator_arr[2] == "pivotR1" or indicator_arr[2] == "pivotR2" or indicator_arr[2] == "pivotR3" or indicator_arr[2] == "pivotR4" 
                or indicator_arr[2] == "pivotS1" or indicator_arr[2] == "pivotS2" or indicator_arr[2] == "pivotS3" or indicator_arr[2] == "pivotS4"
                or indicator_arr[2] == "stochasticRSIK"
                or indicator_arr[2] == "stochasticRSID"
                or indicator_arr[2] == "atr"
                or indicator_arr[2] == "momentum"
                or indicator_arr[2] == "roc"
                or indicator_arr[2] == "cci"
                or indicator_arr[2] == "williamsPercentR"
                or indicator_arr[2] == "cmo"
                or indicator_arr[2] == "cmf"
                or indicator_arr[2] == "donchianUpper"
                or indicator_arr[2] == "donchianLower"
                or indicator_arr[2] == "donchianMiddle"
                or indicator_arr[2] == "keltnerBasis"
                or indicator_arr[2] == "keltnerUpper"
                or indicator_arr[2] == "keltnerLower"
                or indicator_arr[2] == "conversionLineIC"
                or indicator_arr[2] == "baseLineIC"
                or indicator_arr[2] == "laggingLineIC"
                or indicator_arr[2] == "leadingSpanAIC"
                or indicator_arr[2] == "leadingSpanBIC"
                or indicator_arr[2] == "datetime_number"):

                    
                    stock = '{stock}'
                    stock = f"{smallest}_{stock}_{indicator_arr[1]}_{indicator_arr[0]}_{indicator_shortform}"
                    modified_string = f'f"{stock}"'
                    # print(stock)
                        
                    temp_str += f"df_fastCache_colum_arr[{modified_string}][i]"
                    
                        
            
            temp_str = temp_str + " "
        
        elif "condition" in i:
            
            # print(option, len(temp))
            if len(temp) == 1:
                temp_str = temp_str + f"( {entry_to_equation(i["condition"], "condition", smallest)} )"
            else:
                # print(option)
                temp_str = temp_str + f"( {entry_to_equation(i["condition"], "condition", smallest)} )" 
                index += 1
                
                if index < len(temp):
                    temp_str = temp_str + " " + option + " "

        elif "AND" in i:
            print(option, len(temp))
            if len(temp) == 1:
                temp_str += f"( {entry_to_equation(i['AND'], 'and', smallest)} )"
            else:
                temp_str = temp_str + f"( {entry_to_equation(i['AND'], 'and', smallest)} )"
                index += 1
                print("index_and", index_and)
                
                if index < len(temp):
                    temp_str = temp_str + " " + option + " "
                    print(temp_str)
        elif "OR" in i:
            print(option, len(temp))
            if len(temp) == 1:
                temp_str += f"( {entry_to_equation(i['OR'], 'or', smallest)} )"
            else:
                
                temp_str = temp_str + f"( {entry_to_equation(i['OR'], 'or', smallest)} )"
                index += 1
                print("index_or", index_or)
                
                
                if index < len(temp):
                    temp_str = temp_str + " " + option + " "
                    # print("option", option)
                    # print(temp_str)
                    

    return temp_str

