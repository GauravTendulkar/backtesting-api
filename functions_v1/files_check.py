
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
import time

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

    print("arr_indicator_generator", arr_indicator_generator)

    temp = []
    for i in range(0, len(arr_indicator_generator)):

        if arr_indicator_generator[i] not in temp:
            temp.append(arr_indicator_generator[i])
    
    # smallest = get_smallest_tf(temp)
    # # print("smallest", smallest)
    # for i in range(0, len(temp)):
    #     temp[i][3] = f"{smallest}_{temp[i][3]}"
    return temp




# def convert_equation_to_(data1, list_stocks):
#     # initial_time = time.perf_counter()
#     """
#     Fast, deduplicated, recursive extractor for all atomic indicator, stock, and shortform combos
#     from a nested equation or logical structure.
#     """

#     arr_indicator_generator = []
#     indicator_set = set()  # For fast deduplication

#     # Set of recognized atomic indicator types for O(1) lookup
#     indicator_types = {
#         "sma", "ema", "rsi", "BBbasis", "BBupper", "BBlower",
#         "close", "high", "low", "open", "volume",
#         "macdLine", "signalLine", "macdHistogram",
#         "supertrend", "H1", "H2", "H3", "H4", "L1", "L2", "L3", "L4",
#         "CPRPP", "CPRBC", "CPRTC",
#         "pivotR1", "pivotR2", "pivotR3", "pivotR4",
#         "pivotS1", "pivotS2", "pivotS3", "pivotS4",
#         "stochasticRSIK", "stochasticRSID",
#         "atr", "momentum", "roc", "cci", "williamsPercentR",
#         "cmo", "cmf", "donchianUpper", "donchianLower", "donchianMiddle",
#         "keltnerBasis", "keltnerUpper", "keltnerLower",
#         "conversionLineIC", "baseLineIC", "laggingLineIC",
#         "leadingSpanAIC", "leadingSpanBIC", "datetime_number"
#     }

#     def deepfreeze(obj):
#         """
#         Recursively converts lists to tuples and dicts to frozensets for hashing.
#         """
#         if isinstance(obj, dict):
#             return frozenset((k, deepfreeze(v)) for k, v in sorted(obj.items()))
#         elif isinstance(obj, (list, tuple)):
#             return tuple(deepfreeze(x) for x in obj)
#         else:
#             return obj

#     def get_indicator_list(item_list):
#         for element in item_list:
#             # Block: atomic indicator
#             if "indicator" in element:
#                 indicator_arr, indicator_shortform = indicators.get_indicator_shortform(None, element["indicator"], 0)

#                 # Atomic indicator case (indicator_arr[2] in allowed list)
#                 if if_index_exist(indicator_arr, [2]) and indicator_arr[2] in indicator_types:
#                     for l in list_stocks:
#                         arr = [
#                             l,  # stock
#                             indicator_arr[1],  # timeframe
#                             indicator_shortform,  # shortform
#                             f"{l}_{indicator_arr[1]}_{indicator_arr[0]}_{indicator_shortform}",  # unique id
#                             indicator_arr      # indicator definition
#                         ]
#                         tup = deepfreeze(arr)
#                         if tup not in indicator_set:
#                             indicator_set.add(tup)
#                             arr_indicator_generator.append(arr)
#                 # Math operators and wrappers (recurse as needed)
#                 elif if_index_exist(indicator_arr, [0]):
#                     key = indicator_arr[0]
#                     # Nested indicator subexpressions for these keys
#                     if key in {"max", "min"}:
#                         get_indicator_list([indicator_arr[2]])
#                         get_indicator_list([{
#                             "indicator": [
#                                 {"value": indicator_arr[2]["indicator"][0]["value"]},
#                                 {"value": indicator_arr[2]["indicator"][1]["value"]},
#                                 {"value": "datetime_number"}
#                             ]
#                         }])
#                     elif key in {"ceil", "floor", "abs", "log10", "log"}:
#                         get_indicator_list([indicator_arr[1]])
#                 # Fall-through: not a handled indicator type or form

#             # Logic blocks: recursively process contents
#             elif "condition" in element:
#                 get_indicator_list(element["condition"])
#             elif "AND" in element:
#                 get_indicator_list(element["AND"])
#             elif "OR" in element:
#                 get_indicator_list(element["OR"])
#             # else: not recognized, skip

#     get_indicator_list(data1)
#     # print("array_to_equation")
#     # elapsed_time = time.perf_counter() - initial_time
#     # print(elapsed_time)
#     # print(f"Elapsed time: {elapsed_time * 1_000:.2f} ms")   # Microseconds
#     # print(f"Elapsed time: {elapsed_time * 1_000_000:.2f} µs")   # Microseconds
#     # print(f"Elapsed time: {elapsed_time * 1_000_000_000:.2f} ns")  # Nanoseconds
#     return arr_indicator_generator


