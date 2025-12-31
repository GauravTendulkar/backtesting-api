
path = "functions_duckdb/indicator_files"


def joining_condition(smallest, tf, column_name):
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

def first_Candle(smallest, candle, indicator, stock, tf, with_condition, start_date, end_date):

    file_name = ""
    if tf == "Daily" or tf == "Weekly" or tf == "Monthly":
        file_name = tf
    elif type(tf) == int: 
        file_name = f"{tf}min"
    column_name = f'"{smallest}_{stock}_{tf}_={candle}_{indicator}"'
    n = candle
    # indicator = "close"
    if with_condition == True :
        def inner(n, indicator, stock, tf):
            text =f"""
            WITH 
            numbered AS (
                SELECT *,
                    row_number() OVER (PARTITION BY date_trunc('day', datetime) ORDER BY datetime) AS rn,
                    date_trunc('day', datetime) AS candle_day
                FROM "{path}/{stock}_{file_name}.parquet"
                WHERE datetime BETWEEN '{start_date}' AND '{end_date}'
            ),
            first_candles AS (
                SELECT candle_day,
                    MAX(CASE WHEN rn = {n} THEN {indicator} ELSE NULL END) AS {indicator}_{n},
                    
                FROM numbered
                GROUP BY candle_day
            )

            SELECT n.datetime, n.datetime + INTERVAL {tf} minute AS "datetime_end",
            --n.{indicator}, n.rn, f.{indicator}_{n},
            CASE 
                WHEN (n.rn > {n}) THEN f.{indicator}_{n} ELSE NULL
            END as {column_name}

            FROM numbered n
            JOIN first_candles f ON n.candle_day = f.candle_day
            ORDER BY n.datetime

            """
            return text

        text = f"""
        {column_name} AS  (
        {inner(n, indicator, stock, tf)}
        )"""
        return text
    elif with_condition == False:
        return joining_condition(smallest, tf, column_name)
    elif with_condition == "name":
        return f'{column_name}'

def previous_candle(smallest, candle, indicator, stock, tf, with_condition, start_date, end_date):
    file_name = ""
    comment = ""
    if tf == "Daily" or tf == "Weekly" or tf == "Monthly":
        file_name = tf
        comment = "--"
    elif type(tf) == int: 
        file_name = f"{tf}min"
    

    column_name = f'"{smallest}_{stock}_{tf}_-{candle}_{indicator}"'
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
            "{path}/{stock}_{file_name}.parquet"
            WHERE datetime BETWEEN '{start_date}' AND '{end_date}'
            """
            return text

        text = f"""
        {column_name} AS  (
        {inner(n, indicator, stock, tf)}
        )"""
        return text
    elif with_condition == False:
        return joining_condition(smallest, tf, column_name)
    elif with_condition == "name":
        return f'{column_name}'

def current_candle(smallest, candle, indicator, stock, tf, with_condition, start_date, end_date):
    if candle != 0:
        return
    
    file_name = ""
    comment = ""
    if tf == "Daily" or tf == "Weekly" or tf == "Monthly":
        file_name = tf
        comment = "--"
    elif type(tf) == int: 
        file_name = f"{tf}min"
    
    column_name = f'"{smallest}_{stock}_{tf}_{candle}_{indicator}"'
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
            "{path}/{stock}_{file_name}.parquet"
            WHERE datetime BETWEEN '{start_date}' AND '{end_date}'
            """
            return text

        text = f"""
        {column_name} AS  (
        {inner(n, indicator, stock, tf)}
        )"""
        return text
    elif with_condition == False:
        return joining_condition(smallest, tf, column_name)
    elif with_condition == "name":
        return f'"{smallest}_{stock}_{tf}_{n}_{indicator}"'




def candle(smallest, candle, indicator, stock, tf, with_condition, start_date, end_date):
    if type(candle) == int:
        if candle == 0:
            return current_candle(smallest, candle, indicator, stock, tf, with_condition, start_date, end_date)
        elif candle < 0 :
            return previous_candle(smallest, abs(candle), indicator, stock, tf, with_condition, start_date, end_date)
    elif type(candle) == str and (tf != "Daily" or tf != "Weekly" or tf != "Monthly"):

        if candle.startswith("="):
            
            return first_Candle(smallest, int(candle[1:]), indicator, stock, tf, with_condition, start_date, end_date)

