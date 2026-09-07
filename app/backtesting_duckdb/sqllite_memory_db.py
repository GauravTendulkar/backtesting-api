import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import math
from datetime import datetime, timedelta

def calculate_fifo_pnl(df):
    df = df.sort_values(["symbol", "datetime"]).copy()

    results = []
    open_positions = {}   # key = symbol, value = list of open lots

    for _, row in df.iterrows():
        symbol = row["symbol"]
        qty = row["quantity"]
        price = row["price"]

        # initialize symbol bucket
        if symbol not in open_positions:
            open_positions[symbol] = []

        # ENTRY
        if row["entryexit"] == "entry":
            open_positions[symbol].append({
                "qty": qty,
                "price": price,
                "datetime": row["datetime"],
                "label": row["label"],
                "buysell": row["buysell"]
            })

        # EXIT
        elif row["entryexit"] == "exit":
            exit_qty = abs(qty)

            while exit_qty > 0 and open_positions[symbol]:
                entry = open_positions[symbol][0]

                matched_qty = min(entry["qty"], exit_qty)

                pnl = (price - entry["price"]) * matched_qty

                results.append({
                    "stock": symbol,
                    "buysell": entry["buysell"],
                    "entry_date": entry["datetime"].split()[0],
                    "entry_time": entry["datetime"].split()[1],
                    "entry": entry["price"],
                    "exit_date": row["datetime"].split()[0],
                    "exit_time": row["datetime"].split()[1],
                    "exit": price,
                    "quantity": matched_qty,
                    "pnl": pnl,
                    "entry_label": entry["label"],
                    "exit_label": row["label"]
                })

                entry["qty"] -= matched_qty
                exit_qty -= matched_qty

                if entry["qty"] == 0:
                    open_positions[symbol].pop(0)

    return pd.DataFrame(results)


class TrackingDB:
    def __init__(self ):

        self.conn_sqlite = sqlite3.connect(":memory:")
        self.cursor = self.conn_sqlite.cursor() 

        self.cache = {}

        self.first_trade_cache = {}

        # Create tracking table
        self.cursor.execute("""
        CREATE TABLE tracking (
            datetime TIMESTAMP NOT NULL,
            symbol TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            buysell TEXT NOT NULL,
            entryexit TEXT NOT NULL,
            label TEXT
        )
        """)

        self.conn_sqlite.commit()
    def init_table(self):
        self.cursor.execute("""
        DELETE FROM tracking;
        
        """)
        self.conn_sqlite.commit()
        self.cursor.execute("""
        
        VACUUM;
        """)

    def vacuum_database(self):
        self.cursor.execute("""
        
        VACUUM;
        """)


    def get_quantity_remaining_for_stock(self, stock):
        query = f""" 
SELECT sum(quantity) FROM tracking
WHERE symbol == '{stock}'
GROUP BY symbol
""" 
        try:
            # if self.get_cache(query) == math.inf:
                # print("query", self.get_cache(query) , query)
#                 self.cursor.execute(f""" 
# SELECT quantity FROM tracking
# WHERE symbol == '{stock}'

# """ )
                # print(self.cursor.fetchall())
            # print("get_cache", self.get_cache(query))
            return self.get_cache(query)
        
        except:
            
            self.cursor.execute(query)

            result = self.cursor.fetchall()
            if len(result) == 0:
                self.set_cache(query, 0)
                # print("return 0", 0)
                return 0
            self.set_cache(query, result[0][0])
            # print("result[0][0]", result[0][0])
            return result[0][0]
        # try:
        #     result = result[0][0]
        # except :
            
        #     print(query)
        #     print("Error result",result)
        # return result

    def set_cache(self, key : str, value):
        if key not in self.cache:
            self.cache[key] = value
    
    def get_cache(self, key: str):
        return self.cache[key]
    
    def delete_all_cache(self):
        self.cache = {}


# ENTRY **************    
    def insert_entry(self, datetime, symbol, price, quantity, buysell_setup, entryexit= "entry", label=""):
        if buysell_setup == "buy":
            quantity = abs(quantity)
        elif buysell_setup == "sell":
            quantity = -abs(quantity)
        # print("quantity", quantity)
        if price == math.inf or price == -math.inf or quantity == math.inf or quantity == -math.inf:
            return
            # print("quantity", quantity)
        if quantity != 0 :
        # if True :
            query = """
    INSERT INTO tracking (datetime, symbol, price, quantity, buysell,entryexit, label)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """     
            open_p_quantity = self.open_position_quantity(symbol)
            if open_p_quantity == 0:
                self.first_trade_cache = {
                    "datetime" : datetime,
                    "symbol"  : symbol,
                    "price" : price,
                    "label" : label,

                }
            
            self.cursor.execute(query, (datetime, symbol, price, quantity, buysell_setup, entryexit, label))
            self.conn_sqlite.commit()
        self.delete_all_cache()
