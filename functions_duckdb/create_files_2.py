from functions import indicators
import os
import duckdb
import pandas as pd
from pyarrow import parquet as pq
from functions import timeframe, indicators


# using indicator_process_duckdb/parquet

INDICATOR_FILE_DATABASE = "indicator_process_duckdb"

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


def create_timeframe_files(duckdb_conn, stock, timeframe):
    
    # print("Hellow", timeframe)
    if type(timeframe) == int and 1 <= timeframe and timeframe < 60*4:
        
        raw_data_path = f"Clean_data/1min/{stock}_1min.csv"
        if os.path.isfile(raw_data_path):

            interval = f"{timeframe} minutes"
            
            # os.makedirs(f"{INDICATOR_FILE_DATABASE}/symbol={stock}/tf={TIMEFRAME_CONVERSION[timeframe]}", exist_ok=True)
            query = f"""
COPY (
            SELECT 
                -- 1. Create the time buckets
                time_bucket(INTERVAL '{interval}', datetime - INTERVAL '9 hours 15 minutes') + INTERVAL '9 hours 15 minutes' AS datetime,
                
                -- 2. Open: Price at the earliest time in the bucket
                first(open) AS open,
                
                -- 3. High: Highest price in the bucket
                max(high) AS high,
                
                -- 4. Low: Lowest price in the bucket
                min(low) AS low,
                
                -- 5. Close: Price at the latest time in the bucket
                last(close) AS close,
                
                -- 6. Volume: Total volume in the bucket
                sum(volume) AS volume
                
            FROM "Clean_data/1min/{stock}_1min.csv"
            
            GROUP BY 1
            ORDER BY 1 
)
TO "{INDICATOR_FILE_DATABASE}/symbol={stock}/tf={TIMEFRAME_CONVERSION[timeframe]}/data.parquet"
(FORMAT PARQUET, COMPRESSION ZSTD);
            """

            duckdb_conn.execute(query)
            # print("created", f"{INDICATOR_FILE_DATABASE}/symbol={stock}/tf={TIMEFRAME_CONVERSION[timeframe]}/data.parquet")
    elif type(timeframe) == str and (timeframe == "Daily" or timeframe == "Weekly" or timeframe == "Monthly") :
        # pass
        raw_data_path = f"Clean_data/RAW_daily_data_tradingview/{stock}_Daily.csv"
        if os.path.isfile(raw_data_path):
            # os.makedirs(f"{INDICATOR_FILE_DATABASE}/symbol={stock}/tf={TIMEFRAME_CONVERSION[timeframe]}", exist_ok=True)
            if TIMEFRAME_CONVERSION[timeframe] == "Daily":
                query = f""" 
COPY (
SELECT
        datetime::DATE AS datetime,
        open, high, low, close, volume
    FROM read_csv_auto('{raw_data_path}')


"""
                duckdb_conn.execute(query)
            elif TIMEFRAME_CONVERSION[timeframe] == "Weekly":
                query = f"""
COPY (
WITH raw AS (
    SELECT
        datetime::DATE AS ts,
        open, high, low, close, volume
    FROM read_csv_auto('{raw_data_path}')
),

-- Add year + week (ISO week)
wk AS (
    SELECT
        ts,
        open, high, low, close, volume,
        strftime(ts, '%Y-%W') AS week_key
    FROM raw
),

-- Find first trading day of each week
first_day AS (
    SELECT
        week_key,
        MIN(ts) AS week_start
    FROM wk
    GROUP BY week_key
),

-- Aggregate weekly OHLCV
weekly AS (
    SELECT
        f.week_start AS datetime,
        FIRST(w.open) AS open,
        MAX(w.high)  AS high,
        MIN(w.low)   AS low,
        LAST(w.close) AS close,
        SUM(w.volume) AS volume
    FROM wk w
    JOIN first_day f USING (week_key)
    GROUP BY f.week_start
    ORDER BY f.week_start
)

SELECT * FROM weekly
)
TO "{INDICATOR_FILE_DATABASE}/symbol={stock}/tf={TIMEFRAME_CONVERSION[timeframe]}/data.parquet"
(FORMAT PARQUET, COMPRESSION ZSTD);
"""
                
                duckdb_conn.execute(query)
                
            elif TIMEFRAME_CONVERSION[timeframe] == "Monthly":
                query = f"""
COPY (
WITH raw AS (
    SELECT
        datetime::DATE AS ts,
        open, high, low, close, volume
    FROM read_csv_auto('{raw_data_path}')
),

mo AS (
    SELECT
        ts,
        open, high, low, close, volume,
        strftime(ts, '%Y-%m') AS month_key
    FROM raw
),

first_day AS (
    SELECT
        month_key,
        MIN(ts) AS month_start
    FROM mo
    GROUP BY month_key
),

monthly AS (
    SELECT
        f.month_start AS datetime,
        FIRST(m.open) AS open,
        MAX(m.high)   AS high,
        MIN(m.low)    AS low,
        LAST(m.close) AS close,
        SUM(m.volume) AS volume
    FROM mo m
    JOIN first_day f USING (month_key)
    GROUP BY f.month_start
    ORDER BY f.month_start
)

SELECT * FROM monthly
)
TO "{INDICATOR_FILE_DATABASE}/symbol={stock}/tf={TIMEFRAME_CONVERSION[timeframe]}/data.parquet"
(FORMAT PARQUET, COMPRESSION ZSTD);
"""

                duckdb_conn.execute(query)
                
            elif TIMEFRAME_CONVERSION[timeframe] == "Yearly":
                query = f"""
COPY (
WITH raw AS (
    SELECT
        datetime::DATE AS ts,
        open, high, low, close, volume
    FROM read_csv_auto('{raw_data_path}')
),

yr AS (
    SELECT
        ts,
        open, high, low, close, volume,
        strftime(ts, '%Y') AS year_key
    FROM raw
),

-- First trading day each year
first_day AS (
    SELECT
        year_key,
        MIN(ts) AS year_start
    FROM yr
    GROUP BY year_key
),

yearly AS (
    SELECT
        f.year_start AS datetime,
        FIRST(y.open)  AS open,
        MAX(y.high)    AS high,
        MIN(y.low)     AS low,
        LAST(y.close)  AS close,
        SUM(y.volume)  AS volume
    FROM yr y
    JOIN first_day f USING (year_key)
    GROUP BY f.year_start
    ORDER BY f.year_start
)

SELECT * FROM yearly
)
TO "{INDICATOR_FILE_DATABASE}/symbol={stock}/tf={TIMEFRAME_CONVERSION[timeframe]}/data.parquet"
(FORMAT PARQUET, COMPRESSION ZSTD);
"""

                duckdb_conn.execute(query)
                


