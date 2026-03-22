
from functions import indicators


# using database_duckdb/stocks.duckdb

TIMEFRAME_CONVERSION = {
        1 : '1min',
        2: '2min',
        3: '3min',
        5: '5min',
        10: '10min',
        15: '15min',
        30: '30min',
        60: '1h',
        120: '2h',
        180: '3h',
        240: '4h',
        "Daily": "Daily",
        "Weekly": "Weekly",
        "Monthly": "Monthly",
        "Yearly": "Yearly",

    }

TIMEFRAME_CONVERSION_REVERSED = {
    '1min': 1,
    '2min': 2,
    '3min': 3,
    '5min': 5,
    '10min': 10,
    '15min': 15,
    '30min': 30,
    '1h': 60,
    '2h': 120,
    '3h': 180,
    '4h': 240,
    "Daily": "Daily",
    "Weekly": "Weekly",
    "Monthly": "Monthly",
    "Yearly": "Yearly",
}


def if_index_exist(arr_list, arr_number):
    
    try:
        for i in range(0, len(arr_number)):
            # print(arr_number[i])
            if arr_list[arr_number[i]]:
                pass
        return True
    except:
            return False


def convert_req_data_to_list(data1, list_stocks): 
    # print(data1)
    arr_indicator_generator = []


    def get_indicator_list(data1):

        for i in data1:
            if "indicator" in i:
                # print("___________________")
                indicator_arr, indicator_shortform = indicators.get_indicator_shortform(None, i["indicator"], 0)
                # print("get_list_for_generator", indicator_arr, indicator_shortform)
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
                        # get_indicator_list([{'indicator': [{'value': indicator_arr[2]["indicator"][0]["value"]}, {'value': indicator_arr[2]["indicator"][1]["value"]}, {'value': 'datetime_number'}]}])
                    elif  indicator_arr[0] == "min": 
                        # print("[indicator_arr[2]]", [indicator_arr[2]])
                        get_indicator_list([indicator_arr[2]])
                        # get_indicator_list([{'indicator': [{'value': indicator_arr[2]["indicator"][0]["value"]}, {'value': indicator_arr[2]["indicator"][1]["value"]}, {'value': 'datetime_number'}]}])

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

    # print("arr_indicator_generator", arr_indicator_generator)

    temp = []
    for i in range(0, len(arr_indicator_generator)):

        if arr_indicator_generator[i] not in temp:
            temp.append(arr_indicator_generator[i])
    
    # smallest = get_smallest_tf(temp)
    # # print("smallest", smallest)
    # for i in range(0, len(temp)):
    #     temp[i][3] = f"{smallest}_{temp[i][3]}"
    return temp

def find_smallest_time_frame(a, b):
    if type(a) == int and type(b) == int :
        if a <= b:
            return a
        else:
            return b
    elif type(a) == str and type(b) == int:
        return b
    elif type(b) == str and type(a) == int:
        return a
    elif type(a) == str and type(b) == str:
        if a == "Daily" or b == "Daily" :
            return "Daily"
        elif a == "Weekly" or b == "Weekly":
            return "Weekly"
        elif a == "Monthly" or b == "Monthly":
            return "Monthly"
        elif a == "Yearly" or b == "Yearly":
            return "Yearly"            




