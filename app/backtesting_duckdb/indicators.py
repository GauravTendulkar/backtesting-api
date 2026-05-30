import pandas as pd
import numpy as np
# import pandas_ta as ta
# import time
from datetime import date
# import threading
# import multiprocessing
# from pathlib import Path
from openalgo import ta

#__________________________________________________________

# def if_index_exist(arr_list, number):
#     try:
#         if arr_list[number]:
#             return True
#     except:
#         return False
    
def if_index_exist(arr_list, arr_number):
    
    try:
        for i in range(0, len(arr_number)):
            # print(arr_number[i])
            if arr_list[arr_number[i]]:
                pass
        return True
    except:
            return False

def get_indicator_shortform(df, arr, num_one):
    temp = []
    temp_str = ""
    try:
        for i in arr:
            temp.append(i["value"])
    except:
        temp = arr
    
    if if_index_exist(temp, [0]):
        if (temp[0] == "<" or temp[0] == ">" or temp[0] == "==" or temp[0] == "!=" or temp[0] == "<=" or temp[0] == ">=" or temp[0] == "entry" or temp[0] == "number"
            or temp[0] == "+" or temp[0] == "-" or temp[0] == "*" or temp[0] == "/" or temp[0] == "(" or temp[0] == ")"):
            temp_str = f"{temp[0]}"

    if if_index_exist(temp, [2]) :
        # datetime_number
        if temp[2] == "datetime_number":
            temp_str = "datetime_number"
            if num_one == 1:
                return df

    if if_index_exist(temp, [2, 3, 4]) :
        
        
        # SMA
        if temp[2] == "sma":
            temp_str = f"{temp[2]}_{temp[4]}_{temp[3]}"
            if num_one == 1:
                return sma_generator(df, temp[3], temp[4])
        # EMA
        if temp[2] == "ema":
            temp_str = f"{temp[2]}_{temp[4]}_{temp[3]}"
            if num_one == 1:
                return ema_generator(df, temp[3], temp[4])
        # RSI
        if temp[2] == "rsi":
            temp_str = f"{temp[2]}_{temp[4]}_{temp[3]}"
            if num_one == 1:
                column_name = f'rsi_{temp[4]}_{temp[3]}'
                df[column_name] = ta.rsi(data = df[f"{temp[3]}"] , period=temp[4] )
                return df
                
                # return rsi_generator(df, temp[3], temp[4])
    # BB
    if if_index_exist(temp, [2, 3, 4, 5, 6]):
        if temp[2] == "BBbasis":
            temp_str = f"{temp[2]}_{temp[3]}_{temp[4]}_{temp[5]}_{temp[6]}"
            if num_one == 1:
                return bb_generator(df, temp[3], temp[4], temp[5], temp[6])
        if temp[2] == "BBupper":
            temp_str = f"{temp[2]}_{temp[3]}_{temp[4]}_{temp[5]}_{temp[6]}"
            if num_one == 1:
                return bb_generator(df, temp[3], temp[4], temp[5], temp[6])
        if temp[2] == "BBlower":
            temp_str = f"{temp[2]}_{temp[3]}_{temp[4]}_{temp[5]}_{temp[6]}"
            if num_one == 1:
                return bb_generator(df, temp[3], temp[4], temp[5], temp[6])
           
            
    if if_index_exist(temp, [2, 3, 4, 5, 6]) :
        # MACD
        if temp[2] == "macdLine"     :
            temp_str = f'macdLine_{int(temp[3])}_{int(temp[4])}_{int(temp[5])}_{str(temp[6])}' 
            if num_one == 1:
                return calculate_macd(df, int(temp[3]), int(temp[4]), int(temp[5]), str(temp[6]))
        elif temp[2] == "signalLine":
            temp_str = f"signalLine_{int(temp[3])}_{int(temp[4])}_{int(temp[5])}_{str(temp[6])}"
            if num_one == 1:
                return calculate_macd(df, int(temp[3]), int(temp[4]), int(temp[5]), str(temp[6]))
        elif temp[2] == "macdHistogram":
            temp_str = f"macdHistogram_{int(temp[3])}_{int(temp[4])}_{int(temp[5])}_{str(temp[6])}"
            if num_one == 1:
                return calculate_macd(df, int(temp[3]), int(temp[4]), int(temp[5]), str(temp[6]))
            
    if if_index_exist(temp, [2, 3, 4, 5, 6]) :
        # Ichimoku_cloud
        if temp[2] == "conversionLineIC"     :
            temp_str = f'conversionLineIC_{int(temp[3])}_{int(temp[4])}_{int(temp[5])}_{int(temp[6])}' 
            if num_one == 1:
                return Ichimoku_cloud(df, int(temp[3]), int(temp[4]), int(temp[5]), int(temp[6]))
        elif temp[2] == "baseLineIC":
            temp_str = f"baseLineIC_{int(temp[3])}_{int(temp[4])}_{int(temp[5])}_{int(temp[6])}"
            if num_one == 1:
                return Ichimoku_cloud(df, int(temp[3]), int(temp[4]), int(temp[5]), int(temp[6]))
        elif temp[2] == "laggingLineIC":
            temp_str = f"laggingLineIC_{int(temp[3])}_{int(temp[4])}_{int(temp[5])}_{int(temp[6])}"
            if num_one == 1:
                return Ichimoku_cloud(df, int(temp[3]), int(temp[4]), int(temp[5]), int(temp[6]))
        elif temp[2] == "leadingSpanAIC":
            temp_str = f"leadingSpanAIC_{int(temp[3])}_{int(temp[4])}_{int(temp[5])}_{int(temp[6])}"
            if num_one == 1:
                return Ichimoku_cloud(df, int(temp[3]), int(temp[4]), int(temp[5]), int(temp[6]))
        elif temp[2] == "leadingSpanBIC":
            temp_str = f"leadingSpanBIC_{int(temp[3])}_{int(temp[4])}_{int(temp[5])}_{int(temp[6])}"
            if num_one == 1:
                return Ichimoku_cloud(df, int(temp[3]), int(temp[4]), int(temp[5]), int(temp[6]))
            

    if if_index_exist(temp, [2, 3, 4]) :
        if temp[2] == "momentum"     :
            temp_str = f'momentum_{int(temp[3])}_{str(temp[4])}' 
            if num_one == 1:
                return momentum_indicator(df, int(temp[3]), str(temp[4]))



    if if_index_exist(temp, [2, 3, 4, 5, 6, 7]) :
        if temp[2] == "stochasticRSIK":
            temp_str = f'stochasticRSIK_{int(temp[3])}_{int(temp[4])}_{int(temp[5])}_{int(temp[6])}_{str(temp[7])}' 
            if num_one == 1:
                return stochastic_RSI(df, int(temp[3]), int(temp[4]), int(temp[5]), int(temp[6]), str(temp[7]))
        elif temp[2] == "stochasticRSID":
            temp_str = f'stochasticRSID_{int(temp[3])}_{int(temp[4])}_{int(temp[5])}_{int(temp[6])}_{str(temp[7])}' 
            if num_one == 1:
                return stochastic_RSI(df, int(temp[3]), int(temp[4]), int(temp[5]), int(temp[6]), str(temp[7]))
        
   

    if if_index_exist(temp, [2, 3, 4]) :
        
        # supertrend
        if temp[2] == "supertrend":
            temp_str = f"{temp[2]}_{temp[3]}_{temp[4]}"
            if num_one == 1:
                return supertrend_generator(df, atr_length= temp[3], factor=temp[4])
        
        # ATR
        if temp[2] == "atr":
            temp_str = f"atr_{int(temp[3])}_{str(temp[4])}"
            if num_one == 1:
                return atr_generator(df, int(temp[3]), str(temp[4]))
            
        if temp[2] == "roc":
            temp_str = f"roc_{int(temp[3])}_{str(temp[4])}"
            if num_one == 1:
                return rate_of_change(df, int(temp[3]), str(temp[4]))
            
        if temp[2] == "cci":
            temp_str = f"cci_{int(temp[3])}_{str(temp[4])}"
            if num_one == 1:
                return cci_indicator(df, int(temp[3]), str(temp[4]))
            
        if temp[2] == "williamsPercentR":
            temp_str = f"williamsPercentR_{int(temp[3])}_{str(temp[4])}"
            if num_one == 1:
                return williams_r(df, int(temp[3]), str(temp[4]))
            
        if temp[2] == "cmo":
            temp_str = f"cmo_{int(temp[3])}_{str(temp[4])}"
            if num_one == 1:
                return chande_momentum_oscillator(df, int(temp[3]), str(temp[4]))
    
    if if_index_exist(temp, [2, 3, 4]) :
        if temp[2] == "keltnerBasis":
            temp_str = f"keltnerBasis_{int(temp[3])}_{float(temp[4])}"
            if num_one == 1:
                return keltner_channels(df, int(temp[3]), float(temp[4]))
        if temp[2] == "keltnerUpper":
            temp_str = f"keltnerUpper_{int(temp[3])}_{float(temp[4])}"
            if num_one == 1:
                return keltner_channels(df, int(temp[3]), float(temp[4]))
        if temp[2] == "keltnerLower":
            temp_str = f"keltnerLower_{int(temp[3])}_{float(temp[4])}"
            if num_one == 1:
                return keltner_channels(df, int(temp[3]), float(temp[4]))
     


    if if_index_exist(temp, [2, 3]) :

        if temp[2] == "donchianUpper":
            temp_str = f"donchianUpper_{int(temp[3])}"
            if num_one == 1:
                return donchian_channels(df, int(temp[3]))
        elif temp[2] == "donchianLower":
            temp_str = f"donchianLower_{int(temp[3])}"
            if num_one == 1:
                return donchian_channels(df, int(temp[3]))
        elif temp[2] == "donchianMiddle":
            temp_str = f"donchianMiddle_{int(temp[3])}"
            if num_one == 1:
                return donchian_channels(df, int(temp[3]))
            
            
    if if_index_exist(temp, [2, 3]) :

        if temp[2] == "cmf":
            temp_str = f"cmf_{int(temp[3])}"
            if num_one == 1:
                return chaikin_money_flow(df, int(temp[3]))
            
            
    if if_index_exist(temp, [2]) :
        
        
        if temp[2] == "H1" or temp[2] == "H2" or temp[2] == "H3" or temp[2] == "H4" or temp[2] == "L1" or temp[2] == "L2" or temp[2] == "L3" or temp[2] == "L4":
            temp_str = temp[2]
            if num_one == 1:
                return camarilla_levels(df)
            
        if temp[2] == "CPRPP" or temp[2] == "CPRBC" or temp[2] == "CPRTC" or temp[2] == "pivotR1" or temp[2] == "pivotR2" or temp[2] == "pivotR3" or temp[2] == "pivotR4" or temp[2] == "pivotS1" or temp[2] == "pivotS2" or temp[2] == "pivotS3" or temp[2] == "pivotS4":
            temp_str = temp[2]
            if num_one == 1:
                return pivot_points_and_cpr(df)

    

    if if_index_exist(temp, [2]) :
        if temp[2] == "close" or temp[2] == "high" or temp[2] == "low" or temp[2] == "open" or temp[2] == "volume":
            temp_str = f"{temp[2]}"
            if num_one == 1:
                return df

            
    
            
    return temp,temp_str

    