def check_if_indicators_not_exist( data):
    # data = {'SBIN_15_close': ['SBIN', 15, 'close', 'SBIN_15_0_close', ['0', 15, 'close']], 
    #     'SBIN_15_sma_250_close': ['SBIN', 15, 'sma_250_close', 'SBIN_15_-1_sma_250_close', ['-1', 15, 'sma', 'close', 250]], 
    #     'SBIN_15_rsi_14_close': ['SBIN', 15, 'rsi_14_close', 'SBIN_15_0_rsi_14_close', ['0', 15, 'rsi', 'close', 14]]}
    print(data)
    data_list = list(data.values())
    print(data_list)
    unique_stock_tf_dict = {}

    for i in range(len(data_list)):
        stock = data_list[i][0]
        time_frame = data_list[i][1]
        key = f"{stock}_{time_frame}"

        if key not in unique_stock_tf_dict:
            unique_stock_tf_dict[key] = []
        unique_stock_tf_dict[key].append(data_list[i])


    # print(unique_stock_tf_dict)
    unique_stock_tf_list = list(unique_stock_tf_dict.values())

    for i in range(len(unique_stock_tf_list)):
        temp = []
        stock = unique_stock_tf_list[i][0][0]
        time_frame = unique_stock_tf_list[i][0][1]
        key = f"{stock}_{time_frame}"
        path = f"{INDICATOR_FILE_DATABASE}/symbol={stock}/tf={TIMEFRAME_CONVERSION[time_frame]}/data.parquet"
        df_columns = pq.read_schema(path).names
        for j in range(len(unique_stock_tf_list[i])):
            indicator_name = unique_stock_tf_list[i][j][2]
            if indicator_name not in df_columns:
                temp.append(unique_stock_tf_list[i][j])
        unique_stock_tf_dict[key] = temp

    return unique_stock_tf_dict
                

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

def create_table_string_query(table_list):
    final_text = """ 
"""
    for _,table in enumerate(table_list):
        text = f"AND table_name = '{table}'\n"
        text = str(text)
    return final_text


def create_indicators(conn , create_indicator_list):
        
        indicator_to_be_created_list = list(create_indicator_list.values())
        for i in range(0, len(indicator_to_be_created_list)):
            
            if len(indicator_to_be_created_list[i]) > 0:
                
                stock_name = indicator_to_be_created_list[i][0][0]
                time_frame = indicator_to_be_created_list[i][0][1]
                # print(stock_name, time_frame)
                # path = f"{INDICATOR_FILE_DATABASE}/symbol={stock_name}/tf={TIMEFRAME_CONVERSION[time_frame]}/data.parquet"
                df = conn.execute(f"""
                                SELECT * FROM "{stock_name}_{TIMEFRAME_CONVERSION[time_frame]}"
                                """).df()
                # print(df)
                for j in range(0, len(indicator_to_be_created_list[i])):
                    
                    df = indicators.get_indicator_shortform(df, indicator_to_be_created_list[i][j][4], 1)
                
                # print(df.columns)
                
                query = f"""
CREATE OR REPLACE TABLE "{stock_name}_{TIMEFRAME_CONVERSION[time_frame]}" AS
SELECT * FROM df                                
                                """
                # print(query)
                conn.execute(query)