# EXIT **************
    def insert_exit(self, datetime, symbol, price, quantity, buysell_setup, entryexit= "exit", label=""):
        if buysell_setup == "buy":
            quantity = -abs(quantity)
        elif buysell_setup == "sell":
            quantity = abs(quantity)
        query = """
INSERT INTO tracking (datetime, symbol, price, quantity, buysell,entryexit, label)
VALUES (?, ?, ?, ?, ?, ?, ?)
"""
        open_p_quantity = self.open_position_quantity(symbol)

        # print("open_p_quantity", open_p_quantity, quantity, open_p_quantity - quantity)
        if (open_p_quantity + quantity) < 0 and buysell_setup == "buy" :
            return None
        if (-open_p_quantity - quantity) > 0 and buysell_setup == "sell" :
            return None
    

        self.cursor.execute(query, (datetime, symbol, price, quantity, buysell_setup, entryexit, label))
        self.conn_sqlite.commit()
        self.delete_all_cache()

        open_p_quantity = self.open_position_quantity(symbol)
        if open_p_quantity == 0:
            # remove cache
            self.first_trade_cache = {}
        
    def exit_percentage_to_quantity(self, percentage, symbol):
        if percentage < 0 or percentage > 100:
            return None
        remaining_quantity = self.get_quantity_remaining_for_stock(symbol)
        # print("remaining_quantity", remaining_quantity)
        final_quantity_to_exit = 0
        try:
            final_quantity_to_exit = round(abs(remaining_quantity) * (percentage/100))
        except :
            # print("remaining_quantity", remaining_quantity)
            pass
        
        return final_quantity_to_exit

    def exit_percentage_quantity(self, datetime, symbol, price, label, quantity, buysell_setup = "buy"):
        # if percentage < 0 or percentage > 100:
        #     return None
        # remaining_quantity = self.get_quantity_remaining_for_stock(symbol)
        # final_quantity_to_exit = round(abs(remaining_quantity) * (percentage/100))
        final_quantity_to_exit = quantity

        if final_quantity_to_exit <= 0 :
            return None
        # if remaining_quantity < 0 :
            
        #     self.insert_exit( datetime, symbol, price, final_quantity_to_exit, buysell_setup= "sell",  label=label)
            
        # elif remaining_quantity > 0 :
        #     self.insert_exit( datetime, symbol, price, final_quantity_to_exit, buysell_setup= "buy",  label=label)
        elif final_quantity_to_exit == 0 :
            return None
        self.insert_exit( datetime, symbol, price, final_quantity_to_exit, buysell_setup= buysell_setup,  label=label)
        
        

        
    def create_result_table(self):
        df = pd.read_sql_query("SELECT * FROM tracking", self.conn_sqlite)
        df.to_csv("w_sqlite_table.csv")
        # return df
        pnl_df = calculate_fifo_pnl(df)
        return pnl_df
    

    def previous_position(self,  stock, mode = "count", date: str = "2025-01-01"):
        if mode not in ["value", "count", "quantity"]:
            print(["value", "count", "quantity"])
            return None
        query = ""
        if mode == "count":
        # if mode == "quantity":
            query = f"""
    SELECT 
        COUNT(symbol) AS entry_count,
        DATE(datetime) AS trade_date
    FROM tracking
    WHERE 
        symbol = '{stock}'
        AND entryexit = 'entry'
        AND DATE(datetime) = '{date}'
    GROUP BY symbol, DATE(datetime)
    """
        elif mode == "quantity":
            query = f"""
    SELECT 
        SUM(quantity) AS entry_count --,
        --DATE(datetime) AS trade_date
    FROM tracking
    WHERE 
        symbol = '{stock}'
        AND entryexit = 'entry'
        --AND DATE(datetime) = '{date}'
    GROUP BY symbol, DATE(datetime)
    """
            
            query = f"""
    SELECT 
        SUM(quantity) AS entry_count 
        
    FROM tracking
    WHERE 
        symbol = '{stock}'
        AND entryexit = 'entry'
		AND entryexit = 'exit'
        
    GROUP BY symbol
    """
            query = f"""
SELECT 
    SUM(quantity) AS entry_count
FROM tracking
WHERE symbol = '{stock}'
GROUP BY symbol
"""
            pass
        elif mode == "value":
            query = f"""
    SELECT 
        SUM(quantity * price) AS entry_count,
        DATE(datetime) AS trade_date
    FROM tracking
    WHERE 
        symbol = '{stock}'
        AND entryexit = 'entry'
        AND DATE(datetime) = '{date}'
    GROUP BY symbol, DATE(datetime)
    """

        try:
            # print(self.get_cache(query))
            return self.get_cache(query)
        except:
            
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            # if date == "2018-11-16":
                # print(result, len(result))
                # print("result", result)
            if len(result) == 0:
                self.set_cache(query, 0)
                # print(0)
                return 0
            self.set_cache(query, result[0][0])
            # print(result[0][0])
            return result[0][0]
    # previous entry price 
    def open_entry_price(self, symbol):
        query = f""" 
SELECT price
    FROM tracking
WHERE
    entryexit = 'entry'
    AND symbol = '{symbol}'
ORDER BY datetime DESC
LIMIT 1;
"""
        
        try:
            return self.get_cache(query)
        except:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            
            if len(result) == 0:
                self.set_cache(query, None)
                return None
            self.set_cache(query, result[0][0])
            return result[0][0]

            
