import pandas as pd
from ..backtesting_duckdb import indicators

import numpy as np
from numba import njit

import os
import re


SIMPLE_FUNCTION = ["ceil", "floor", "abs", "log", 'log10']
WINDOW_FUNCTION = ["min", "max"]
OPERATORS = ["+", "-", "*", "/"]

def date_str_to_int(datepass: str):
    temp = datepass.split("-")
    
    return int(f"{temp[0]}{temp[1]}{temp[2]}")





class BackTestingFunction:

    def __init__(self, stock_list = []):
        self.stock_list = stock_list
        self.tags = {}


        self.uniqueid = 0
        self.collect_depth_zero_uniqueid = {}
        self.collect_all_cte_tables = {}

    @staticmethod
    def if_index_exist(arr_list, arr_number):
    
        try:
            for i in range(0, len(arr_number)):
                # print(arr_number[i])
                if arr_list[arr_number[i]]:
                    pass
            return True
        except:
                return False
        
    @staticmethod
    def indicator_column_check(indicator_arr):

        if (indicator_arr[2] == "sma" 
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
            return True
        else:
            return False
    #  my old code
    def condition_arr_to_equation(self, data, pretext):
        text = ""
        stack = 0
        start_index = 0
        end_index = 0
        for index, item in enumerate(data):
            if stack == 0:
                start_index = index
            if item in WINDOW_FUNCTION or item in SIMPLE_FUNCTION  :
                stack += 1
            if item == "(":
                
                if stack > 0:
                    stack += 1
                else:
                    text = text + f"{item} "

            elif item == ")":
                
                if stack == 1:
                    end_index = index
                    # text = text + f"{item}"
                    # print(start_index, end_index)
                    text = text + f'df["{pretext}_{start_index}_{end_index}"][i] '
                if stack == 0:
                    text = text + f" {item} "
                if stack > 0:
                    stack -= 1
            else:
                if stack == 0:
                    text = text + f"{item} "
        return text
    
    # chatgpt code
    
    
    def entry_to_equation(self, temp, option, smallest, depth="", tags= "entry"): 
        temp_str = ""
        index = 0
        index_or = 0
        index_and = 0

        return_indicator = ""
        connect_special_function = []
        for i, item in enumerate(temp):
            if "indicator" in item:
                return_indicator = "indicator"
            
                indicator_arr, indicator_shortform = indicators.get_indicator_shortform(None, item["indicator"], 0)
                # print(indicator_arr, indicator_shortform)
                
                if BackTestingFunction.if_index_exist(indicator_arr, [0]):
                    
                    if indicator_arr[0] == "prevEntry":
                        # temp_str += "float(Tracking.loc[Tracking.index[-1], 'entry'])"
                        # temp_str += "float(Tracking.loc[Tracking_index, 'entry'])"
                        # temp_str += "float(entry_array[Tracking_index])"
                        text = "sl_db.open_entry_price(df['symbol'][i])"
                        connect_special_function.append(text)
                    elif indicator_arr[0] == "first_entry":
                        connect_special_function.append("""sl_db.first_entry()""")
                    elif indicator_arr[0] == "time":
                        # temp_str += "float(Tracking.loc[Tracking.index[-1], 'entry'])"
                        # temp_str += "int(df_data[i][time_index]/100)"
                        # temp_str += "df['time_int'][i]"
                        connect_special_function.append("df['time_int'][i]")
                    
                    elif indicator_arr[0] == "countPrevTrades":
                        # date_text = "f'{date_str[0:10]} {date_str[11:19]}'"
                        date_text = "f'{date_str[0:10]}'"
                        text = f"""sl_db.previous_position(df['symbol'][i], mode = 'count', date = {date_text})"""
                        connect_special_function.append(text)
                        
                    elif indicator_arr[0] == "countPrevTradesWeekly":
                        # temp_str += "functions.count_previous_entry_intraday(Tracking, int(df_data[i][date_index]))"
                        temp_str += "functions.count_previous_entry_weekly(date_number_array, int(df_data[i][date_index]))"
                    elif indicator_arr[0] == "countPrevTradesMonthly":
                        # temp_str += "functions.count_previous_entry_intraday(Tracking, int(df_data[i][date_index]))"
                        temp_str += "functions.count_previous_entry_monthly(date_number_array, int(df_data[i][date_index]))"

                    elif indicator_arr[0] == "open_position_quantity":
                        connect_special_function.append("""sl_db.open_position_quantity(df['symbol'][i])""")

                    elif indicator_arr[0] == "open_position_value":
                        connect_special_function.append("""sl_db.open_position_value(df['symbol'][i])""")
                    elif indicator_arr[0] == "open_position_avg_price":
                        connect_special_function.append("""sl_db.open_position_avg_price(df['symbol'][i])""")
                    elif indicator_arr[0] == "open_entry_count":
                        connect_special_function.append(f"""sl_db.open_entry_count(df['symbol'][i], label="{indicator_arr[2]}", entryexit="{indicator_arr[1]}")""")
                    elif indicator_arr[0] == "open_trade":
                        # .work on this tomorrow
                        # open_trade(self, mode, stock, label="", entryexit="entry")
                        text = f"""sl_db.open_trade(  stock = df['symbol'][i], mode = "{indicator_arr[1]}", label = "{indicator_arr[3]}", entryexit = "{indicator_arr[2]}")"""
                        # print("******************************************************", text)
                        connect_special_function.append(text)
                        # pass
                    elif indicator_arr[0] == "add_datetime":
                                            
                        # text = f"""sl_db.add_datetime(  stock = df['symbol'][i], mode = "{indicator_arr[1]}", label = "{indicator_arr[3]}", entryexit = "{indicator_arr[2]}")"""
                        text = f"""sl_db.add_datetime(  stock = df['symbol'][i], option = "{indicator_arr[1]}", mode = "{indicator_arr[2]}", label = "{indicator_arr[3]}", days = {indicator_arr[4]}, hours = {indicator_arr[5]}, minutes = {indicator_arr[6]}) """
                        print("add_datetime", text)
                        connect_special_function.append(text)
                    elif indicator_arr[0] == "datetime":
                        text = f"""sl_db.datetime(  date_int = df["date_int"][i], time_int = df["time_int"][i]) """
                        connect_special_function.append(text)

                    elif indicator_arr[0] == "percentage_quantity":
                        connect_special_function.append(f"""sl_db.exit_percentage_to_quantity({indicator_arr[1]} ,df['symbol'][i])""")
                    
                    elif indicator_arr[0] == "number":
                        connect_special_function.append(indicator_arr[1])
                        
                        # temp_str += f"{indicator_arr[1]}"
                    elif indicator_arr[0] == "+" or indicator_arr[0] == "-" or indicator_arr[0] == "/" or indicator_arr[0] == "*" :
                        connect_special_function.append(indicator_arr[0])
                        # temp_str += f"{indicator_arr[0]}"
                    elif indicator_arr[0] == "(" or indicator_arr[0] == ")" :
                        connect_special_function.append(indicator_arr[0])
                        # temp_str += f"{indicator_arr[0]}"
                    elif indicator_arr[0] == "<" or indicator_arr[0] == "<=" or indicator_arr[0] == ">" or indicator_arr[0] == ">=" or indicator_arr[0] == "==" or indicator_arr[0] == "!=":
                        # temp_str += f"{indicator_shortform}"
                        connect_special_function.append(indicator_shortform)
                    
                    elif  indicator_arr[0] == "ceil":
                        connect_special_function.append(indicator_arr[0])
                        # temp_str += f"functions.ceil({entry_to_equation([indicator_arr[1]], None, smallest)} )"
                    elif  indicator_arr[0] == "floor":
                        connect_special_function.append(indicator_arr[0])
                        # temp_str += f"functions.floor({entry_to_equation([indicator_arr[1]], None, smallest)} )"
                    elif  indicator_arr[0] == "abs":
                        # print("abs", indicator_arr[1])
                        connect_special_function.append(indicator_arr[0])
                        # temp_str += f"functions.abs({entry_to_equation([indicator_arr[1]], None, smallest)} )"
                    elif  indicator_arr[0] == "log10":
                        connect_special_function.append(indicator_arr[0])
                        # temp_str += f"functions.log10({entry_to_equation([indicator_arr[1]], None, smallest)} )"
                    elif  indicator_arr[0] == "log":
                        connect_special_function.append(indicator_arr[0])
                    #     temp_str += f"functions.log({entry_to_equation([indicator_arr[1]], None, smallest)} )"

                    elif  indicator_arr[0] == "max":
                        connect_special_function.append(indicator_arr[0])
                        
                    elif  indicator_arr[0] == "min":
                        connect_special_function.append(indicator_arr[0])
                        
                if BackTestingFunction.if_index_exist(indicator_arr, [1]):
                    if indicator_arr[1] == "number_of_trades":
                        date_text = "f'{date_str[0:10]}'"
                        # text = f"""sl_db.previous_position(df['symbol'][i], mode = 'count', date = {date_text})"""
                        
                        text = f"""sl_db.number_of_trades(  stock = df['symbol'][i], mode = "{indicator_arr[2]}", date = {date_text}, label = "{indicator_arr[4]}", entryexit = "{indicator_arr[3]}", tf = "{indicator_arr[0]}")"""
                        connect_special_function.append(text)

                if BackTestingFunction.if_index_exist(indicator_arr, [2]):
                    if BackTestingFunction.indicator_column_check(indicator_arr):

                        
                        # stock = f'{stock}'
                        # stock = f"{smallest}_{stock}_{indicator_arr[1]}_{indicator_arr[0]}_{indicator_shortform}"

                        stock = f"{smallest}_{indicator_arr[1]}_{indicator_arr[0]}_{indicator_shortform}"
                        # modified_string = f'f"{stock}"'
                        # print(stock)
                            
                        # temp_str += f'df["{stock}"][i]'
                        connect_special_function.append(f'df["{stock}"][i]')
                            
                
                # temp_str = temp_str + " "
            
            elif "condition" in item:
                # print( f"{tags}_{depth}{i}C")
                condition_arr = self.entry_to_equation(item["condition"], "condition", smallest, depth+f"{i}C", tags)
                # print(condition_arr)

                output_text = self.condition_arr_to_equation(condition_arr, f"{tags}_{depth}{i}C")
                # print(output_text)
                # temp_str = temp_str + " " + output_text + " "

                # print(option, len(temp))
                if len(temp) == 1:
                    # temp_str = temp_str + f"( {self.entry_to_equation(item["condition"], "condition", smallest, depth+f"{i}C", tags)}, )"
                    # temp_str = temp_str + f"( {output_text}, )"
                    temp_str = temp_str + f"( {output_text} )"

                    # print(temp_str)
                else:
                    # print(option)
                    # temp_str = temp_str + f"( {self.entry_to_equation(item["condition"], "condition", smallest, depth+f"{i}C", tags)} )" 
                    temp_str = temp_str + f"( {output_text} )" 
                    # print(temp_str)
                    index += 1
                    
                    if index < len(temp):
                        temp_str = temp_str + " " + option + " "
                # print(temp_str)

            elif "AND" in item:
                # print(option, len(temp))
                if len(temp) == 1:
                    temp_str += f"( {self.entry_to_equation(item['AND'], 'and', smallest, depth+f"{i}A", tags)} )"
                    # print(temp_str)
                else:
                    temp_str = temp_str + f"( {self.entry_to_equation(item['AND'], 'and', smallest, depth+f"{i}A", tags)} )"
                    # print(temp_str)
                    index += 1
                    # print("index_and", index_and)
                    
                    if index < len(temp):
                        temp_str = temp_str + " " + option + " "
                
            elif "OR" in item:
                # print(option, len(temp))
                if len(temp) == 1:
                    temp_str += f"( {self.entry_to_equation(item['OR'], 'or', smallest, depth+f"{i}O", tags)} )"
                else:
                    
                    temp_str = temp_str + f"( {self.entry_to_equation(item['OR'], 'or', smallest, depth+f"{i}O", tags)} )"
                    index += 1
                    # print("index_or", index_or)
                    
                    
                    if index < len(temp):
                        temp_str = temp_str + " " + option + " "
                        # print("option", option)
                        # print(temp_str)
        if return_indicator == "indicator" :
            # 
            return connect_special_function               

        return temp_str



    def convert_req_data_to_list(self, data1, tag): 
        # print(data1)
        arr_indicator_generator = []


        def get_indicator_list(data1):

            for i in data1:
                if "indicator" in i:
                    # print("___________________")
                    indicator_arr, indicator_shortform = indicators.get_indicator_shortform(None, i["indicator"], 0)
                    # print("get_list_for_generator", indicator_arr, indicator_shortform)
                    if (BackTestingFunction.if_index_exist(indicator_arr, [2]) 
                    and BackTestingFunction.indicator_column_check(indicator_arr)):
                            for l in self.stock_list:
                                arr = []
                                arr.append(l)
                                arr.append(indicator_arr[1])
                                arr.append(indicator_shortform)
                                arr.append(f"{l}_{indicator_arr[1]}_{indicator_arr[0]}_{indicator_shortform}")
                                arr.append(indicator_arr)
                                # if indicator_arr[2] != "datetime_number":
                                    
                                arr_indicator_generator.append(arr)
                                
                    elif BackTestingFunction.if_index_exist(indicator_arr, [0]):  
                        
                        if  indicator_arr[0] == "max": 
                            # print(indicator_arr)
                            # print("[indicator_arr[2]]", [indicator_arr[2]])
                            # get_indicator_list([indicator_arr[2]])
                            pass
                            # get_indicator_list([{'indicator': [{'value': indicator_arr[2]["indicator"][0]["value"]}, {'value': indicator_arr[2]["indicator"][1]["value"]}, {'value': 'datetime_number'}]}])
                        elif  indicator_arr[0] == "min": 
                            # print("[indicator_arr[2]]", [indicator_arr[2]])
                            # get_indicator_list([indicator_arr[2]])
                            pass
                            # get_indicator_list([{'indicator': [{'value': indicator_arr[2]["indicator"][0]["value"]}, {'value': indicator_arr[2]["indicator"][1]["value"]}, {'value': 'datetime_number'}]}])

                        # elif  indicator_arr[0] == "ceil":
                            # get_indicator_list([indicator_arr[1]])
                        # elif  indicator_arr[0] == "floor":
                        #     get_indicator_list([indicator_arr[1]])
                        # elif  indicator_arr[0] == "abs":
                        #     get_indicator_list([indicator_arr[1]])
                        # elif  indicator_arr[0] == "log10":
                        #     get_indicator_list([indicator_arr[1]])
                        # elif  indicator_arr[0] == "log":
                        #     get_indicator_list([indicator_arr[1]])
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

        # print("arr_indicator_generator", arr_indicator_generator)

        temp = []
        for i in range(0, len(arr_indicator_generator)):

            if arr_indicator_generator[i] not in temp:
                temp.append(arr_indicator_generator[i])
        
        # smallest = get_smallest_tf(temp)
        # # print("smallest", smallest)
        # for i in range(0, len(temp)):
        #     temp[i][3] = f"{smallest}_{temp[i][3]}"
        self.tags[tag] = temp
        return temp

# find_special_functions helper
    def generater_unique_id(self):
        self.uniqueid += 1 
        return self.uniqueid
    
    def join_columns(self, joining_id_arr):
        final_text = f""" 
"""
        if len(joining_id_arr) > 0:
            for index, item in enumerate(joining_id_arr):
                text = f"LEFT JOIN id_{item} ON id_{item}.datetime = s.datetime \n"
                final_text = final_text + text
            final_text = str(final_text)
            return final_text
        else:
            return ""
        
    def generate_cte(self, equation, unique_id, joining_id_arr , length = 1, function_value= "" ):
        if function_value in WINDOW_FUNCTION:
            text = f""" 
id_{unique_id} AS (
    SELECT s.datetime,
        {function_value}({equation}) OVER ( ORDER BY s.datetime ROWS BETWEEN {length} PRECEDING AND CURRENT ROW ) 
        as rolling_max_{unique_id}
    from "stock_timeframe" s         
{self.join_columns(joining_id_arr)}
)"""
            return text
        elif function_value in SIMPLE_FUNCTION:
            text = f""" 
id_{unique_id} AS (
    SELECT s.datetime,
        {function_value}({equation})
        as rolling_max_{unique_id}
    from "stock_timeframe" s         
{self.join_columns(joining_id_arr)}
)"""
            return text
        

    def maxmin_str(self, arr, depth, unique_key):
        unique_id = 0
        length_max_min = 0
        start_flag = 0
        start_flag_value = ""
        final_text = ''
        stack = 0
        index=0
        joining_id_arr = []
        start_index = 0
        end_index = 0
        time_frame = 0
        
        
        while(index < len(arr)):
            item = arr[index]
            if isinstance(item , list) and item[0] in WINDOW_FUNCTION:
                if start_flag == 0:
                    start_flag_value = item[0]
                    length_max_min = item[1]
                    if depth == 0:
                        start_index = index
                start_flag += 1
                if start_flag > 1:
                    skip_index, joining_id  = self.maxmin_str(arr[index:], depth+1, unique_key)
                    joining_id_arr.append(joining_id)
                    
                    index += skip_index
                    final_text = final_text +  f"id_{joining_id}.rolling_max_{joining_id}"
                    start_flag -= 1
                
                    # print("skip_index",index, skip_index)

            elif isinstance(item , str) and item in SIMPLE_FUNCTION:
                if start_flag == 0 and depth == 0:
                    start_flag_value = item
                    start_index = index
                start_flag += 1
                if depth > 0:
                    final_text = final_text +  f'{item}( ' 
                # elif depth == 0:
                #     print("item",item , "start_flag_value", start_flag_value, "depth", depth, "start_flag", start_flag,"isinstance(item , str)", isinstance(item , str) )
                    # if start_flag > 1:
                        


            elif isinstance(item , list) and (isinstance(item[0] , int) or isinstance(item[0] , float) or isinstance(item[0] , str) ) and start_flag > 0:
                # add candle columns
                final_text = final_text +  f'"{item[1]}" ' 
                time_frame = item[0]

            elif isinstance(item , str) and item in OPERATORS and start_flag > 0:
                final_text = final_text +  f'{item} ' 

            elif isinstance(item , int) or isinstance(item , float):
                # number type
                final_text = final_text +  f'{item} ' 

            elif item == "(":
                if start_flag >0:
                    start_flag += 1
                    if depth >0:
                        final_text = final_text +  f' ('

            elif item == ")":
                # print("item",item , "start_flag_value", start_flag_value, "depth", depth, "start_flag", start_flag,"isinstance(item , str)", isinstance(item , str) )

                start_flag -= 1
                # print(item)
                if depth >0:
                    # if start_flag_value in WINDOW_FUNCTION:
                    #     pass
                    # else:
                    if start_flag > 0:
                        # pass
                        final_text = final_text +  f' )' 
                    # if start_flag == 0:
                    #     pass
                    #     end_index =  index 
                    #     break
                if start_flag == 0 and start_flag_value in WINDOW_FUNCTION:
                    # print("item",item , "start_flag_value", start_flag_value,"depth", depth, "start_flag", start_flag,"isinstance(item , str)", isinstance(item , str) )
                    unique_id = self.generater_unique_id()
                    text = self.generate_cte(final_text, unique_id, joining_id_arr , length_max_min ,start_flag_value  )
                    if time_frame not in self.collect_all_cte_tables:
                        self.collect_all_cte_tables[time_frame] = []
                    self.collect_all_cte_tables[time_frame].append(text)
                    # print(text)
                    if depth == 0:
                        end_index = index
                        if time_frame not in self.collect_depth_zero_uniqueid:
                            self.collect_depth_zero_uniqueid[time_frame] = []
                        self.collect_depth_zero_uniqueid[time_frame].append({ f"{unique_key}_{start_index}_{end_index}" : unique_id})
                    final_text = ''
                elif start_flag == 0 and start_flag_value in SIMPLE_FUNCTION:
                    unique_id = self.generater_unique_id()
                    text = self.generate_cte(final_text, unique_id, joining_id_arr , length_max_min, start_flag_value )
                    # print(text)
                    if time_frame not in self.collect_all_cte_tables:
                        self.collect_all_cte_tables[time_frame] = []
                    self.collect_all_cte_tables[time_frame].append(text)
                    if depth == 0:
                        end_index = index
                        if time_frame not in self.collect_depth_zero_uniqueid:
                            self.collect_depth_zero_uniqueid[time_frame] = []
                        self.collect_depth_zero_uniqueid[time_frame].append({ f"{unique_key}_{start_index}_{end_index}" : unique_id})
                    final_text = ''
                if depth >0 and start_flag == 0: 
                    stack =  index 
                    break
            # print(start_flag, item)
            index+= 1

        
        
#         
        # print(final_text)
        # print(text)
        # print("end_index", end_index)
        return stack, unique_id



# max, min, ceil, floor, 
    def find_special_functions(self, data1, tag): 
        # print(data1)
        arr_indicator_generator = []
        

        def get_indicator_list(data1, depth):
            connect_special_function = []
            sp_flag_maxmin = 0
            for i, item in enumerate(data1):
                if "indicator" in item:
                    # print("___________________")
                    indicator_arr, indicator_shortform = indicators.get_indicator_shortform(None, item["indicator"], 0)
                    # print("get_list_for_generator", indicator_arr, indicator_shortform)
                    if (BackTestingFunction.if_index_exist(indicator_arr, [2]) 
                    and BackTestingFunction.indicator_column_check(indicator_arr)):
                            
                            if indicator_arr[0] == 0 or indicator_arr[0] == "0":
                                connect_special_function.append([indicator_arr[1], f"{indicator_shortform}"])
                            else:
                                connect_special_function.append([indicator_arr[1], f"{indicator_arr[1]}_{indicator_arr[0]}_{indicator_shortform}"])
                            
                                
                    elif BackTestingFunction.if_index_exist(indicator_arr, [0]):  
                        
                        if  indicator_arr[0] == "max": 
                            connect_special_function.append(indicator_arr)
                            sp_flag_maxmin += 1
                            
                        elif  indicator_arr[0] == "min": 
                            connect_special_function.append(indicator_arr)
                            sp_flag_maxmin += 1
                            
                        elif  indicator_arr[0] == "ceil":
                            connect_special_function.append(indicator_arr[0])
                            sp_flag_maxmin += 1
                            
                        elif  indicator_arr[0] == "floor":
                            connect_special_function.append(indicator_arr[0])
                            sp_flag_maxmin += 1
                            
                        elif  indicator_arr[0] == "abs":
                            connect_special_function.append(indicator_arr[0])
                            sp_flag_maxmin += 1
                            
                        elif  indicator_arr[0] == "log10":
                            connect_special_function.append(indicator_arr[0])
                            sp_flag_maxmin += 1
                            
                        elif  indicator_arr[0] == "log":
                            connect_special_function.append(indicator_arr[0])
                            sp_flag_maxmin += 1
                            
                        elif indicator_arr[0] == "number":
                            connect_special_function.append(indicator_arr[1])
                            
                        elif indicator_arr[0] == "+" or indicator_arr[0] == "-" or indicator_arr[0] == "/" or indicator_arr[0] == "*" :
                            connect_special_function.append(indicator_arr[0])
                            
                        elif indicator_arr[0] == "(" or indicator_arr[0] == ")" :
                            connect_special_function.append(indicator_arr[0])
                        elif indicator_arr[0] == "<" or indicator_arr[0] == "<=" or indicator_arr[0] == ">" or indicator_arr[0] == ">=" or indicator_arr[0] == "==" or indicator_arr[0] == "!=":
                            connect_special_function.append(indicator_arr[0])
                            
                    else:
                
                        pass
                        
                    

                elif "condition" in item:
                    
                    result, flag = get_indicator_list(item["condition"], depth+f"{i}C")
                    
                    if flag > 0:
                        # print("result", result)
                        # print(depth+f"{i}C")
                        self.maxmin_str( result, 0, depth+f"{i}C")
                elif "AND" in item:
                    
                    get_indicator_list(item["AND"], depth+f"{i}A")

                elif "OR" in item:
                    
                    get_indicator_list(item["OR"], depth+f"{i}O")


            return connect_special_function ,sp_flag_maxmin
        get_indicator_list(data1, f"{tag}_")

        

        temp = []
        for i in range(0, len(arr_indicator_generator)):

            if arr_indicator_generator[i] not in temp:
                temp.append(arr_indicator_generator[i])
        
        # smallest = get_smallest_tf(temp)
        # # print("smallest", smallest)
        # for i in range(0, len(temp)):
        #     temp[i][3] = f"{smallest}_{temp[i][3]}"
        # self.tags[tag] = temp
        return temp
    