class BacktestingTable:

    def __init__(self, stock_list = []):

        self.stock_list = stock_list
        self.raw_data_list = []
        self.unique_time_frame = []
        self.unique_column_for_each_time_frame = {}

        self.smallest_tf = "Yearly"

        self.raw_data_group_by_stock = {}

        self.unique_stock = []

        self.unique_candles_for_each_time_frame = {}

        self.collect_depth_zero_uniqueid = {}
        self.collect_all_cte_tables = {}

       

    def accumulate_request_data(self, req_data):
        # temp = convert_req_data_to_list(req_data, self.stock_list)
        temp = req_data
        
        for i in range(0, len(temp)):
            
            stock = temp[i][0]
            time_frame = temp[i][1]
            indicator_column = temp[i][2]
            candle = temp[i][4][0]
            fast_cache_column = f"{time_frame}_{candle}_{indicator_column}"

            if time_frame not in self.unique_candles_for_each_time_frame:
                self.unique_candles_for_each_time_frame[time_frame] = {}
            if fast_cache_column not in  self.unique_candles_for_each_time_frame[time_frame]:
                if candle == "0" or candle == "0":
                    self.unique_candles_for_each_time_frame[time_frame][fast_cache_column] = indicator_column
                else:
                    self.unique_candles_for_each_time_frame[time_frame][fast_cache_column] = fast_cache_column

            if stock not in self.unique_stock:
                self.unique_stock.append(stock)

            if stock not in self.raw_data_group_by_stock:
                self.raw_data_group_by_stock[stock] = []
            if temp[i] not in self.raw_data_group_by_stock[stock]:
                self.raw_data_group_by_stock[stock].append(temp[i])

            self.smallest_tf = find_smallest_time_frame(self.smallest_tf, time_frame)

            if f"{time_frame}" not in self.unique_column_for_each_time_frame :
                self.unique_column_for_each_time_frame[f"{time_frame}"] = []
            if indicator_column not in self.unique_column_for_each_time_frame[f"{time_frame}"]:
                self.unique_column_for_each_time_frame[f"{time_frame}"].append(indicator_column)

            if time_frame not in self.unique_time_frame:
                self.unique_time_frame.append(time_frame)
            if temp[i] not in self.raw_data_list:
                self.raw_data_list.append(temp[i])


    # 
    def joining_condition(self, smallest, tf, column_name):
        column_name = f'"{column_name}"'
        if tf == "Daily" or tf == "Weekly" or tf == "Monthly":
            if type(smallest) == int:
                if tf == "Daily":
                    return f"""LEFT JOIN {column_name} ON date_trunc('day', OHLC.DATETIME) =  date_trunc('day', {column_name}.DATETIME) """
                elif tf == "Weekly":
                    return f""" LEFT JOIN {column_name} ON (OHLC.DATETIME >= date_trunc('week',{column_name}.DATETIME)  AND OHLC.DATETIME < date_trunc('week',{column_name}.DATETIME ) + INTERVAL 1 WEEK)"""
                elif tf == "Monthly":
                    return f""" LEFT JOIN {column_name} ON (OHLC.DATETIME >= date_trunc('month',{column_name}.DATETIME)  AND OHLC.DATETIME < date_trunc('month',{column_name}.DATETIME ) + INTERVAL 1 MONTH)"""
            else:
                if smallest == "Daily" and (tf == "Weekly" or tf == "Monthly"):
                    if tf == "Weekly":
                        return f""" LEFT JOIN {column_name} ON (OHLC.DATETIME >= date_trunc('week',{column_name}.DATETIME)  AND OHLC.DATETIME < date_trunc('week',{column_name}.DATETIME ) + INTERVAL 1 WEEK)"""
                    elif tf == "Monthly":
                        return f""" LEFT JOIN {column_name} ON (OHLC.DATETIME >= date_trunc('month',{column_name}.DATETIME)  AND OHLC.DATETIME < date_trunc('month',{column_name}.DATETIME ) + INTERVAL 1 MONTH)"""
                
                elif smallest == "Weekly" and tf == "Monthly":
                    
                    return f""" LEFT JOIN {column_name} ON (OHLC.DATETIME >= date_trunc('month',{column_name}.DATETIME)  AND OHLC.DATETIME < date_trunc('month',{column_name}.DATETIME ) + INTERVAL 1 MONTH)"""
                

        if smallest == tf :
            
            return f"""LEFT JOIN {column_name} ON OHLC.DATETIME = {column_name}.DATETIME"""
        elif smallest <= tf :
            return f""" LEFT JOIN {column_name} ON (OHLC.DATETIME >= {column_name}.DATETIME  AND OHLC.DATETIME < {column_name}.DATETIME_END ) """


    def get_all_tf_joining_string_query_list(self):
        final_text="""

"""
        for _, tf in enumerate(self.unique_candles_for_each_time_frame):
            text = self.joining_condition(self.smallest_tf, tf, TIMEFRAME_CONVERSION[tf])
            final_text = final_text + text
            final_text = final_text + "\n"
            final_text = str(final_text)

        return final_text

    def get_all_candle_string_query_list(self):
        final_text="""

"""
        for index, tf in enumerate(self.unique_candles_for_each_time_frame):
            for column_index, column in enumerate(self.unique_candles_for_each_time_frame[tf]):
                text = f'"{self.smallest_tf}_{column}"'
                if index == len(self.unique_candles_for_each_time_frame) -1 and column_index == len(self.unique_candles_for_each_time_frame[tf]) -1:
                    final_text = final_text + text
                    final_text = final_text + "\n"
                else:
                    final_text = final_text + text
                    final_text = final_text + ",\n"
                final_text = str(final_text)
        return final_text
                


    def get_column_string_query_list(self, column_list):
        final_text="""

"""
        for index, column in enumerate(column_list):
            text = f'"{column_list[column]}" AS "{self.smallest_tf}_{column}"'
            if index == len(column_list) -1 :
                final_text = final_text + text + "\n"
            else:
                final_text = final_text + text + ",\n"
            final_text = str(final_text)
        return final_text

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
        
    def create_column_string(self, joining_id_arr):
        final_text = f""" 
"""
        if len(joining_id_arr) > 0:
            for index, item in enumerate(joining_id_arr):
                key = list(item.keys())[0]
                value = item[key]
                text = f'id_{value}.rolling_max_{value} AS {key} ,\n'
                final_text = final_text + text
            final_text = str(final_text)
            return final_text
        else:
            return ""
    def create_all_column_string(self):
        data = self.collect_depth_zero_uniqueid
        final_text = f""" 
    """ 
        for index_tf, tf in enumerate(data):
            
            for index, item in enumerate(data[tf]):
                key = list(item.keys())[0]
                text = f'"{key}" ,\n'
                final_text = final_text + text
        final_text = str(final_text)
        return final_text
    def create_cte_for_window_functions(self, tf, stock):
        
        if len( self.collect_all_cte_tables.get(tf, [])) > 0:
            final_text = """ 
WITH
"""     
            for index, item in enumerate(self.collect_all_cte_tables[tf]):
                final_text = final_text + item.replace('"stock_timeframe"', f'"{stock}_{TIMEFRAME_CONVERSION[tf]}"')
                if index == len(self.collect_all_cte_tables[tf]) -1 :

                    final_text = final_text + "\n"
                else:
                    final_text = final_text + ",\n"

            final_text = str(final_text)
            return final_text
        else:
            return ""

        
    def timeframe_and_columns(self, stock, start_date, end_date):
        final_text = """
WITH

"""
        for _, tf in enumerate(self.unique_candles_for_each_time_frame):
            comment = ""
            if tf == "Daily" or tf == "Weekly" or tf == "Monthly":
                comment = "--"
            elif type(tf) == int: 
                pass

            text = f"""
"{TIMEFRAME_CONVERSION[tf]}" AS (
        {self.create_cte_for_window_functions(tf, stock)}
        SELECT 
        {self.create_column_string( [i for i in self.collect_depth_zero_uniqueid.get(tf, [])])}
        s.DATETIME,
        {comment}s.datetime + INTERVAL {tf} minute AS "datetime_end", 
        {self.get_column_string_query_list(self.unique_candles_for_each_time_frame[tf])}
        FROM "{stock}_{TIMEFRAME_CONVERSION[tf]}" s
        {self.join_columns([list(i.values())[0] for i in self.collect_depth_zero_uniqueid.get(tf, [])])}
        WHERE s.datetime BETWEEN '{start_date}' AND '{end_date}'
)"""        
            final_text = final_text + text + ",\n"
            final_text = str(final_text)

        text = f"""
OHLC AS (
SELECT
s.DATETIME, 
'{stock}' AS symbol,
close,
-- Construct YYYYMMDD as integer
date_part('year', datetime) * 10000
+ date_part('month', datetime) * 100
+ date_part('day', datetime) AS date_int,

-- Construct HHMM as integer
date_part('hour', datetime) * 100
+ date_part('minute', datetime) AS time_int,

CASE WHEN ROW_NUMBER() OVER (PARTITION BY date_int ORDER BY time_int) = 1 
THEN 1 ELSE 0 END AS start,
CASE WHEN ROW_NUMBER() OVER (PARTITION BY date_int ORDER BY time_int DESC) = 1 
THEN 1 ELSE 0 END AS end,

CASE WHEN ROW_NUMBER() OVER (ORDER BY s.datetime) = 1 
THEN 1 ELSE 0 END AS start_symbol,
CASE WHEN ROW_NUMBER() OVER (ORDER BY s.datetime DESC) = 1 
THEN 1 ELSE 0 END AS end_symbol

FROM "{stock}_{TIMEFRAME_CONVERSION[self.smallest_tf]}" s
WHERE s.datetime BETWEEN '{start_date}' AND '{end_date}'
),

FRESH AS (
select OHLC.*, 
 
{self.create_all_column_string()}
{self.get_all_candle_string_query_list()}

from OHLC
 
{self.get_all_tf_joining_string_query_list()}

WHERE OHLC.datetime BETWEEN '{start_date}' AND '{end_date}'
order by OHLC.datetime
)

SELECT * FROM FRESH
"""
        
        final_text = final_text + text

        return final_text

    def select_union_all(self):
        final_text = """


"""
        for index, stock in enumerate(self.unique_stock):
            text = f'SELECT * FROM "{stock}"\n'

            final_text = final_text + text
            if index != len(self.unique_stock) - 1:
                final_text = final_text + "UNION ALL\n"
            
        return final_text
        
    def final_query(self, start_date, end_date):
        final_text = """
WITH

"""
        for index, stock in enumerate(self.unique_stock):

            text = f"""
"{stock}" AS (
{self.timeframe_and_columns(stock, start_date, end_date)}
)"""
            if index == len(self.unique_stock) -1 :
                final_text = final_text + text + "\n"
            else:
                final_text = final_text + text + ",\n"
            final_text = str(final_text)
            
        final_text = final_text + self.select_union_all()
        final_text = str(final_text)
        return final_text