#__________________________________________________________
#
# this is used to generate required date time into numbers


def convert_date_time_datetime_into_numbers(df):
    # Extract date and time from the index in a vectorized way
    df['date'] = df.index.date.astype(str)
    df['time'] = df.index.time.astype(str)
    
    # Vectorized operations to convert date and time to numbers
    df['date_number'] = df['date'].str.replace('-', '').astype(int)
    df['time_number'] = df['time'].str.replace(':', '').str.split('.').str[0].astype(int)
    df['datetime_number'] = (df['date'].str.replace('-', '') + df['time'].str.replace(':', '').str.split('.').str[0]).astype(int)

    # Drop temporary 'date' and 'time' columns
    df.drop(columns=['date', 'time'], inplace=True)
    
    return df

#__________________________________________________________
#
# this is used to generate required date time into numbers for daily

def convert_date_time_datetime_into_numbers_Daily(df):
    # Extract date and time from the index in a vectorized way
    df['date'] = df.index.date.astype(str)
    # df['time'] = df.index.time.astype(str)
    
    # Vectorized operations to convert date and time to numbers
    df['date_number'] = df['date'].str.replace('-', '').astype(int)
    # df['time_number'] = df['time'].str.replace(':', '').str.split('.').str[0].astype(int)
    # df['datetime_number'] = (df['date'].str.replace('-', '') + df['time'].str.replace(':', '').str.split('.').str[0]).astype(int)

    # Drop temporary 'date' and 'time' columns
    df.drop(columns=['date'], inplace=True)
    
    return df

