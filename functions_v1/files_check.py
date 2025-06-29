
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

def if_index_exist(arr_list, arr_number):
    
    try:
        for i in range(0, len(arr_number)):
            # print(arr_number[i])
            if arr_list[arr_number[i]]:
                pass
        return True
    except:
            return False
    
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


def convert_equation_to_(data1, list_stocks):
    # print(data1)
    arr_indicator_generator = []


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
                            arr.append(f"{l}_{indicator_arr[1]}_{indicator_arr[0]}_{indicator_shortform}")
                            arr.append(indicator_arr)
                            # if indicator_arr[2] != "datetime_number":
                                
                            arr_indicator_generator.append(arr)
                            
            
                else:
            
                    pass
                    
                

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
    
    # smallest = get_smallest_tf(temp)
    # # print("smallest", smallest)
    # for i in range(0, len(temp)):
    #     temp[i][3] = f"{smallest}_{temp[i][3]}"
    return temp