#     def open_position_quantity(self, stock, label="", entryexit="entry"):
    
#         query = f"""
# SELECT 
#     SUM(quantity) AS entry_count
# FROM tracking
# WHERE symbol = '{stock}'
# AND datetime >= "{self.first_trade_cache["datetime"]}"
# GROUP BY symbol
# """
#         try:
            
#             return self.get_cache(query)
#         except:
            
#             self.cursor.execute(query)
#             result = self.cursor.fetchall()
#             if len(result) == 0:
#                 self.set_cache(query, 0)
#                 return 0
#             self.set_cache(query, result[0][0])
#             return result[0][0]
       
    def open_position_quantity(self, stock, label="", entryexit="all"):
        
        if self.first_trade_cache:

            label_query = ""
            if label != "":
                label_query = f' AND label = "{label}"'
            if entryexit == "all":
                entryexit = ""
            else:
                entryexit = f"""AND entryexit = "{entryexit}" """


            query = f"""
            SELECT COALESCE(SUM(quantity), 0) AS position_quantity
            FROM tracking
            WHERE
                symbol = "{stock}"
                {entryexit}
                AND datetime >= "{self.first_trade_cache["datetime"]}"
                {label_query}
            """

            try:
                # print("result c", self.get_cache(query))
                return self.get_cache(query)

            except:
                self.cursor.execute(query)

                result = self.cursor.fetchone()
                
                quantity = result[0] if result else 0
                # print("result", result, quantity)
                # print(query)
                # print(self.first_trade_cache)
                self.set_cache(query, quantity)
                return quantity
        # print(self.first_trade_cache)
        # print("result 0", 0)
        return 0

#     def open_position_value(self, stock, label="", entryexit="entry"):
#         open_quantity = self.open_position_quantity(stock)

#         query = f"""
#     SELECT 
#         quantity , price
        
#     FROM tracking
#     WHERE 
#         symbol = '{stock}'
#         AND entryexit = 'entry'
# """       
#         self.cursor.execute(query)
#         result = self.cursor.fetchall()
#         try:
            
#             return self.get_cache(query)
#         except:

#         # print(result)\
#             if open_quantity != 0 and len(result) > 0:
#                 pass
#                 # return (result, open_quantity)
#                 # print(open_quantity)
#                 if open_quantity > 0 :
#                     total_value = 0
#                     for i in range(len(result) -1 , -1 , -1):
#                         if open_quantity == 0:
#                             break
#                         if open_quantity <= result[i][0]:
#                             total_value =  total_value + open_quantity * result[i][1]
#                             open_quantity -= open_quantity
#                         else:
#                             total_value =  total_value + result[i][0] * result[i][1]
#                             open_quantity -= result[i][0]
#                     # print("total_value", total_value)
#                     self.set_cache(query, total_value)
#                     return total_value
#                 elif open_quantity < 0 :
#                     total_value = 0
#                     for i in range(len(result) -1 , -1 , -1):
#                         if open_quantity == 0:
#                             break
#                         if open_quantity >= result[i][0]:
#                             total_value =  total_value + open_quantity * result[i][1]
                            