# def sma_generator(df, ohlc, value):
#     df['sma'+str(value)+'_'+str(ohlc)] = 0.0
#     arr = np.zeros((len(df)))
#     for i in range(value-1,len(df)):
#         arr[i] = np.average( df.loc[df.index[i-value+1]:df.index[i] , str(ohlc)])
#     df['sma'+str(value)+'_'+str(ohlc)] = arr
#     return df



def sma_generator(df, ohlc='close', value=14):
    column_name = f'sma_{value}_{ohlc}'
    # Calculate SMA using rolling window mean
    df[column_name] = df[ohlc].rolling(window=value, min_periods=value).mean()
    
    return df

def ema_generator(df, ohlc='close', value=14):
    
    column_name = f'ema_{value}_{ohlc}'
    # Calculate EMA using the same logic as TradingView's ta.ema
    df[column_name] = df[ohlc].ewm(
        span=value,
        adjust=False,
        min_periods=0  # Starts calculation from first value
    ).mean()
    
    return df

def rsi_generator(df, ohlc='close', length=14):
    column_name = f'rsi_{length}_{ohlc}'
    
    delta = df[ohlc].diff()

    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    
    # Initialize average gains and losses
    df['avg_gain'] = np.nan
    df['avg_loss'] = np.nan
    
    # Calculate initial SMA for the first period
    df.loc[df.index[length-1], 'avg_gain'] = gain.iloc[:length].mean()
    df.loc[df.index[length-1], 'avg_loss'] = loss.iloc[:length].mean()
    
    # Calculate subsequent RMA values
    for i in range(length, len(df)):
        idx = df.index[i]
        prev_idx = df.index[i-1]
        
        df.loc[idx, 'avg_gain'] = (df.loc[prev_idx, 'avg_gain'] * (length - 1) + gain.loc[idx]) / length
        df.loc[idx, 'avg_loss'] = (df.loc[prev_idx, 'avg_loss'] * (length - 1) + loss.loc[idx]) / length
    
    # Calculate RS and RSI
    avg_gain = df['avg_gain']
    avg_loss = df['avg_loss']
    
    # Handle division by zero cases
    rs = avg_gain / avg_loss
    rs.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    df[column_name] = 100 - (100 / (1 + rs))
    
    # TradingView-specific edge cases
    df[column_name] = np.where(avg_loss == 0, 100.0, df[column_name])
    df[column_name] = np.where(avg_gain == 0, 0.0, df[column_name])
    
    # Cleanup intermediate columns
    df.drop(columns=['avg_gain', 'avg_loss'], inplace=True)
    
    return df

def bb_generator(df, length, matype, ohlc, stddev):
   
    # Calculate the Basis (Middle Band)
    if matype == 'sma':
        basis = df[ohlc].rolling(window=length).mean()
    elif matype == 'ema':
        basis = df[ohlc].ewm(span=length, adjust=False).mean()
    else:
        raise ValueError("Invalid 'matype'. Choose 'sma' or 'ema'.")

    # Calculate the standard deviation
    rolling_std = df[ohlc].rolling(window=length).std()

    # Calculate the Upper and Lower Bands
    upper_band = basis + (stddev * rolling_std)
    lower_band = basis - (stddev * rolling_std)

    # Add the columns to the DataFrame
    df[f'BBbasis_{length}_{matype}_{ohlc}_{stddev}'] = basis
    df[f'BBupper_{length}_{matype}_{ohlc}_{stddev}'] = upper_band
    df[f'BBlower_{length}_{matype}_{ohlc}_{stddev}'] = lower_band

    return df


# def calculate_macd(df, fast_period=12, slow_period=26, signal_period=9, price_column='close'):
    
#     # Calculate the short-term EMA
#     ema_fast = df[price_column].ewm(span=fast_period, adjust=False).mean()
    
#     # Calculate the long-term EMA
#     ema_slow = df[price_column].ewm(span=slow_period, adjust=False).mean()
    
#     # Calculate MACD line
#     df[f'macd_line_{fast_period}_{slow_period}_{signal_period}_{price_column}'] = ema_fast - ema_slow
    
#     # Calculate the signal line
#     df[f"signal_line_{fast_period}_{slow_period}_{signal_period}_{price_column}"] = df[f'macd_line_{fast_period}_{slow_period}_{signal_period}_{price_column}'].ewm(span=signal_period, adjust=False).mean()
    
#     # Calculate the MACD histogram
#     df[f'macd_histogram_{fast_period}_{slow_period}_{signal_period}_{price_column}'] = df[f'macd_line_{fast_period}_{slow_period}_{signal_period}_{price_column}'] - df[f"signal_line_{fast_period}_{slow_period}_{signal_period}_{price_column}"]
    
#     return df