def all_candle(stock, column_array, with_condition , start_date, end_date):
    fullText = """ 

"""
    for i in range(len(column_array[stock])):
        t = column_array[stock][i]
        if t[4][0].startswith("="): 
            fullText += candle(15, t[4][0], t[2], stock, t[1], with_condition, '2022-02-28', '2023-02-28')
        else:
            # print(t[4][0])
            fullText += candle(15, int(t[4][0]), t[2], stock, t[1], with_condition, '2022-02-28', '2023-02-28')
        # print(fullText)
        if with_condition != False:
            fullText = fullText + ",\n"
        else:
            fullText = fullText + "\n"
        fullText = str(fullText)
    return fullText

# def return_main(stock, smallest, start_date, end_date):
#     smallest = 15
#     textFinal = f""" 
#         WITH 
#         {candle(smallest, -1, "close", stock, 60, True, start_date, end_date)},
#         {candle(smallest, 0, "H4", stock, "Daily", True, start_date, end_date)},
#         {candle(smallest, "=1", "close", stock, 15, True, start_date, end_date)},
        
#         OHLC AS (
#         SELECT 
#             DATETIME, 
#             close,
#             -- Construct YYYYMMDD as integer
#             --date_part('year', datetime) * 10000
#             --+ date_part('month', datetime) * 100
#             --+ date_part('day', datetime) AS date_int,

#             -- Construct HHMM as integer
#             date_part('hour', datetime) * 100
#             + date_part('minute', datetime) AS time_int
#             FROM "{path}/{stock}_{smallest}min.parquet"
#         ),



#         Fresh AS  (SELECT OHLC.*, --,  "close_=2".DATETIME + INTERVAL 15 minute AS MIN   
#         {candle(smallest, -1, "close", stock, 60, "name", start_date, end_date)},
#         {candle(smallest, 0, "H4", stock, "Daily", "name", start_date, end_date)},
#         {candle(smallest, "=1", "close", stock, 15, "name", start_date, end_date)},
#         OHLC.datetime
#         from OHLC 
#         {candle(smallest, -1, "close", stock, 60, False, start_date, end_date)}
#         {candle(smallest, 0, "H4", stock, "Daily", False, start_date, end_date)}
#         {candle(smallest, "=1", "close", stock, 15, False, start_date, end_date)}
#         --LEFT JOIN "close_=1" ON OHLC.DATETIME = "close_=1".DATETIME
#         --LEFT JOIN "close_=2" ON OHLC.DATETIME = "close_=2".DATETIME
#         --LEFT JOIN "close_=2" ON (OHLC.DATETIME >= "close_=2".DATETIME  AND OHLC.DATETIME < "close_=2".DATETIME_END )
#         --LEFT JOIN "close_=2" ON date_trunc('minute', OHLC.datetime) = "close_=2".DATETIME
#         WHERE
#         --OHLC.datetime BETWEEN '2019-10-30' AND '2024-10-30'
#         OHLC.datetime BETWEEN '{start_date}' AND '{end_date}'
        
#         ORDER BY OHLC.DATETIME)

#         select 
#         datetime,
#         CASE
#             WHEN ((time_int <= 1115 )
#             AND ({candle(smallest, "=1", "close", stock, 15, "name")} > {candle(smallest, 0, "H4", stock, "Daily", "name")} ) ) THEN TRUE ELSE FALSE

#         END as condition,
#         '{stock}' AS stock
        
#         from Fresh"""
#     return textFinal



# def return_main(stock, column_array, smallest, start_date, end_date):
#     # smallest = 15
#     path = "functions_duckdb/indicator_files"
#     textFinal = f""" 
# WITH 
#         {all_candle(stock, column_array, True ,  start_date, end_date )}
        
#         OHLC AS (
#         SELECT 
#             DATETIME, 
#             close,
#             -- Construct YYYYMMDD as integer
#             --date_part('year', datetime) * 10000
#             --+ date_part('month', datetime) * 100
#             --+ date_part('day', datetime) AS date_int,

#             -- Construct HHMM as integer
#             date_part('hour', datetime) * 100
#             + date_part('minute', datetime) AS time_int
#             FROM "{path}/{stock}_{smallest}min.parquet"
#         ),



#         Fresh AS  (SELECT OHLC.*, --,  "close_=2".DATETIME + INTERVAL 15 minute AS MIN   
        
        
#         {all_candle(stock, column_array , "name" ,  start_date, end_date  )}

#         OHLC.datetime
#         from OHLC 
        
        
#         {all_candle(stock, column_array , False ,  start_date, end_date  )}
#         --LEFT JOIN "close_=1" ON OHLC.DATETIME = "close_=1".DATETIME
#         --LEFT JOIN "close_=2" ON OHLC.DATETIME = "close_=2".DATETIME
#         --LEFT JOIN "close_=2" ON (OHLC.DATETIME >= "close_=2".DATETIME  AND OHLC.DATETIME < "close_=2".DATETIME_END )
#         --LEFT JOIN "close_=2" ON date_trunc('minute', OHLC.datetime) = "close_=2".DATETIME
#         WHERE
#         --OHLC.datetime BETWEEN '2019-10-30' AND '2024-10-30'
#         OHLC.datetime BETWEEN '{start_date}' AND '{end_date}'
        
