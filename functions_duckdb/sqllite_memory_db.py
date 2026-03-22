import sqlite3
import pandas as pd


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
            return self.get_cache(query)
        except:
            
            self.cursor.execute(query)

            result = self.cursor.fetchall()
            if len(result) == 0:
                self.set_cache(query, 0)
                return 0
            self.set_cache(query, result[0][0])
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


    
    def insert_entry(self, datetime, symbol, price, quantity, buysell_setup, entryexit= "entry", label=""):
        if buysell_setup == "buy":
            quantity = abs(quantity)
        elif buysell_setup == "sell":
            quantity = -abs(quantity)
        query = """
INSERT INTO tracking (datetime, symbol, price, quantity, buysell,entryexit, label)
VALUES (?, ?, ?, ?, ?, ?, ?)
"""
        self.cursor.execute(query, (datetime, symbol, price, quantity, buysell_setup, entryexit, label))
        self.conn_sqlite.commit()
        self.delete_all_cache()

    def insert_exit(self, datetime, symbol, price, quantity, buysell_setup, entryexit= "exit", label=""):
        if buysell_setup == "buy":
            quantity = -abs(quantity)
        elif buysell_setup == "sell":
            quantity = abs(quantity)
        query = """
INSERT INTO tracking (datetime, symbol, price, quantity, buysell,entryexit, label)
VALUES (?, ?, ?, ?, ?, ?, ?)
"""
        self.cursor.execute(query, (datetime, symbol, price, quantity, buysell_setup, entryexit, label))
        self.conn_sqlite.commit()
        self.delete_all_cache()
        


    def exit_percentage_quantity(self, datetime, symbol, price, label, percentage):
        if percentage < 0 or percentage > 100:
            return None
        remaining_quantity = self.get_quantity_remaining_for_stock(symbol)
        final_quantity_to_exit = round(abs(remaining_quantity) * (percentage/100))
       
        if final_quantity_to_exit <= 0 :
            return None
        if remaining_quantity < 0 :
            
            self.insert_exit( datetime, symbol, price, final_quantity_to_exit, buysell_setup= "sell",  label=label)
            
        elif remaining_quantity > 0 :
            self.insert_exit( datetime, symbol, price, final_quantity_to_exit, buysell_setup= "buy",  label=label)
        elif remaining_quantity == 0 :
            return None

        
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
        SUM(quantity) AS entry_count,
        DATE(datetime) AS trade_date
    FROM tracking
    WHERE 
        symbol = '{stock}'
        AND entryexit = 'entry'
        AND DATE(datetime) = '{date}'
    GROUP BY symbol, DATE(datetime)
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
            return self.get_cache(query)
        except:
            
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            # print(result, len(result))
            if len(result) == 0:
                self.set_cache(query, 0)
                return 0
            self.set_cache(query, result[0][0])
            return result[0][0]

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

            
        

       

    


# obj = TrackingDB()