def calculate_macd(df, fast_period=12, slow_period=26, signal_period=9, price_column='close', osc_ma_type='EMA', signal_ma_type='EMA'):
    
    # Calculate MACD line
    if osc_ma_type == 'SMA':
        fast_ma = df[price_column].rolling(window=fast_period, min_periods=fast_period).mean()
        slow_ma = df[price_column].rolling(window=slow_period, min_periods=slow_period).mean()
    else:  # EMA
        fast_ma = df[price_column].ewm(span=fast_period, adjust=False).mean()
        slow_ma = df[price_column].ewm(span=slow_period, adjust=False).mean()
    
    macd_line = fast_ma - slow_ma
    macd_line_name = f'macdLine_{fast_period}_{slow_period}_{signal_period}_{price_column}'
    df[macd_line_name] = macd_line
    
    # Calculate Signal line
    if signal_ma_type == 'SMA':
        signal_line = macd_line.rolling(window=signal_period, min_periods=signal_period).mean()
    else:  # EMA
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    
    signal_line_name = f"signalLine_{fast_period}_{slow_period}_{signal_period}_{price_column}"
    df[signal_line_name] = signal_line
    
    # Calculate Histogram
    hist_name = f'macdHistogram_{fast_period}_{slow_period}_{signal_period}_{price_column}'
    df[hist_name] = macd_line - signal_line
    
    return df



# def supertrend_generator(df, atr_length=10, factor=3.0):
#     # Define the column name dynamically
#     column_name = f'supertrend_{atr_length}_{factor}'
    
#     # Calculate the True Range (TR)
#     df['tr1'] = df['high'] - df['low']
#     df['tr2'] = abs(df['high'] - df['close'].shift(1))
#     df['tr3'] = abs(df['low'] - df['close'].shift(1))
#     df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    
#     # Calculate the Average True Range (ATR)
#     df['atr'] = df['tr'].rolling(window=atr_length).mean()
    
#     # Calculate the basic upper and lower bands
#     df['basic_upper'] = (df['high'] + df['low']) / 2 + factor * df['atr']
#     df['basic_lower'] = (df['high'] + df['low']) / 2 - factor * df['atr']
    
#     # Initialize the SuperTrend and trend columns
#     df[column_name] = 0.0  # Use the dynamic column name
#     df['in_uptrend'] = True
    
#     # Calculate SuperTrend
#     for i in range(1, len(df)):
#         if df.loc[df.index[i], 'close'] > df.loc[df.index[i-1], 'basic_upper']:
#             df.loc[df.index[i], 'in_uptrend'] = True
#         elif df.loc[df.index[i], 'close'] < df.loc[df.index[i-1], 'basic_lower']:
#             df.loc[df.index[i], 'in_uptrend'] = False
#         else:
#             df.loc[df.index[i], 'in_uptrend'] = df.loc[df.index[i-1], 'in_uptrend']
            
#             if df.loc[df.index[i], 'in_uptrend'] and df.loc[df.index[i], 'basic_lower'] < df.loc[df.index[i-1], 'basic_lower']:
#                 df.loc[df.index[i], 'basic_lower'] = df.loc[df.index[i-1], 'basic_lower']
            
#             if not df.loc[df.index[i], 'in_uptrend'] and df.loc[df.index[i], 'basic_upper'] > df.loc[df.index[i-1], 'basic_upper']:
#                 df.loc[df.index[i], 'basic_upper'] = df.loc[df.index[i-1], 'basic_upper']
        
#         if df.loc[df.index[i], 'in_uptrend']:
#             df.loc[df.index[i], column_name] = df.loc[df.index[i], 'basic_lower']
#         else:
#             df.loc[df.index[i], column_name] = df.loc[df.index[i], 'basic_upper']
    
#     # Drop intermediate columns
#     df.drop(columns=['tr1', 'tr2', 'tr3', 'tr', 'atr', 'basic_upper', 'basic_lower', 'in_uptrend'], inplace=True)
    
#     return df

# def supertrend_generator(df, atr_length=10, factor=3.0):
#     """
#     Adds a SuperTrend indicator column (name: supertrend_{atr_length}_{factor}) to a copy of df.
#     Only requires columns 'high', 'low', 'close'.
#     """
#     df = df.copy()
#     column_name = f'supertrend_{atr_length}_{factor}'

#     # True Range (TR)
#     df['tr1'] = df['high'] - df['low']
#     df['tr2'] = (df['high'] - df['close'].shift(1)).abs()
#     df['tr3'] = (df['low'] - df['close'].shift(1)).abs()
#     df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)

#     # Average True Range (ATR)
#     df['atr'] = df['tr'].rolling(window=atr_length, min_periods=1).mean()

#     # Basic Bands
#     hl2 = (df['high'] + df['low']) / 2
#     df['basic_upper'] = hl2 + factor * df['atr']
#     df['basic_lower'] = hl2 - factor * df['atr']

#     # Prepare arrays for speed
#     close = df['close'].values
#     basic_upper = df['basic_upper'].values
#     basic_lower = df['basic_lower'].values

#     supertrend = np.full_like(close, np.nan, dtype=float)
#     in_uptrend = np.ones_like(close, dtype=bool)

#     # First row: by default trend True (as in your code)
#     for i in range(1, len(df)):
#         if close[i] > basic_upper[i-1]:
#             in_uptrend[i] = True
#         elif close[i] < basic_lower[i-1]:
#             in_uptrend[i] = False
#         else:
#             in_uptrend[i] = in_uptrend[i-1]
#             if in_uptrend[i] and basic_lower[i] < basic_lower[i-1]:
#                 basic_lower[i] = basic_lower[i-1]
#             if not in_uptrend[i] and basic_upper[i] > basic_upper[i-1]:
#                 basic_upper[i] = basic_upper[i-1]

#         # Set supertrend value
#         supertrend[i] = basic_lower[i] if in_uptrend[i] else basic_upper[i]

#     # Assign outputs
#     df[column_name] = supertrend

#     # Drop intermediate columns
#     df.drop(columns=['tr1', 'tr2', 'tr3', 'tr', 'atr', 'basic_upper', 'basic_lower'], inplace=True)

