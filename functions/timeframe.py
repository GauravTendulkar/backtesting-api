import pandas as pd
from functions import functions
import numpy as np
from datetime import date
from numba import njit
# 1m 14s to run below code
# def timeframe_1min(df):
#     # uniqueDate = pd.DataFrame({"uniquedate":np.sort(df['date'].unique())} )
#     # df["symbol"] = symbol_
#     df['date'] = df.index.date
#     df['time'] = df.index.time
#     uniqueTime = pd.read_csv("Clean_data/uniqueTime.csv",low_memory=False,index_col=[0])
#     temp = pd.DataFrame()
#     temp['symbol'] = ''
#     temp['open'] = 0.0
#     temp['high'] = 0.0
#     temp['low'] = 0.0
#     temp['close'] = 0.0
#     temp['volume'] = 0.0
#     temp['datetime'] = ''

#     def dfTime_index(time):
#         def binary_search(arr, target):
#             left, right = 0, len(arr) - 1
#             while left <= right:
#                 mid = (left + right) // 2
#                 if arr[mid] == target:
#                     return mid
#                 elif arr[mid] < target:
#                     left = mid + 1
#                 else:
#                     right = mid - 1
#             return -1
#         return binary_search(uniqueTime['uniqueTime'], str(time))
    
#     # index_list = []
#     a = {}
#     symbol =  np.full(len(df), '', dtype=f'<U{len(df.loc[df.index[0], 'symbol'])}')
#     open = np.zeros((len(df)))
#     high = np.zeros((len(df)))
#     low = np.zeros((len(df)))
#     close = np.zeros((len(df)))
#     volume = np.zeros((len(df)), dtype= int)
#     datetime = np.full(len(df), '', dtype=f'<U{20}')
#     count = 0
#     for j in range(0, len(df)):
#         if str(df.loc[df.index[j], 'time']) in a:
#             x = a[str(df.loc[df.index[j], 'time'])]
#         else:
#             a[str(df.loc[df.index[j], 'time'])] = dfTime_index(df.loc[df.index[j], 'time'])
#             x = a[str(df.loc[df.index[j], 'time'])]
#         # x = dfTime_index(df.loc[df.index[j], 'time'])
#         # print(x)
#         if 1 <= x  and x <= 375:
            
#             symbol[count] = df.loc[df.index[j],'symbol']
#             open[count] = df.loc[df.index[j],'open']
#             high[count] = df.loc[df.index[j],'high']
#             low[count] = df.loc[df.index[j],'low']
#             close[count] = df.loc[df.index[j],'close']
#             volume[count] = df.loc[df.index[j],'volume']
#             datetime[count] = df.index[j]
#             count += 1
#     temp['symbol'] = symbol
#     temp['open'] = open
#     temp['high'] = high
#     temp['low'] = low
#     temp['close'] = close
#     temp['volume'] = volume
#     temp['datetime'] = datetime

#     temp = temp[:count]
            
#     temp.index = pd.to_datetime(temp['datetime'])
#     del temp['datetime']
#     return temp

# 4.1s to run below code
def timeframe_1min(df):
    # Precompute columns and unique time mapping
    uniqueTime = pd.read_csv("Clean_data/uniqueTime.csv", low_memory=False, index_col=[0])
    unique_time_values = uniqueTime['uniqueTime'].values
    df['time_str'] = df.index.time.astype(str)  # Precompute time as string
    
    # Dictionary for caching time indices
    time_cache = {}

    # Preallocate lists to collect data
    symbols, opens, highs, lows, closes, volumes, datetimes = [], [], [], [], [], [], []

    for time, row in zip(df['time_str'], df.itertuples()):
        if time not in time_cache:
            # Use numpy searchsorted for efficient binary search
            idx = np.searchsorted(unique_time_values, time)
            if idx < len(unique_time_values) and unique_time_values[idx] == time:
                time_cache[time] = idx
            else:
                time_cache[time] = -1
        else:
            idx = time_cache[time]

        if 1 <= idx <= 375:  # Keep rows within this range
            symbols.append(row.symbol)
            opens.append(row.open)
            highs.append(row.high)
            lows.append(row.low)
            closes.append(row.close)
            volumes.append(row.volume)
            datetimes.append(row.Index)

    # Create DataFrame from collected data
    temp = pd.DataFrame({
        'symbol': symbols,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    }, index=pd.to_datetime(datetimes))
    temp.index.name = "datetime"
    return temp

# ________________________________________________________________
# @njit
def binary_search(arr, target):
    # key = str((arr, target))
    # if key in cache:
    #     return cache[key]
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            # cache[key] = mid
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    # cache[key] = -1
    return -1

