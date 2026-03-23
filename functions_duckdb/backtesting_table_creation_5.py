from functions import indicators

TIMEFRAME_CONVERSION = {
    1: '1min', 2: '2min', 3: '3min', 5: '5min', 10: '10min', 15: '15min',
    30: '30min', 60: '1h', 120: '2h', 180: '3h', 240: '4h',
    "Daily": "Daily", "Weekly": "Weekly", "Monthly": "Monthly", "Yearly": "Yearly"
}

class BacktestingTable:
    def __init__(self, stock_list=[]):
        self.stock_list = stock_list
        self.unique_stock = stock_list
        self.indicator_requests = [] # List of (timeframe, column_name, alias)
        self.smallest_tf = None

    def accumulate_request_data(self, req_data):
        """
        Parses req_data to identify which columns are needed from which timeframes.
        """
        # Simplified parser logic based on your existing convert_req_data_to_list
        # For brevity, assume this populates self.indicator_requests with unique needs
        # e.g., (15, 'rsi_14_close', '15_15_0_rsi_14_close')
        pass

    def _generate_stock_query(self, stock, start_date, end_date):
        """
        Generates the optimized query for a single stock.
        """
        base_tf_str = TIMEFRAME_CONVERSION[self.smallest_tf]
        base_table = f"{stock}_{base_tf_str}"
        
        # 1. Identify indicators that belong to the BASE timeframe (No Join Needed)
        base_cols = [
            f'"{col}" AS "{self.smallest_tf}_{alias}"' 
            for tf, col, alias in self.indicator_requests if tf == self.smallest_tf
        ]
        
        # 2. Identify indicators that belong to HIGHER timeframes (Join Needed)
        higher_tfs = sorted(list(set(tf for tf, c, a in self.indicator_requests if tf != self.smallest_tf)))
        
        ctes = []
        joins = []
        select_aliases = base_cols.copy()

        for tf in higher_tfs:
            tf_str = TIMEFRAME_CONVERSION[tf]
            tf_table_name = f"ref_{tf_str}"
            tf_source = f"{stock}_{tf_str}"
            
            # Create CTE for the higher timeframe
            tf_cols = [f'"{col}" AS "{self.smallest_tf}_{alias}"' 
                       for t, col, alias in self.indicator_requests if t == tf]
            
            # Handle Interval logic for joins
            interval_logic = f' + INTERVAL {tf} minute' if isinstance(tf, int) else ""
            
            cte = f"""
            "{tf_table_name}" AS (
                SELECT DATETIME, 
                       DATETIME {interval_logic} AS "end_time",
                       {", ".join(tf_cols)}
                FROM "{tf_source}"
                WHERE DATETIME BETWEEN '{start_date}' AND '{end_date}'
            )"""
            ctes.append(cte)
            
            # Create Join Condition
            if isinstance(tf, str): # Higher order like Daily/Weekly
                join = f'LEFT JOIN "{tf_table_name}" ON date_trunc(\'{tf.lower()}\', OHLC.DATETIME) = date_trunc(\'{tf.lower()}\', "{tf_table_name}".DATETIME)'
            else: # Int minutes
                join = f'LEFT JOIN "{tf_table_name}" ON (OHLC.DATETIME >= "{tf_table_name}".DATETIME AND OHLC.DATETIME < "{tf_table_name}".end_time)'
            
            joins.append(join)
            # Add these aliases to the final SELECT
            select_aliases.extend([f'"{self.smallest_tf}_{alias}"' for t, c, alias in self.indicator_requests if t == tf])

        # Construct the final string
        cte_section = "WITH " + ",\n".join(ctes) + "," if ctes else "WITH "
        
        query = f"""
        {cte_section}
        OHLC AS (
            SELECT DATETIME, '{stock}' AS symbol, close,
                   (extract('hour' FROM DATETIME) * 100 + extract('minute' FROM DATETIME)) AS time_int,
                   {", ".join(base_cols) if base_cols else "close"}
            FROM "{base_table}"
            WHERE DATETIME BETWEEN '{start_date}' AND '{end_date}'
        )
        SELECT OHLC.*, {", ".join([f'"{tf_table_name}".*' for tf_table_name in [f"ref_{TIMEFRAME_CONVERSION[t]}" for t in higher_tfs]]) if higher_tfs else ""}
        FROM OHLC
        {" ".join(joins)}
        """
        return query

    def final_query(self, start_date, end_date):
        stock_queries = []
        for stock in self.unique_stock:
            # Wrap each stock query in a CTE to keep the UNION ALL clean
            stock_queries.append(f'"{stock}_final" AS ({self._generate_stock_query(stock, start_date, end_date)})')
            
        full_query = "WITH " + ",\n".join(stock_queries)
        union_all = "\nUNION ALL\n".join([f'SELECT * FROM "{stock}_final"' for stock in self.unique_stock])
        
        return f"{full_query}\n{union_all} ORDER BY symbol, DATETIME"