#                         else:
#                             total_value =  total_value + result[i][0] * result[i][1]
#                             open_quantity -= result[i][0]
#                     # print("total_value", total_value)
#                     self.set_cache(query, total_value)
#                     return total_value
#             self.set_cache(query, 0)
#             return 0

    def open_position_value(self, stock, label="", entryexit="entry"):

        if self.first_trade_cache:

            open_quantity = self.open_position_quantity(
                stock,
                label=label,
                entryexit=entryexit
            )

            label_query = ""
            if label != "":
                label_query = f' AND label = "{label}"'
            if entryexit == "all":
                entryexit = ""
            else:
                entryexit = f"""AND entryexit = "{entryexit}" """

            query = f"""
            SELECT
                quantity,
                price
            FROM tracking
            WHERE
                symbol = "{stock}"
                {entryexit}
                AND datetime >= "{self.first_trade_cache["datetime"]}"
                {label_query}
            ORDER BY datetime
            """

            try:
                return self.get_cache(query)

            except:
                self.cursor.execute(query)
                result = self.cursor.fetchall()

                if open_quantity != 0 and result:

                    remaining_quantity = open_quantity
                    total_value = 0

                    # Calculate from newest entries backwards (LIFO)
                    for quantity, price in reversed(result):

                        if remaining_quantity == 0:
                            break

                        if remaining_quantity > 0:

                            qty = min(remaining_quantity, quantity)
                            total_value += qty * price
                            remaining_quantity -= qty

                        else:  # Short position

                            qty = min(abs(remaining_quantity), abs(quantity))
                            total_value += qty * price
                            remaining_quantity += qty

                    self.set_cache(query, total_value)
                    return total_value

                self.set_cache(query, 0)
                return 0

        return 0


#     def open_position_avg_price(self, stock, label="", entryexit="entry"):
#         open_quantity = self.open_position_quantity(stock)
#         temp_open_quantity = open_quantity
#         query = f"""
#     SELECT 
#         quantity , price
        
#     FROM tracking
#     WHERE 
#         symbol = '{stock}'
#         AND entryexit = 'entry'
# """       
#         self.cursor.execute(query)
#         result = self.cursor.fetchall()
#         try:
            
#             return self.get_cache(query)
#         except:

#         # print(result)\
#             if open_quantity != 0 and len(result) > 0:
#                 pass
#                 # return (result, open_quantity)
#                 # print(open_quantity)
#                 if temp_open_quantity > 0 :
#                     total_value = 0
#                     for i in range(len(result) -1 , -1 , -1):
#                         if temp_open_quantity == 0:
#                             break
#                         if temp_open_quantity <= result[i][0]:
#                             total_value =  total_value + temp_open_quantity * result[i][1]
#                             temp_open_quantity -= temp_open_quantity
#                         else:
#                             total_value =  total_value + result[i][0] * result[i][1]
#                             temp_open_quantity -= result[i][0]
#                     # print("total_value", total_value)
#                     self.set_cache(query, total_value/abs(open_quantity))
#                     return total_value
#                 elif temp_open_quantity < 0 :
#                     total_value = 0
#                     for i in range(len(result) -1 , -1 , -1):
#                         if temp_open_quantity == 0:
#                             break
#                         if temp_open_quantity >= result[i][0]:
#                             total_value =  total_value + temp_open_quantity * result[i][1]
                            
