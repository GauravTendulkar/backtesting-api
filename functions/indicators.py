import pandas as pd
import numpy as np
# import pandas_ta as ta
# import time
from datetime import date
# import threading
# import multiprocessing
# from pathlib import Path

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
            temp_str = f"{temp[2]}{temp[4]}_{temp[3]}"
            if num_one == 1:
                return sma_generator(df, temp[3], temp[4])
        # EMA
        if temp[2] == "ema":
            temp_str = f"{temp[2]}{temp[4]}_{temp[3]}"
            if num_one == 1:
                return ema_generator(df, temp[3], temp[4])
        # RSI
        if temp[2] == "rsi":
            temp_str = f"{temp[2]}_{temp[4]}_{temp[3]}"
            if num_one == 1:
                return rsi_generator(df, temp[3], temp[4])
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
    

    if if_index_exist(temp, [2, 3, 4]) :
        
        # supertrend
        if temp[2] == "supertrend":
            temp_str = f"{temp[2]}_{temp[3]}_{temp[4]}"
            if num_one == 1:
                return supertrend_generator(df, atr_length= temp[3], factor=temp[4])
            
    if if_index_exist(temp, [2]) :
        
        # supertrend
        if temp[2] == "H1" or temp[2] == "H2" or temp[2] == "H3" or temp[2] == "H4" or temp[2] == "L1" or temp[2] == "L2" or temp[2] == "L3" or temp[2] == "L4":
            temp_str = temp[2]
            if num_one == 1:
                return camarilla_levels(df)

    

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
    column_name = f'sma{value}_{ohlc}'
    # Calculate SMA using rolling window mean
    df[column_name] = df[ohlc].rolling(window=value, min_periods=value).mean()
    
    return df

def ema_generator(df, ohlc='close', value=14):
    
    column_name = f'ema{value}_{ohlc}'
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



def supertrend_generator(df, atr_length=10, factor=3.0):
    # Define the column name dynamically
    column_name = f'supertrend_{atr_length}_{factor}'
    
    # Calculate the True Range (TR)
    df['tr1'] = df['high'] - df['low']
    df['tr2'] = abs(df['high'] - df['close'].shift(1))
    df['tr3'] = abs(df['low'] - df['close'].shift(1))
    df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    
    # Calculate the Average True Range (ATR)
    df['atr'] = df['tr'].rolling(window=atr_length).mean()
    
    # Calculate the basic upper and lower bands
    df['basic_upper'] = (df['high'] + df['low']) / 2 + factor * df['atr']
    df['basic_lower'] = (df['high'] + df['low']) / 2 - factor * df['atr']
    
    # Initialize the SuperTrend and trend columns
    df[column_name] = 0.0  # Use the dynamic column name
    df['in_uptrend'] = True
    
    # Calculate SuperTrend
    for i in range(1, len(df)):
        if df.loc[df.index[i], 'close'] > df.loc[df.index[i-1], 'basic_upper']:
            df.loc[df.index[i], 'in_uptrend'] = True
        elif df.loc[df.index[i], 'close'] < df.loc[df.index[i-1], 'basic_lower']:
            df.loc[df.index[i], 'in_uptrend'] = False
        else:
            df.loc[df.index[i], 'in_uptrend'] = df.loc[df.index[i-1], 'in_uptrend']
            
            if df.loc[df.index[i], 'in_uptrend'] and df.loc[df.index[i], 'basic_lower'] < df.loc[df.index[i-1], 'basic_lower']:
                df.loc[df.index[i], 'basic_lower'] = df.loc[df.index[i-1], 'basic_lower']
            
            if not df.loc[df.index[i], 'in_uptrend'] and df.loc[df.index[i], 'basic_upper'] > df.loc[df.index[i-1], 'basic_upper']:
                df.loc[df.index[i], 'basic_upper'] = df.loc[df.index[i-1], 'basic_upper']
        
        if df.loc[df.index[i], 'in_uptrend']:
            df.loc[df.index[i], column_name] = df.loc[df.index[i], 'basic_lower']
        else:
            df.loc[df.index[i], column_name] = df.loc[df.index[i], 'basic_upper']
    
    # Drop intermediate columns
    df.drop(columns=['tr1', 'tr2', 'tr3', 'tr', 'atr', 'basic_upper', 'basic_lower', 'in_uptrend'], inplace=True)
    
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
    df['CPR_PP'] = (df['prev_high'] + df['prev_low'] + df['prev_close']) / 3
    
    # Calculate CPR Levels
    df['CPR_BC'] = (df['prev_high'] + df['prev_low']) / 2  # Central Pivot (BC)
    df['CPR_TC'] = 2 * df['CPR_PP'] - df['CPR_BC']         # Central Target (TC)
    
    # Calculate Support/Resistance Levels
    prev_range = df['prev_high'] - df['prev_low']
    
    df['pivot_R1'] = 2 * df['CPR_PP'] - df['prev_low']
    df['pivot_R2'] = df['CPR_PP'] + prev_range
    df['pivot_R3'] = df['prev_high'] + 2 * (df['CPR_PP'] - df['prev_low'])
    df['pivot_R4'] = df['pivot_R3'] + prev_range  # New R4 level
    
    df['pivot_S1'] = 2 * df['CPR_PP'] - df['prev_high']
    df['pivot_S2'] = df['CPR_PP'] - prev_range
    df['pivot_S3'] = df['prev_low'] - 2 * (df['prev_high'] - df['CPR_PP'])
    df['pivot_S4'] = df['pivot_S3'] - prev_range  # New S4 level
    
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