#     return df

def supertrend_generator(df, atr_length=10, factor=3.0):
    """
    Adds a SuperTrend indicator column (name: supertrend_{atr_length}_{factor}) to a copy of df.
    Only requires columns 'high', 'low', 'close'.
    """
    df = df.copy()
    column_name = f'supertrend_{atr_length}_{factor}'

    supertrend, direction = ta.supertrend(high= df["high"], low=df["low"], close= df["close"], period=atr_length, multiplier=factor)
    # Assign outputs
    df[column_name] = supertrend

    # Drop intermediate columns
    

    return df



def camarilla_levels(df):
    
    # Ensure sorted by date
    # df = df.sort_index()
    
    # Get previous day's values
    df['prev_high'] = df['high'].shift(1)
    df['prev_low'] = df['low'].shift(1)
    df['prev_close'] = df['close'].shift(1)
    
    # Calculate previous day's range
    df['prev_range'] = df['prev_high'] - df['prev_low']
    
    # Calculate Camarilla levels
    df['H1'] = df['prev_close'] + (df['prev_range'] * 1.1 / 12)
    df['H2'] = df['prev_close'] + (df['prev_range'] * 1.1 / 6)
    df['H3'] = df['prev_close'] + (df['prev_range'] * 1.1 / 4)
    df['H4'] = df['prev_close'] + (df['prev_range'] * 1.1 / 2)
    
    df['L1'] = df['prev_close'] - (df['prev_range'] * 1.1 / 12)
    df['L2'] = df['prev_close'] - (df['prev_range'] * 1.1 / 6)
    df['L3'] = df['prev_close'] - (df['prev_range'] * 1.1 / 4)
    df['L4'] = df['prev_close'] - (df['prev_range'] * 1.1 / 2)
    
    # Cleanup intermediate columns
    df.drop(columns=['prev_high', 'prev_low', 'prev_close', 'prev_range'], inplace=True)
    
    return df

def pivot_points_and_cpr(df):
    
    # Ensure sorted by date
    # df = df.sort_index()
    
    # Get previous day's values
    df['prev_high'] = df['high'].shift(1)
    df['prev_low'] = df['low'].shift(1)
    df['prev_close'] = df['close'].shift(1)
    
    # Calculate Pivot Points (PP)
    df['CPRPP'] = (df['prev_high'] + df['prev_low'] + df['prev_close']) / 3
    
    # Calculate CPR Levels
    df['CPRBC'] = (df['prev_high'] + df['prev_low']) / 2  # Central Pivot (BC)
    df['CPRTC'] = 2 * df['CPRPP'] - df['CPRBC']         # Central Target (TC)
    
    # Calculate Support/Resistance Levels
    prev_range = df['prev_high'] - df['prev_low']
    
    df['pivotR1'] = 2 * df['CPRPP'] - df['prev_low']
    df['pivotR2'] = df['CPRPP'] + prev_range
    df['pivotR3'] = df['prev_high'] + 2 * (df['CPRPP'] - df['prev_low'])
    df['pivotR4'] = df['pivotR3'] + prev_range  # New R4 level
    
    df['pivotS1'] = 2 * df['CPRPP'] - df['prev_high']
    df['pivotS2'] = df['CPRPP'] - prev_range
    df['pivotS3'] = df['prev_low'] - 2 * (df['prev_high'] - df['CPRPP'])
    df['pivotS4'] = df['pivotS3'] - prev_range  # New S4 level
    
    # Cleanup intermediate columns
    df.drop(columns=['prev_high', 'prev_low', 'prev_close'], inplace=True)
    
    return df



def DMI_generator(df, ADX_Smoothing=14, DI_Length=14):
    
    # Calculate True Range
    df['prev_close'] = df['close'].shift(1)
    df['tr1'] = df['high'] - df['low']
    df['tr2'] = abs(df['high'] - df['prev_close'])
    df['tr3'] = abs(df['low'] - df['prev_close'])
    df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    
    # Calculate Directional Movements
    df['up'] = df['high'].diff()
    df['down'] = -df['low'].diff()
    df['plusDM'] = df.apply(lambda x: x['up'] if x['up'] > x['down'] and x['up'] > 0 else 0, axis=1)
    df['minusDM'] = df.apply(lambda x: x['down'] if x['down'] > x['up'] and x['down'] > 0 else 0, axis=1)
    
    # Calculate RMA (Wilder's Moving Average)
    def rma(series, length):
        return series.ewm(alpha=1/length, min_periods=length, adjust=False).mean()
    
    # Calculate Smoothed Values
    df['trur'] = rma(df['tr'], DI_Length)
    df['plus'] = 100 * rma(df['plusDM'], DI_Length) / df['trur']
    df['minus'] = 100 * rma(df['minusDM'], DI_Length) / df['trur']
    
    # Calculate ADX components
    df['sum'] = df['plus'] + df['minus']
    df['diff'] = abs(df['plus'] - df['minus'])
    df['dx'] = 100 * (df['diff'] / df['sum'].replace(0, 1))  # Handle division by zero
    
    # Calculate final ADX
    df[f'ADX_{ADX_Smoothing}_{DI_Length}'] = rma(df['dx'], ADX_Smoothing)
    df[f'DIplus_{ADX_Smoothing}_{DI_Length}'] = df['plus']
    df[f'DIminus_{ADX_Smoothing}_{DI_Length}'] = df['minus']
    
    # Cleanup intermediate columns
    df.drop(columns=['prev_close', 'tr1', 'tr2', 'tr3', 'tr', 'up', 'down', 
                     'plusDM', 'minusDM', 'trur', 'plus', 'minus', 'sum', 'diff', 'dx'], 
            inplace=True)
    
    return df