#                         else:
#                             total_value =  total_value + result[i][0] * result[i][1]
#                             temp_open_quantity -= result[i][0]
#                     # print("total_value", total_value)
#                     self.set_cache(query, total_value/abs(open_quantity))
#                     return total_value
#             self.set_cache(query, 0)
#             return 0

    def open_position_avg_price(self, stock, label="", entryexit="entry"):

        if self.first_trade_cache:

            open_quantity = self.open_position_quantity(
                stock,
                label=label,
                entryexit=entryexit
            )

            label_query = ""
            if label != "":
                label_query = f' AND label = "{label}"'
                
            if entryexit == "all":
                entryexit = ""
            else:
                entryexit = f"""AND entryexit = "{entryexit}" """

            query = f"""
            SELECT
                quantity,
                price
            FROM tracking
            WHERE
                symbol = "{stock}"
                {entryexit}
                AND datetime >= "{self.first_trade_cache["datetime"]}"
                {label_query}
            ORDER BY datetime
            """

            try:
                return self.get_cache(query)

            except:
                self.cursor.execute(query)
                result = self.cursor.fetchall()

                if open_quantity != 0 and result:

                    remaining_quantity = open_quantity
                    total_value = 0

                    # Calculate from newest entries backwards (LIFO)
                    for quantity, price in reversed(result):

                        if remaining_quantity == 0:
                            break

                        if remaining_quantity > 0:

                            qty = min(remaining_quantity, quantity)
                            total_value += qty * price
                            remaining_quantity -= qty

                        else:  # Short position

                            qty = min(abs(remaining_quantity), abs(quantity))
                            total_value += qty * price
                            remaining_quantity += qty

                    avg_price = total_value / abs(open_quantity)

                    self.set_cache(query, avg_price)
                    return avg_price

                self.set_cache(query, 0)
                return 0

        return 0



    def open_entry_count(self, stock, label="", entryexit="entry"):
        # print("inside open_entry_count")
        if self.first_trade_cache:

            label_query = ""
            if label != "":
                label_query = f' AND label = "{label}"'
            if entryexit == "all":
                entryexit = ""
            else:
                entryexit = f"""AND entryexit = "{entryexit}" """

            query = f"""
            SELECT COUNT(*) AS entry_count
            FROM tracking
            WHERE
                symbol = "{stock}"
                {entryexit}
                AND datetime >= "{self.first_trade_cache["datetime"]}"
                {label_query}
            """
            # print("query", query)
            try:
                return self.get_cache(query)

            except:
                self.cursor.execute(query)

                result = self.cursor.fetchone()
                count = result[0] if result else 0

                self.set_cache(query, count)
                return count
        return 0
    

    def open_trade(self, mode, stock, label="", entryexit="entry"):
#         print(
#     "CALL",
#     f"stock={stock}",
#     f"entryexit={entryexit}",
#     f"label={label}"
# )
        # print("mode", mode)
        if mode == "count":
            # print("pre open_trade")
            temp = self.open_entry_count(stock, label = label, entryexit = entryexit)
            # print("open_trade", mode, temp)
            return temp
        elif mode == "avg_price":
            return self.open_position_avg_price(stock, label = label, entryexit = entryexit)
        elif mode == "value":
            return self.open_position_value(stock, label = label, entryexit = entryexit)
        elif mode == "quantity":
            t = self.open_position_quantity(stock, label = label, entryexit = entryexit)
            # print("************ quantity" ,t)
            return t
        
    
    def first_entry(self):
        try:
            return self.first_trade_cache["price"]
        except:
            return None


#     def number_of_trades(self,  stock, mode = "count", date: str = "2025-01-01", label = "", entryexit = "all", tf = "Daily"):
#         if mode not in ["value", "count", "quantity"]:
#             return None
#         if tf not in ["Daily", "Weekly", "Monthly", "Yearly"]:
#             return None
#         if entryexit not in ["all", "entry", "exit"]:
#             return None
#         query = ""
#         if mode == "count":
        
#             query = f"""
#     SELECT 
#         COUNT(symbol) AS entry_count,
#         DATE(datetime) AS trade_date
#     FROM tracking
#     WHERE 
#         symbol = '{stock}'
#         AND entryexit = 'entry'
#         AND DATE(datetime) = '{date}'
#     GROUP BY symbol, DATE(datetime)
#     """
#         elif mode == "quantity":
#             query = f"""
#     SELECT 
#         SUM(quantity) AS entry_count --,
#         --DATE(datetime) AS trade_date
#     FROM tracking
#     WHERE 
#         symbol = '{stock}'
#         AND entryexit = 'entry'
#         --AND DATE(datetime) = '{date}'
#     GROUP BY symbol, DATE(datetime)
#     """
            
#             query = f"""
#     SELECT 
#         SUM(quantity) AS entry_count 
        
#     FROM tracking
#     WHERE 
#         symbol = '{stock}'
#         AND entryexit = 'entry'
# 		AND entryexit = 'exit'
        