def convert_1min_anymin(df, timeframe):
    df['date'] = df.index.date
    df['time'] = df.index.time
    cache = {}
    temp = functions.timeframe_divide_uniqueTime(timeframe)
    temp_1 = functions.timeframe_divide_uniqueTime(1)
    temp_list = list(temp['uniqueTime_'+str(timeframe)])
    temp_1_list = list(temp_1['uniqueTime_1'])

    def dfTime_index(time, timeframe):
        # uniqueTime = timeframe_divide_uniqueTime(timeframe)

        if timeframe == 1:
            return binary_search(temp_1_list , str(time))
        else:
            return binary_search(temp_list, str(time))


    return_df = pd.DataFrame()
    return_df['symbol'] = ''
    return_df['open'] = 0.0
    return_df['high'] = 0.0
    return_df['low'] = 0.0
    return_df['close'] = 0.0
    return_df['volume'] = 0.0
    return_df['datetime'] = ''
    # index_list = []
    symbol =  np.full(len(df), '', dtype=f'<U{len(df.loc[df.index[0], 'symbol'])}')
    open = np.zeros((len(df)))
    high = np.zeros((len(df)))
    low = np.zeros((len(df)))
    close = np.zeros((len(df)))
    volume = np.zeros((len(df)), dtype= object)
    datetime = np.full(len(df), '', dtype=f'<U{20}')
    count = 0
    
    for k in range(0, len(df)):
        # print(df.loc[df.index[k],'time'])
        if dfTime_index(df.loc[df.index[k],'time'], timeframe) > -1:
            if str(df.loc[df.index[k],'time']) == str(temp.loc[temp.index[-1],'uniqueTime_'+str(timeframe)]):
                s = dfTime_index(df.loc[df.index[k],'time'], 1)
                
                symbol[count] = df.loc[df.index[k],'symbol']
                open[count] = df.loc[df.index[k],'open']
                high[count] = df.loc[df.index[k]:df.index[k-1+375-s],'high'].max()
                low[count] = df.loc[df.index[k]:df.index[k-1+375-s],'low'].min()
                close[count] = df.loc[df.index[k-1+375-s],'close']
                volume[count] = df.loc[df.index[k]:df.index[k-1+375-s],'volume'].sum()
                datetime[count] = df.index[k]
                count += 1

                
            else:
                symbol[count] = df.loc[df.index[k],'symbol']
                open[count] = df.loc[df.index[k],'open']
                high[count] = df.loc[df.index[k]:df.index[k-1+timeframe],'high'].max()
                low[count] = df.loc[df.index[k]:df.index[k-1+timeframe],'low'].min()
                close[count] = df.loc[df.index[k-1+timeframe],'close']
                volume[count] = df.loc[df.index[k]:df.index[k-1+timeframe],'volume'].sum()
                datetime[count] = df.index[k]
                count += 1
                
                
    return_df['symbol'] = symbol
    return_df['open'] = open
    return_df['high'] = high
    return_df['low'] = low
    return_df['close'] = close
    return_df['volume'] = volume
    return_df['datetime'] = datetime
    return_df = return_df[:count]
                
    return_df.index = pd.to_datetime(return_df['datetime'])
    del return_df['datetime']
    
    return return_df


#______________________________________________________________________
# this function retuens the correct format for Daily Time Frame
#
#
# def timeframe_Daily(df):
#     df["symbol"] = df["symbol"].str[4:]
#     df["open"] = (df["open"] / 0.05).round() * 0.05
#     df["high"] = (df["high"] / 0.05).round() * 0.05
#     df["low"] = (df["low"] / 0.05).round() * 0.05
#     df["close"] = (df["close"] / 0.05).round() * 0.05
#     df["volume"] = df["volume"].astype(int)
#     return df

def timeframe_Daily(df):
    # df["symbol"] = df["symbol"].str[4:]
    df.index = df.index.map(lambda x: x.replace(hour=9, minute=15, second=0))
    df["open"] = ((df["open"] / 0.05).round() * 0.05).round(2)
    df["high"] = ((df["high"] / 0.05).round() * 0.05).round(2)
    df["low"] = ((df["low"] / 0.05).round() * 0.05).round(2)
    df["close"] = ((df["close"] / 0.05).round() * 0.05).round(2)
    df["volume"] = df["volume"].astype(int)
    return df



def convert_daily_weekly_and_monthly(df_daily, tf):
    df_daily["date"] = df_daily.index.date
    df_daily["time"] = df_daily.index.time
    
    # df_daily["date"] = 
    if tf == "Weekly":
        df_daily["weekdays"] = pd.to_datetime(df_daily["date"]).dt.weekday
    if tf == "Monthly":
        df_daily["weekdays"] = pd.to_datetime(df_daily["date"]).dt.day
    temp = []
    temp_collect = []
    week_start = 0
    for i in range(0, len(df_daily)-1):
       
        if df_daily.loc[df_daily.index[i-1], "weekdays"] > df_daily.loc[df_daily.index[i], "weekdays"] and week_start == 0:
           
            temp_collect.append(i)
            week_start = 1

        if df_daily.loc[df_daily.index[i], "weekdays"] > df_daily.loc[df_daily.index[i+1], "weekdays"] and week_start == 1:
            temp_collect.append(i)
            temp.append(temp_collect)
            temp_collect = []
            week_start = 0

    symbols, opens, highs, lows, closes, volumes, datetimes = [], [], [], [], [], [], []

    for i in range(0, len(temp)):

        symbols.append(df_daily.loc[df_daily.index[temp[i][0]], "symbol"])
        opens.append(df_daily.loc[df_daily.index[temp[i][0]], "open"])
        highs.append(df_daily.loc[df_daily.index[temp[i][0]]:df_daily.index[temp[i][1]], "high"].max())
        lows.append(df_daily.loc[df_daily.index[temp[i][0]]:df_daily.index[temp[i][1]], "low"].min())
        closes.append(df_daily.loc[df_daily.index[temp[i][1]], "close"])
        volumes.append(df_daily.loc[df_daily.index[temp[i][0]] : df_daily.index[temp[i][1]], "volume"].sum())
        datetimes.append(df_daily.index[temp[i][0]])
  

    df_weekly = pd.DataFrame({
        'symbol': symbols,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    }, index=pd.to_datetime(datetimes))

    df_weekly.index.name = "datetime"


    return df_weekly