def lag_function(conn, stock, timeframe, candle, indicator ):

    if candle < 0 and type(candle) == int:
        pass
    else:
        return

    table = f"{stock}_{TIMEFRAME_CONVERSION[timeframe]}"
    column_name = f"{timeframe}_{candle}_{indicator}"
    try:
        conn.execute(f"""
        ALTER TABLE {table}
        ADD COLUMN "{column_name}" DOUBLE;
        """)
    except :
        print(f"{column_name} already exists in table {table}")
        pass

    # try:
    conn.execute(f"""
    WITH calc AS (
        SELECT 
            datetime,
            lag("{indicator}", {abs(candle)}) OVER (ORDER BY datetime) AS "{column_name}"
        FROM "{table}"
    )
    UPDATE "{table}" AS t
    SET "{column_name}" = c."{column_name}"
    FROM calc c
    WHERE t.datetime = c.datetime;
    """)

def first_candle_function(conn, stock, timeframe, candle, indicator ):

    # if candle < 0 and type(candle) == int:
    #     pass
    # else:
    #     return

    table = f"{stock}_{TIMEFRAME_CONVERSION[timeframe]}"
    column_name = f"{timeframe}_={candle}_{indicator}"
    try:
        conn.execute(f"""
        ALTER TABLE {table}
        ADD COLUMN "{column_name}" DOUBLE;
        """)
    except :
        print(f"{column_name} already exists in table {table}")
        pass

    # try:
    conn.execute(f"""
    WITH calc AS (
        WITH 
                numbered AS (
                    SELECT datetime,
                            "{indicator}", 
                        row_number() OVER (PARTITION BY date_trunc('day', datetime) ORDER BY datetime) AS rn,
                        date_trunc('day', datetime) AS candle_day
                    FROM "{table}"
                    
                    --AND symbol = 'AARTIIND'
                ),
                first_candles AS (
                    SELECT candle_day,
                        MAX(CASE WHEN rn = {abs(candle)} THEN "{indicator}" ELSE NULL END) AS "{indicator}_{abs(candle)}",
                        
                    FROM numbered
                    GROUP BY candle_day
                )

                SELECT n.datetime, n.datetime + INTERVAL 15 minute AS "datetime_end",
                --n."{indicator}", n.rn, f."{indicator}_{abs(candle)}",
                CASE 
                    WHEN (n.rn > 1) THEN f."{indicator}_{abs(candle)}" ELSE NULL
                END as "{column_name}"

                FROM numbered n
                JOIN first_candles f ON n.candle_day = f.candle_day
                ORDER BY n.datetime
    )
    UPDATE "{table}" AS t
    SET "{column_name}" = c."{column_name}"
    FROM calc c
    WHERE t.datetime = c.datetime;
    """)
    # except :
    #     print(f"{indicator} not exists in table {table}")


class CreateFiles:
    def __init__(self, duckdb_conn = duckdb.connect(), stock_list = []):
        self.duckdb_conn = duckdb_conn
        self.stock_list = stock_list
        self.raw_data_list = []
        # list of unique indicator data
        self.unique_indicator_columns = {}
        # list of grouped indicator data need to create indicators
        self.indicator_to_be_created = {}

        self.create_files_list = {}

        self.smallest_tf = "Yearly"

        self.unique_tables = []

        
        


    def accumulate_request_data(self, req_data):
        # temp = convert_req_data_to_list(req_data, stocks_list)
        temp = req_data
        
        for i in range(0, len(temp)):
            stock = temp[i][0]
            time_frame = temp[i][1]
            table_name = f"{stock}_{TIMEFRAME_CONVERSION[time_frame]}"
            if table_name not in self.unique_tables :
                self.unique_tables.append(table_name)


            self.unique_indicator_columns[f"{temp[i][0]}_{temp[i][1]}_{temp[i][2]}"] = temp[i]
            # finding smalles tf
            self.smallest_tf = find_smallest_time_frame(self.smallest_tf, temp[i][1])

            self.create_files_list[f"{temp[i][0]}_{temp[i][1]}"] = temp[i][0:2]
            # print(i,f"{temp[i][0]}_{temp[i][1]}_{temp[i][2]}")
            if temp[i] not in self.raw_data_list:
                self.raw_data_list.append(temp[i])




    def check_files_exist(self):
        unique_indicator_columns_values =  list(self.create_files_list.values())
        length_of_unique_indicator_columns = len(unique_indicator_columns_values)
        # print(unique_indicator_columns_values)
        for i in range(length_of_unique_indicator_columns):

            stock_name = unique_indicator_columns_values[i][0]
            time_frame = unique_indicator_columns_values[i][1]
            tf = time_frame
            if type(time_frame) == int and 0 < time_frame and time_frame < 60*5:
                tf = TIMEFRAME_CONVERSION[time_frame]

            path = f"{INDICATOR_FILE_DATABASE}/symbol={stock_name}/tf={tf}/data.parquet"
            # print(path)
            if os.path.isfile(path):
                print("File exists")
            else:
                print("File does NOT exist")
                create_timeframe_files(self.duckdb_conn, stock_name, time_frame)

    def check_indicator_exist(self):
        self.indicator_to_be_created = check_if_indicators_not_exist(self.unique_indicator_columns)

    def create_indicators_and_candles(self):
        # check and create files
        self.check_files_exist()
        self.check_indicator_exist()
        

        # check and create indicators and candles

        # print(self.raw_data_list)