#     GROUP BY symbol
#     """
#             query = f"""
# SELECT 
#     SUM(quantity) AS entry_count
# FROM tracking
# WHERE symbol = '{stock}'
# GROUP BY symbol
# """
#             pass
#         elif mode == "value":
#             query = f"""
#     SELECT 
#         SUM(quantity * price) AS entry_count,
#         DATE(datetime) AS trade_date
#     FROM tracking
#     WHERE 
#         symbol = '{stock}'
#         AND entryexit = 'entry'
#         AND DATE(datetime) = '{date}'
#     GROUP BY symbol, DATE(datetime)
#     """

#         try:
#             # print(self.get_cache(query))
#             return self.get_cache(query)
#         except:
            
#             self.cursor.execute(query)
#             result = self.cursor.fetchall()
#             if date == "2018-11-16":
#                 print(result, len(result))
#                 print("result", result)
#             if len(result) == 0:
#                 self.set_cache(query, 0)
#                 # print(0)
#                 return 0
#             self.set_cache(query, result[0][0])
#             # print(result[0][0])
#             return result[0][0]



#     def number_of_trades(
#     self,
#     stock,
#     mode="count",
#     date="2025-01-01",
#     label="",
#     entryexit="all",
#     tf="Daily",
# ):
#         if mode not in ["count", "quantity", "value"]:
#             return None

#         if tf not in ["Daily", "Weekly", "Monthly", "Yearly"]:
#             return None

#         select_map = {
#             "count": "COUNT(*)",
#             "quantity": "COALESCE(SUM(quantity), 0)",
#             "value": "COALESCE(SUM(quantity * price), 0)",
#         }

#         conditions = ["symbol = ?"]
#         params = [stock]

#         # entry / exit filter
#         if entryexit != "all":
#             conditions.append("entryexit = ?")
#             params.append(entryexit)

#         # label filter
#         if label:
#             conditions.append("label = ?")
#             params.append(label)

#         # date filter
#         if date:
#             if tf == "Daily":
#                 conditions.append("DATE(datetime) = ?")
#                 params.append(date)

#             elif tf == "Weekly":
#                 conditions.append("strftime('%Y-%W', datetime) = strftime('%Y-%W', ?)")
#                 params.append(date)

#             elif tf == "Monthly":
#                 conditions.append("strftime('%Y-%m', datetime) = strftime('%Y-%m', ?)")
#                 params.append(date)

#             elif tf == "Yearly":
#                 conditions.append("strftime('%Y', datetime) = strftime('%Y', ?)")
#                 params.append(date)

#         query = f"""
#         SELECT {select_map[mode]} AS result
#         FROM tracking
#         WHERE {' AND '.join(conditions)}
#         """
#         # print("query", query)
#         try:
#             return self.get_cache((query, tuple(params)))

#         except Exception:
#             self.cursor.execute(query, params)

#             result = self.cursor.fetchone()
#             value = result[0] if result and result[0] is not None else 0
#             print("value", value, (query, tuple(params)) )
#             self.set_cache((query, tuple(params)), value)