# df = atr_generator(df.copy(), smoothing="RMA")
def atr_generator(df, length=14, smoothing="RMA"):
    
    column_name = f'atr_{length}_{smoothing}'
    
    # Calculate True Range (TR)
    prev_close = df['close'].shift(1)
    tr1 = df['high'] - df['low']
    tr2 = (df['high'] - prev_close).abs()
    tr3 = (df['low'] - prev_close).abs()
    df['tr'] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # Define smoothing functions
    def rma(series):
        return series.ewm(alpha=1/length, min_periods=length, adjust=False).mean()
    
    def wma(series):
        weights = pd.Series(range(1, length+1))
        return series.rolling(window=length).apply(
            lambda x: (x * weights).sum() / weights.sum(), raw=True
        )
    
    # Calculate ATR based on smoothing method
    if smoothing == "RMA":
        df[column_name] = rma(df['tr'])
    elif smoothing == "SMA":
        df[column_name] = df['tr'].rolling(window=length, min_periods=length).mean()
    elif smoothing == "EMA":
        df[column_name] = df['tr'].ewm(span=length, adjust=False).mean()
    elif smoothing == "WMA":
        df[column_name] = wma(df['tr'])
    else:
        raise ValueError("Invalid smoothing method. Use RMA, SMA, EMA, or WMA")
    
    # Cleanup intermediate columns
    df.drop(columns=['tr'], inplace=True)
    
    return df


# df = vwap_generator(df, anchor_period="Session", source="hlc3")
def vwap_generator(df, anchor_period="Session", source="hlc3"):
    
    # Validate input
    required_columns = ['high', 'low', 'close', 'volume']
    if not all(col in df.columns for col in required_columns):
        raise ValueError("DataFrame must contain OHLCV columns")
    
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame must have a DatetimeIndex")

    # Calculate source price
    source = source.lower()
    if source == "hlc3":
        df['_source_price'] = (df['high'] + df['low'] + df['close']) / 3
    elif source == "close":
        df['_source_price'] = df['close']
    elif source == "hl2":
        df['_source_price'] = (df['high'] + df['low']) / 2
    elif source == "open":
        df['_source_price'] = df['open']
    else:
        raise ValueError(f"Unsupported source: {source}")

    # Create anchor groups
    anchor_period = anchor_period.lower()
    if anchor_period == "session":
        groups = df.index.date
    elif anchor_period == "week":
        groups = df.index.isocalendar().year.astype(str) + "-" + df.index.isocalendar().week.astype(str)
    elif anchor_period == "month":
        groups = df.index.to_period('M').astype(str)
    elif anchor_period == "year":
        groups = df.index.year.astype(str)
    else:
        raise ValueError(f"Unsupported anchor period: {anchor_period}")

    # Calculate cumulative sums within each anchor period
    df['_cum_price_vol'] = df.groupby(groups).apply(
        lambda x: (x['_source_price'] * x['volume']).cumsum()
    ).values
    
    df['_cum_vol'] = df.groupby(groups)['volume'].cumsum()

    # Calculate VWAP
    column_name = f'vwap_{anchor_period}_{source}'
    df[column_name] = df['_cum_price_vol'] / df['_cum_vol']

    # Cleanup intermediate columns
    df.drop(columns=['_source_price', '_cum_price_vol', '_cum_vol'], inplace=True)
    
    return df



# df = parabolicSAR_generator(df)
def parabolicSAR_generator(df, start=0.02, increment=0.02, max_value=0.2):
   
    column_name = f'parabolicSAR_{start}_{increment}_{max_value}'
    
    # Initialize lists to store values
    high = df['high'].values
    low = df['low'].values
    sar = []
    trend = []  # False = Downtrend, True = Uptrend
    
    if len(df) == 0:
        return df
    
    # Initial values (start in downtrend)
    initial_trend = False
    sar.append(high[0])
    trend.append(initial_trend)
    ep = low[0]  # Extreme Point (low for downtrend)
    af = start
    
    for i in range(1, len(df)):
        prev_sar = sar[-1]
        current_high = high[i]
        current_low = low[i]
        
        if not trend[-1]:  # Downtrend
            # Calculate preliminary SAR
            current_sar = prev_sar - af * (prev_sar - ep)
            
            # Check for reversal
            if current_high > current_sar:
                # Reverse to uptrend
                new_sar = ep
                new_trend = True
                new_ep = current_high
                new_af = start
            else:
                new_sar = current_sar
                new_trend = False
                
                # Update EP and AF if new low
                if current_low < ep:
                    new_ep = current_low
                    new_af = min(af + increment, max_value)
                else:
                    new_ep = ep
                    new_af = af
                
                # Adjust SAR to highest of previous two highs
                new_sar = max(new_sar, high[i-1], current_high)
        else:  # Uptrend
            # Calculate preliminary SAR
            current_sar = prev_sar + af * (ep - prev_sar)
            
            # Check for reversal
            if current_low < current_sar:
                # Reverse to downtrend
                new_sar = ep
                new_trend = False
                new_ep = current_low
                new_af = start
            else:
                new_sar = current_sar
                new_trend = True
                
                # Update EP and AF if new high
                if current_high > ep:
                    new_ep = current_high
                    new_af = min(af + increment, max_value)
                else:
                    new_ep = ep
                    new_af = af
                
                # Adjust SAR to lowest of previous two lows
                new_sar = min(new_sar, low[i-1], current_low)
        
        # Append values for this period
        sar.append(new_sar)
        trend.append(new_trend)
        ep = new_ep
        af = new_af
    
    df[column_name] = sar
    return df


def stochastic_RSI(df, k=3, d=3, RSI_length=14, stochastic_length=14, RSI_sourse="close"):
    column_name_K = f"stochasticRSIK_{k}_{d}_{RSI_length}_{stochastic_length}_{RSI_sourse}"
    column_name_D = f"stochasticRSID_{k}_{d}_{RSI_length}_{stochastic_length}_{RSI_sourse}"

    # Step 1: Calculate RSI
    delta = df[RSI_sourse].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(RSI_length).mean()
    avg_loss = loss.rolling(RSI_length).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # Step 2: Stochastic of RSI
    rsi_min = rsi.rolling(stochastic_length).min()
    rsi_max = rsi.rolling(stochastic_length).max()

    stoch_rsi = ((rsi - rsi_min) / (rsi_max - rsi_min)) * 100

    # Step 3: Smooth K and D
    K = stoch_rsi.rolling(k).mean()
    D = K.rolling(d).mean()

    # Save to DataFrame
    df[column_name_K] = K
    df[column_name_D] = D

    return df


