
from functions import indicators
import duckdb


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

    def __init__(self, stock_list = [], duckdb_conn = duckdb.connect()):

        self.duckdb_conn = duckdb_conn
        self.stock_list = stock_list
        self.raw_data_list = []
        self.unique_time_frame = []
        self.unique_column_for_each_time_frame = {}

        self.smallest_tf = "Yearly"

        self.raw_data_group_by_stock = {}

        self.unique_stock = []

       

    def accumulate_request_data(self, req_data):
        temp = convert_req_data_to_list(req_data, self.stock_list)
        
        for i in range(0, len(temp)):
            
            stock = temp[i][0]
            time_frame = temp[i][1]
            indicator_column = temp[i][2]

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


    # create stock list
    def list_of_stock_text(self):
        stock_list = self.stock_list
        final_text = """ 

"""
        for i in range(0, len(stock_list)):
            if len(stock_list) - 1 == i:
                final_text += f"'{stock_list[i]}'"
            else:
                final_text += f"'{stock_list[i]}',"
                final_text += "\n"

            
            final_text = str(final_text)
        # print(final_text)
        return final_text
    
    def timeframe_columns(self, time_frame : str):
        indicator_column_list = self.unique_column_for_each_time_frame[f"{time_frame}"]
        final_text = """ 
symbol,
tf,
datetime,
"""
        for i in range(0, len(indicator_column_list)):
            if len(indicator_column_list) - 1 == i:
                final_text += f'"{indicator_column_list[i]}"'
            else:
                final_text += f'"{indicator_column_list[i]}",'
                final_text += "\n"

            
            final_text = str(final_text)
        return final_text



    # select columns for each timeframe
    def get_raw_tf_data(self, time_frame):
        final_text = f""" 
    SELECT
        {self.timeframe_columns(TIMEFRAME_CONVERSION_REVERSED[time_frame])}
        
    FROM read_parquet('indicator_process_duckdb/*/*/*.parquet' , hive_partitioning = true )
    WHERE symbol IN (
    {self.list_of_stock_text()}
    )   
    and tf = '{time_frame}'

    """
        return final_text
    
    ## get joining string
    def joining_condition(self, smallest, tf, column_name):
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

    ## get previous candle
    def previous_candle(self, smallest, candle, indicator, stock, tf, with_condition, start_date, end_date):
        file_name = ""
        comment = ""
        if tf == "Daily" or tf == "Weekly" or tf == "Monthly":
            file_name = tf
            comment = "--"
        elif type(tf) == int: 
            file_name = f"{tf}min"
        

        column_name = f'"{smallest}_{tf}_-{candle}_{indicator}"'
        # print("column_name", column_name)
        n = candle
        # indicator = "close"
        if with_condition == True :
            def inner(n, indicator, stock, tf):
                text =f"""
                SELECT 
                datetime, 
                {comment}datetime + INTERVAL {tf} minute AS "datetime_end", 
                lag("{indicator}", {n}) OVER (ORDER BY datetime) AS {column_name}, 
                FROM
                "{TIMEFRAME_CONVERSION[tf]}_table"
                WHERE datetime BETWEEN '{start_date}' AND '{end_date}'
                """
                return text

            text = f"""
            {column_name} AS  (
            {inner(n, indicator, stock, tf)}
            )"""
            return text
        elif with_condition == False:
            
            return self.joining_condition(smallest, tf, column_name)
        elif with_condition == "name":
            return f'{column_name}'

    ## get current candle
    def current_candle(self, smallest, candle, indicator, stock, tf, with_condition, start_date, end_date):
        if candle != 0:
            return
        
        file_name = ""
        comment = ""
        if tf == "Daily" or tf == "Weekly" or tf == "Monthly":
            file_name = tf
            comment = "--"
        elif type(tf) == int: 
            file_name = f"{tf}min"
        
        column_name = f'"{smallest}_{tf}_{candle}_{indicator}"'
        n = candle
        # indicator = "close"
        if with_condition == True :
            def inner(n, indicator, stock, tf):
                text =f"""
                SELECT 
                datetime, 
                {comment}datetime + INTERVAL {tf} minute AS "datetime_end", 
                "{indicator}" AS {column_name}, 
                FROM
                "{TIMEFRAME_CONVERSION[tf]}_table"
                WHERE datetime BETWEEN '{start_date}' AND '{end_date}'
                """
                return text

            text = f"""
            {column_name} AS  (
            {inner(n, indicator, stock, tf)}
            )"""
            return text
        elif with_condition == False:
            return self.joining_condition(smallest, tf, column_name)
        elif with_condition == "name":
            return f'{column_name}'

        def candle(self, smallest, candle, indicator, stock, tf, with_condition, start_date, end_date):
            if type(candle) == int:
                if candle == 0:
                    pass
                    # return self.current_candle(smallest, candle, indicator, stock, tf, with_condition, start_date, end_date)
                elif candle < 0 :
                    return self.previous_candle(smallest, abs(candle), indicator, stock, tf, with_condition, start_date, end_date)
            elif type(candle) == str and (tf != "Daily" or tf != "Weekly" or tf != "Monthly"):

                if candle.startswith("="):
                    pass
                    # return self.first_Candle(smallest, int(candle[1:]), indicator, stock, tf, with_condition, start_date, end_date)


    def candle(self, smallest, candle, indicator, stock, tf, with_condition, start_date, end_date):
        if type(candle) == int:
            if candle == 0:
                return self.current_candle(smallest, candle, indicator, stock, tf, with_condition, start_date, end_date)
            elif candle < 0 :
                return self.previous_candle(smallest, abs(candle), indicator, stock, tf, with_condition, start_date, end_date)
        elif type(candle) == str and (tf != "Daily" or tf != "Weekly" or tf != "Monthly"):

            if candle.startswith("="):
                
                return self.first_Candle(smallest, int(candle[1:]), indicator, stock, tf, with_condition, start_date, end_date)
    
    def all_candle(self, stock, column_array, with_condition , start_date, end_date):
        fullText = """ 

    """
        for i in range(len(column_array[stock])):
            t = column_array[stock][i]
            if t[4][0].startswith("="): 
                fullText += self.candle(self.smallest_tf, t[4][0], t[2], stock, t[1], with_condition, start_date, end_date)
            else:
                # print(t[4][0])
                # print(t[4][0] , type(t[4][0]))
                # if int(t[4][0]) != 0:   ## remove this condition
                fullText += self.candle(self.smallest_tf, int(t[4][0]), t[2], stock, t[1], with_condition, start_date, end_date)
            # print(fullText)
            if with_condition != False:
                fullText = fullText + ",\n"
            else:
                fullText = fullText + "\n"
            fullText = str(fullText)
        return fullText
    


    def prepare_columns_for_each_stock(self, stock, start_date , end_date ) :
    
        final_text = f"""
WITH 

{self.all_candle(stock, self.raw_data_group_by_stock, True , start_date, end_date)}
OHLC AS (
SELECT
DATETIME, 
SYMBOL,
close,
-- Construct YYYYMMDD as integer
--date_part('year', datetime) * 10000
--+ date_part('month', datetime) * 100
--+ date_part('day', datetime) AS date_int,

-- Construct HHMM as integer
date_part('hour', datetime) * 100
+ date_part('minute', datetime) AS time_int
FROM "15min_table"
WHERE symbol = '{stock}'

),

FRESH AS (
select OHLC.*, 
{self.all_candle(stock, self.raw_data_group_by_stock, "name" , start_date, end_date)}
from OHLC
{self.all_candle(stock, self.raw_data_group_by_stock, False , start_date, end_date)}
WHERE OHLC.datetime BETWEEN '{start_date}' AND '{end_date}'
order by OHLC.datetime
)

SELECt * FROM FRESH

"""
    
        return final_text


    def accumulate_prepare_columns_for_each_stock(self, start_date , end_date):
        length_of_stock_list = len(self.unique_stock)
        final_text = f"""
"""
        for index, stock in enumerate(self.unique_stock) :
        # for stock in stock_list :
            text = f"""
"{stock}" AS (
{self.prepare_columns_for_each_stock(stock , start_date , end_date)}
)"""
            final_text += text
            if length_of_stock_list -1  == index:
                final_text = final_text + "\n"  
            else:
                final_text = final_text + ",\n"  
            final_text = str(final_text)
            # print(index, stock)
        return final_text
    




    def fetch_all_timeframes(self):
    # obj.unique_time_frame
        final_text = f""" 
"""
        for index, tf in enumerate(self.unique_time_frame):
            text = f""" 
'{TIMEFRAME_CONVERSION[tf]}_table' AS (
{self.get_raw_tf_data(TIMEFRAME_CONVERSION[tf])}
)"""
            final_text += text
            final_text = final_text + ",\n"
            final_text = str(final_text)

        return final_text
    

    def union_all_stock(self):
        length_of_stock_list = len(self.unique_stock) 
        final_text = f"""
"""    
        for index, stock in enumerate(self.unique_stock):
            text = f'SELECT * FROM "{stock}"'
            final_text += text
            final_text = final_text + "\n"
            if length_of_stock_list - 1 == index:
                final_text = final_text + "\n"
            else:
                final_text = final_text + "UNION ALL"
                final_text = final_text + "\n"
            final_text = str(final_text)

        return final_text