#             return value


    


    def number_of_trades(
        self,
        stock: str,
        mode: str = "count",
        date: str | None = None,
        label: str = "",
        entryexit: str = "all",
        tf: str = "Daily",
    ):
        """
        mode:
            - count
            - quantity
            - value

        tf:
            - Daily
            - Weekly
            - Monthly
            - Yearly
        """

        if mode not in {"count", "quantity", "value"}:
            return None

        if tf not in {"Daily", "Weekly", "Monthly", "Yearly"}:
            return None

        select_map = {
            "count": "COUNT(*)",
            "quantity": "COALESCE(SUM(quantity), 0)",
            "value": "COALESCE(SUM(quantity * price), 0)",
        }

        conditions = ["symbol = ?"]
        params = [stock]

        # Optional filters
        if entryexit != "all":
            conditions.append("entryexit = ?")
            params.append(entryexit)

        if label:
            conditions.append("label = ?")
            params.append(label)

        # Cache period key
        period_key = "all"

        if date:
            dt = datetime.fromisoformat(date)

            if tf == "Daily":
                start = dt.date()
                end = start + timedelta(days=1)

                period_key = start.strftime("%Y-%m-%d")

            elif tf == "Weekly":
                # ISO week (Monday -> Monday)
                start = (dt - timedelta(days=dt.weekday())).date()
                end = start + timedelta(days=7)

                iso_year, iso_week, _ = dt.isocalendar()
                period_key = f"{iso_year}-W{iso_week:02d}"

            elif tf == "Monthly":
                start = dt.replace(day=1).date()

                if start.month == 12:
                    end = start.replace(year=start.year + 1, month=1)
                else:
                    end = start.replace(month=start.month + 1)

                period_key = start.strftime("%Y-%m")

            elif tf == "Yearly":
                start = dt.replace(month=1, day=1).date()
                end = start.replace(year=start.year + 1)

                period_key = start.strftime("%Y")

            # Range queries use indexes better than DATE()/strftime()
            conditions.append("datetime >= ?")
            params.append(start.isoformat())

            conditions.append("datetime < ?")
            params.append(end.isoformat())

        query = f"""
        SELECT {select_map[mode]} AS result
        FROM tracking
        WHERE {' AND '.join(conditions)}
        """

        cache_key = (
            stock,
            mode,
            tf,
            period_key,
            label or "all",
            entryexit,
        )

        try:
            return self.get_cache(cache_key)

        except KeyError:
            self.cursor.execute(query, params)

            result = self.cursor.fetchone()
            value = result[0] if result and result[0] is not None else 0
            # print("period_key", period_key, value)
            self.set_cache(cache_key, value)

            return value

    def latest_position_datetime(self, stock, label="", entryexit="all"):

        label_query = ""
        if label != "":
            label_query = f' AND label = "{label}"'

        if entryexit == "all":
            entryexit = ""
        else:
            entryexit = f'AND entryexit = "{entryexit}"'

        query = f"""
        SELECT datetime
        FROM tracking
        WHERE
            symbol = "{stock}"
            {entryexit}
            {label_query}
        ORDER BY datetime DESC
        LIMIT 1
        """

        try:
            return self.get_cache(query)
        except:
            self.cursor.execute(query)

            result = self.cursor.fetchone()

            latest_datetime = result[0] if result else None

            self.set_cache(query, latest_datetime)
        return latest_datetime

    # def add_datetime(self, stock, datetime, option, mode, label, days, hours, minutes ):
    #     if option == "first_entry":
    #         self.first_entry()
    #         # add days, hours, minutes to self.first_entry() and return in yyyymmddhhmm format which is int  
    #         pass
    #     elif option == "previous_trade":
    #         self.latest_position_datetime(self, stock, label=label, entryexit = mode)
    #         # add days, hours, minutes to self.latest_position_datetime(self, stock, label=label, entryexit = mode) and return in yyyymmddhhmm format which is int  
    #         pass

    

    def add_datetime(self, stock, option, mode, label, days, hours, minutes):

        key = str((stock, option, mode, label, days, hours, minutes))
        try:
            return self.get_cache(key)
        except:
            pass

        if option == "first_entry":
            # base_datetime = self.first_entry()
            # print("run add_datetime" )
            base_datetime = self.first_trade_cache["datetime"]
            # print("base_datetime", base_datetime)

        elif option == "previous_trade":
            base_datetime = self.latest_position_datetime(
                stock,
                label=label,
                entryexit=mode
            )
            # print("base_previous_trade", base_datetime)

        else:
            self.set_cache(key, None)
            return None

        # No matching datetime found
        if base_datetime is None:
            # print("run add_datetime 1" )
            self.set_cache(key, None)
            return None
        
        # Convert YYYYMMDDHHMM -> datetime object
        base_datetime = str(base_datetime)
        if len(base_datetime) > 16:
            base_datetime = base_datetime[0:16]
        # print("base_datetime", base_datetime)
        # dt = datetime.strptime(base_datetime, "%Y%m%d%H%M")
        dt = datetime.strptime(base_datetime, "%Y-%m-%d %H:%M")
        # print("dt", dt)
        # print("run add_datetime 2" )
        # Add the offset
        dt += timedelta(
            days=int(days),
            hours=int(hours),
            minutes=int(minutes)
        )

        # Return as YYYYMMDDHHMM integer
        # print("********************add_datetime", int(dt.strftime("%Y%m%d%H%M")))
        self.set_cache(key, int(dt.strftime("%Y%m%d%H%M")))
        return int(dt.strftime("%Y%m%d%H%M"))

    def add_time(self, datetime, option, mode, label, hours, minutes):
        pass

    def datetime(self, date_int, time_int):
        if time_int == 0:
            # print("datetime",date_int * 10000)
            return date_int * 10000
        # print("datetime",date_int * 10000 + time_int)
        return date_int * 10000 + time_int


# obj = TrackingDB()