def Ichimoku_cloud(df, CONVERSION_LINE_LENGTH=9, BASE_LINE_LENGTH=26, LEADING_SPAN_B_LENGTH=52, LAGGING_SPAN=26):
    column_conversion_line = f"conversionLineIC_{CONVERSION_LINE_LENGTH}_{BASE_LINE_LENGTH}_{LEADING_SPAN_B_LENGTH}_{LAGGING_SPAN}"
    column_base_line = f"baseLineIC_{CONVERSION_LINE_LENGTH}_{BASE_LINE_LENGTH}_{LEADING_SPAN_B_LENGTH}_{LAGGING_SPAN}"
    column_lagging_line = f"laggingLineIC_{CONVERSION_LINE_LENGTH}_{BASE_LINE_LENGTH}_{LEADING_SPAN_B_LENGTH}_{LAGGING_SPAN}"
    column_leading_span_a = f"leadingSpanAIC_{CONVERSION_LINE_LENGTH}_{BASE_LINE_LENGTH}_{LEADING_SPAN_B_LENGTH}_{LAGGING_SPAN}"
    column_leading_span_b = f"leadingSpanBIC_{CONVERSION_LINE_LENGTH}_{BASE_LINE_LENGTH}_{LEADING_SPAN_B_LENGTH}_{LAGGING_SPAN}"

    # Conversion Line (Tenkan-sen): (9-period high + 9-period low) / 2
    high_conv = df['high'].rolling(window=CONVERSION_LINE_LENGTH).max()
    low_conv = df['low'].rolling(window=CONVERSION_LINE_LENGTH).min()
    df[column_conversion_line] = (high_conv + low_conv) / 2

    # Base Line (Kijun-sen): (26-period high + 26-period low) / 2
    high_base = df['high'].rolling(window=BASE_LINE_LENGTH).max()
    low_base = df['low'].rolling(window=BASE_LINE_LENGTH).min()
    df[column_base_line] = (high_base + low_base) / 2

    # Leading Span A (Senkou Span A): (Conversion Line + Base Line) / 2 shifted forward
    df[column_leading_span_a] = ((df[column_conversion_line] + df[column_base_line]) / 2).shift(LAGGING_SPAN)

    # Leading Span B (Senkou Span B): (52-period high + 52-period low) / 2 shifted forward
    high_span_b = df['high'].rolling(window=LEADING_SPAN_B_LENGTH).max()
    low_span_b = df['low'].rolling(window=LEADING_SPAN_B_LENGTH).min()
    df[column_leading_span_b] = ((high_span_b + low_span_b) / 2).shift(LAGGING_SPAN)

    # Lagging Span (Chikou Span): closing price shifted backward
    df[column_lagging_line] = df['close'].shift(-LAGGING_SPAN)

    return df

#_______________________________________________________________

def momentum_indicator(df, period=10, source = "close"):
    df[f"momentum_{period}_{source}"] = df[source] - df[source].shift(period)
    return df

def rate_of_change(df, period=9, source="close"):
    if source not in df.columns:
        raise ValueError(f"Invalid source '{source}'. Must be one of: {list(df.columns)}")

    roc_col = f"roc_{period}_{source}"
    df[roc_col] = ((df[source] - df[source].shift(period)) / df[source].shift(period)) * 100
    return df


def cci_indicator(df, period=20,  source="hlc"):
    constant=0.015

    if source == "hlc":
        tp = (df['high'] + df['low'] + df['close']) / 3
    elif source == "hl":
        tp = (df['high'] + df['low'] ) / 2
    elif source == "ohlc":
        tp = (df['high'] + df['low'] + df['close'] + df['open']) / 4
    elif source == "hlcc":
        tp = (df['high'] + df['low'] + df['close'] + df['close']) / 4
    elif source == "open":
        tp = df['open']
    elif source == "high":
        tp = df['high']
    elif source == "low":
        tp = df['low']
    elif source == "close":
        tp = df['close']

    sma_tp = tp.rolling(window=period).mean()
    mean_dev = tp.rolling(window=period).apply(lambda x: (abs(x - x.mean())).mean(), raw=True)
    df[f"cci_{period}_{source}"] = (tp - sma_tp) / (constant * mean_dev)
    return df


def williams_r(df, period=14, source="close"):
    highest_high = df['high'].rolling(window=period).max()
    lowest_low = df['low'].rolling(window=period).min()
    
    if source not in df.columns:
        raise ValueError(f"Invalid source '{source}'. Must be one of: {list(df.columns)}")
    
    df[f"williamsPercentR_{period}_{source}"] = ((highest_high - df[source]) / (highest_high - lowest_low)) * -100
    return df


def chande_momentum_oscillator(df, period=14, source="close"):
    delta = df[source].diff()
    up = delta.where(delta > 0, 0).rolling(window=period).sum()
    down = -delta.where(delta < 0, 0).rolling(window=period).sum()
    df[f"cmo_{period}_{source}"] = 100 * ((up - down) / (up + down))
    return df