#         ORDER BY OHLC.DATETIME)

#         select 
#         datetime,
#         CASE
#             WHEN ((time_int <= 1115 )
#             AND ({candle(smallest, -1, "close", stock, 15, "name", start_date, end_date)} > {candle(smallest, 0, "H4", stock, "Daily", "name", start_date, end_date)} ) ) THEN TRUE ELSE FALSE

#         END as condition,
#         '{stock}' AS stock
        
#         from Fresh"""
#     return textFinal



def return_main(stock, column_array, smallest, start_date, end_date):
    # smallest = 15
    path = "functions_duckdb/indicator_files"
    textFinal = f""" 
    select 
        datetime,
        CASE
            WHEN ((time_int <= 1115 )
            AND ({candle(smallest, -1, "close", stock, 15, "name", start_date, end_date)} > {candle(smallest, 0, "H4", stock, "Daily", "name", start_date, end_date)} ) ) THEN TRUE ELSE FALSE

        END as condition,
        '{stock}' AS stock
        
from (
    WITH 
        {all_candle(stock, column_array, True ,  start_date, end_date )}
        
        OHLC AS (
        SELECT 
            DATETIME, 
            close,
            -- Construct YYYYMMDD as integer
            --date_part('year', datetime) * 10000
            --+ date_part('month', datetime) * 100
            --+ date_part('day', datetime) AS date_int,

            -- Construct HHMM as integer
            date_part('hour', datetime) * 100
            + date_part('minute', datetime) AS time_int
            FROM "{path}/{stock}_{smallest}min.parquet"
        ),



        Fresh AS  (SELECT OHLC.*, --,  "close_=2".DATETIME + INTERVAL 15 minute AS MIN   
        
        
        {all_candle(stock, column_array , "name" ,  start_date, end_date  )}

        OHLC.datetime
        from OHLC 
        
        
        {all_candle(stock, column_array , False ,  start_date, end_date  )}
        --LEFT JOIN "close_=1" ON OHLC.DATETIME = "close_=1".DATETIME
        --LEFT JOIN "close_=2" ON OHLC.DATETIME = "close_=2".DATETIME
        --LEFT JOIN "close_=2" ON (OHLC.DATETIME >= "close_=2".DATETIME  AND OHLC.DATETIME < "close_=2".DATETIME_END )
        --LEFT JOIN "close_=2" ON date_trunc('minute', OHLC.datetime) = "close_=2".DATETIME
        WHERE
        --OHLC.datetime BETWEEN '2019-10-30' AND '2024-10-30'
        OHLC.datetime BETWEEN '{start_date}' AND '{end_date}'
        
        ORDER BY OHLC.DATETIME)

        SELECT * FROM Fresh
        )

        """
    return textFinal



def return_main_data(stock, column_array, smallest, start_date, end_date):
    # smallest = 15
    path = "functions_duckdb/indicator_files"
    textFinal = f""" 
    
    WITH 
        {all_candle(stock, column_array, True ,  start_date, end_date )}
        
        OHLC AS (
        SELECT 
            DATETIME, 
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
            THEN 1 ELSE 0 END AS end


            FROM "{path}/{stock}_{smallest}min.parquet"
        ),



        Fresh AS  (SELECT OHLC.*, --,  "close_=2".DATETIME + INTERVAL 15 minute AS MIN   
        
        
        {all_candle(stock, column_array , "name" ,  start_date, end_date  )}

        OHLC.datetime
        from OHLC 
        
        
        {all_candle(stock, column_array , False ,  start_date, end_date  )}
        --LEFT JOIN "close_=1" ON OHLC.DATETIME = "close_=1".DATETIME
        --LEFT JOIN "close_=2" ON OHLC.DATETIME = "close_=2".DATETIME
        --LEFT JOIN "close_=2" ON (OHLC.DATETIME >= "close_=2".DATETIME  AND OHLC.DATETIME < "close_=2".DATETIME_END )
        --LEFT JOIN "close_=2" ON date_trunc('minute', OHLC.datetime) = "close_=2".DATETIME
        WHERE
        --OHLC.datetime BETWEEN '2019-10-30' AND '2024-10-30'
        OHLC.datetime BETWEEN '{start_date}' AND '{end_date}'
        
        ORDER BY OHLC.DATETIME)

        SELECT * FROM Fresh
        

        """
    return textFinal