# getting wrong answer
def on_balance_volume_with_smoothing(df, ma_type="None", ma_length=14, bb_mult=2.0):
    if not {'close', 'volume'}.issubset(df.columns):
        raise ValueError("DataFrame must contain 'close' and 'volume' columns.")

    # Step 1: Calculate OBV
    direction = np.sign(df['close'].diff()).fillna(0)
    volume = df['volume'].fillna(0)
    df["obv"] = (direction * volume).cumsum()

    # Step 2: Optional MA smoothing
    obv_ma_col = f"obv_{ma_type.lower()}_{ma_length}" if ma_type != "None" else None
    if ma_type == "SMA":
        df[obv_ma_col] = df['obv'].rolling(ma_length).mean()
    elif ma_type == "EMA":
        df[obv_ma_col] = df['obv'].ewm(span=ma_length, adjust=False).mean()
    elif ma_type == "SMMA" or ma_type == "RMA":
        df[obv_ma_col] = df['obv'].ewm(alpha=1/ma_length, adjust=False).mean()
    elif ma_type == "WMA":
        weights = np.arange(1, ma_length + 1)
        df[obv_ma_col] = df['obv'].rolling(ma_length).apply(
            lambda x: np.dot(x, weights)/weights.sum(), raw=True)
    elif ma_type == "VWMA":
        df[obv_ma_col] = (
            (df['obv'] * df['volume']).rolling(ma_length).sum() /
            df['volume'].rolling(ma_length).sum()
        )
    elif ma_type == "SMA + BB":
        sma = df['obv'].rolling(ma_length).mean()
        std = df['obv'].rolling(ma_length).std()
        df[obv_ma_col] = sma
        df[f"{obv_ma_col}_bb_upper"] = sma + bb_mult * std
        df[f"{obv_ma_col}_bb_lower"] = sma - bb_mult * std
    elif ma_type != "None":
        raise ValueError(f"Unsupported MA type: {ma_type}")

    return df

# getting wrong answer
def accumulation_distribution(df):
    ad_col = "accumdist"

    # Prevent divide-by-zero and apply condition logic from Pine Script
    cond = ((df['close'] == df['high']) & (df['close'] == df['low'])) | (df['high'] == df['low'])
    mfm = np.where(cond, 0, ((2 * df['close'] - df['low'] - df['high']) / (df['high'] - df['low'])))
    mfm = np.nan_to_num(mfm)  # ensure NaNs or infs are replaced with 0

    mfv = mfm * df['volume']
    df[ad_col] = mfv.cumsum()

    return df


def chaikin_money_flow(df, period=20):
    cmf_col = f"cmf_{period}"

    mfm = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
    mfm = mfm.replace([float('inf'), -float('inf')], 0).fillna(0)
    mfv = mfm * df['volume']

    cmf = mfv.rolling(window=period).sum() / df['volume'].rolling(window=period).sum()
    df[cmf_col] = cmf

    return df

def donchian_channels(df, period=20):
    upper_col = f"donchianUpper_{period}"
    lower_col = f"donchianLower_{period}"
    mid_col = f"donchianMiddle_{period}"

    df[upper_col] = df['high'].rolling(window=period).max()
    df[lower_col] = df['low'].rolling(window=period).min()
    df[mid_col] = (df[upper_col] + df[lower_col]) / 2

    return df


def keltner_channels(df, period=20, multiplier=2.0 ):
    basis_col = f"keltnerBasis_{period}_{multiplier}"
    upper_col = f"keltnerUpper_{period}_{multiplier}"
    lower_col = f"keltnerLower_{period}_{multiplier}"

    # Calculate EMA of close
    df[basis_col] = df['close'].ewm(span=period, adjust=False).mean()

    # True Range
    high_low = df['high'] - df['low']
    high_close_prev = (df['high'] - df['close'].shift()).abs()
    low_close_prev = (df['low'] - df['close'].shift()).abs()
    tr = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)

    atr = tr.rolling(window=period).mean()  # Simple Moving Average ATR like in TradingView

    df[upper_col] = df[basis_col] + multiplier * atr
    df[lower_col] = df[basis_col] - multiplier * atr

    return df

# getting wrong answer
def zigzag_enhanced(df, depth=10, deviation=5.0, 
                    price_change_type="absolute",  # or "percent" absolute
                    extend_to_last_bar=True,
                    record_volume=True,
                    record_price=True):
    highs = df['high'].values
    lows = df['low'].values
    volumes = df['volume'].values
    closes = df['close'].values

    zz_vals = [np.nan] * len(df)
    zz_changes = [np.nan] * len(df)
    zz_volume = [np.nan] * len(df)

    last_pivot_idx = None
    last_pivot_value = None

    for i in range(depth, len(df) - depth):
        high_window = highs[i - depth:i + 1]
        low_window = lows[i - depth:i + 1]
        current_high = highs[i]
        current_low = lows[i]

        is_pivot_high = current_high == high_window.max()
        is_pivot_low = current_low == low_window.min()

        if is_pivot_high:
            if last_pivot_value is None or current_high >= last_pivot_value * (1 + deviation / 100):
                zz_vals[i] = current_high
                if record_price:
                    if last_pivot_value is not None:
                        change = current_high - last_pivot_value
                        if price_change_type == "percent":
                            change = (change / last_pivot_value) * 100
                        zz_changes[i] = change
                if record_volume and last_pivot_idx is not None:
                    zz_volume[i] = volumes[last_pivot_idx + 1:i + 1].sum()
                last_pivot_idx = i
                last_pivot_value = current_high

        elif is_pivot_low:
            if last_pivot_value is None or current_low <= last_pivot_value * (1 - deviation / 100):
                zz_vals[i] = current_low
                if record_price:
                    if last_pivot_value is not None:
                        change = current_low - last_pivot_value
                        if price_change_type == "percent":
                            change = (change / last_pivot_value) * 100
                        zz_changes[i] = change
                if record_volume and last_pivot_idx is not None:
                    zz_volume[i] = volumes[last_pivot_idx + 1:i + 1].sum()
                last_pivot_idx = i
                last_pivot_value = current_low

    # Extend to last bar (hold last pivot value if enabled)
    if extend_to_last_bar and last_pivot_idx is not None:
        zz_vals[-1] = last_pivot_value

    df[f'zigzag_{depth}_{deviation}'] = zz_vals
    if record_price:
        df[f'zz_change_{price_change_type}'] = zz_changes
    if record_volume:
        df[f'zz_cum_volume'] = zz_volume

    return df
