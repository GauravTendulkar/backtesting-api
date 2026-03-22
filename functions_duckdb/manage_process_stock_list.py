import json
import os
import random
import sqlite3
from datetime import datetime
import time


ASSIGNMENT_FILE = "w_db_assignments.json"



class ManageProcessStockList:
    def __init__(self, stock_list = [], no_of_process = 4):
        self.no_of_process = no_of_process
        self.stock_list = stock_list

        self.conn_sqlite = sqlite3.connect("w_db_assignments.sqlite")
        self.cursor = self.conn_sqlite.cursor()

        self.cache = {}
        # self.cache_stock_porcess_id_relation = {}
        self.CACHE_EXPIRY = 2 * 60 * 60 

        # Create tracking table
        try:
            self.cursor.execute("""
            CREATE TABLE tracking (
                datetime TIMESTAMP NOT NULL,
                stock TEXT NOT NULL
                
            )
            """)

            self.conn_sqlite.commit()
        except :
            pass


    def get_cached(self, key):
        """Return cached value if valid, else None"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            # check expiry
            if time.time() - timestamp < self.CACHE_EXPIRY:
                return value
            else:
                del self.cache[key]  # expired
        return None

    def set_cached(self, key, value):
        """Store value in cache with timestamp"""
        self.cache[key] = (value, time.time())

    def insert_stock_list(self, stock_list):
        current_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data = [(current_dt, stock) for stock in stock_list]

        query = """
            INSERT INTO tracking (datetime, stock)
            VALUES (?, ?)
        """

        self.cursor.executemany(query, data)
        self.conn_sqlite.commit()

    def get_most_used_stocks(self):
        result = self.cursor.execute(""" 
SELECT stock,
       COUNT(*) AS trade_count
FROM tracking
WHERE datetime >= datetime('now', '-2 hours')
GROUP BY stock
ORDER BY trade_count DESC;
""" )
        temp = []
        for i in result:
            temp.append(i[0])
        return temp

        
    def manage_db_shards(self):
        
        assignments = {}
        # 1. Load existing state or initialize empty
        if os.path.exists(ASSIGNMENT_FILE):
            with open(ASSIGNMENT_FILE, 'r') as f:
                assignments = json.load(f)
            if len(assignments.keys()) != self.no_of_process:
                assignments = {}
        else:
            # print("assignments = {}")
            assignments = {}
        #  assigning 1st time
        if assignments == {}:
            process_id = 0
            for stock in self.stock_list:
                process_id += 1
                # print("process_id", process_id)
                if process_id not in assignments:

                    assignments[process_id] = []
                    
                assignments[process_id].append(stock)
                if process_id == self.no_of_process:
                    process_id = 0
            with open(ASSIGNMENT_FILE, 'w') as f:
                json.dump(assignments, f, indent=4)
            return assignments
        else:

            result = self.get_most_used_stocks()
    # list(result)
            # ass = self.manage_db_shards()
            ass = assignments

            adjustment_stock_process = {}
            for stock in result:
                for index, key in enumerate(ass):
                    if stock in ass[key]:
                        if key not in adjustment_stock_process:
                            adjustment_stock_process[key] = []
                        adjustment_stock_process[key].append(stock)
            # for i in adjustment_stock_process:
            #     print(i, adjustment_stock_process[i])          

            def minimal_balance(d, main_process_list):
                keys = list(d.keys())
                
                if not keys:
                    return main_process_list
                
                # Count total & compute target
                total = sum(len(v) for v in d.values())
                n = len(keys)
                
                target_low = total // n
                target_high = target_low + 1

                # Step 1: Collect extra items from large lists (pop from END)
                extra_items = []
                for k in keys:
                    while len(d[k]) > target_high:
                        pop_element = d[k].pop()
                        main_process_list[k].pop()  # mirrors d[k].pop() — removes from end
                        extra_items.append(pop_element)

                # Step 2: Fill small lists up to target_high (to distribute remainders)
                e_idx = 0
                for k in keys:
                    while len(d[k]) < target_high and e_idx < len(extra_items):
                        main_process_list[k].append(extra_items[e_idx])
                        d[k].append(extra_items[e_idx])
                        e_idx += 1

                return main_process_list


            balanced = minimal_balance(adjustment_stock_process, ass)
            # balanced
            with open(ASSIGNMENT_FILE, 'w') as f:
                json.dump(balanced, f, indent=4)
            
            return balanced
        
    

    def stock_key_process_id_value(self, stock_id_list : list= []):
        
        cache_key = "cache_stock_process_id_relation"
        cached = self.get_cached(cache_key)
        # print("cached+++++++++++++++++++++++++++++", cached, cached is not None)
        temp = {}
        if cached is not None:
            
            for stock in stock_id_list:
                if cached[stock] not in temp:
                    temp[cached[stock]] = []
                temp[cached[stock]].append(stock)
            # print("Loaded from cache")
            return temp
        

        # code to run for cache
        cache_stock_porcess_id_relation = {}
        result = self.manage_db_shards()
        for index, item in enumerate(result):
            for stock in result[item]:
                cache_stock_porcess_id_relation[stock] = item
        ## end
        # return self.cache_stock_process_id_relation

        self.set_cached(cache_key, cache_stock_porcess_id_relation)
        cached = cache_stock_porcess_id_relation
        for stock in stock_id_list:
            if cached[stock] not in temp:
                temp[cached[stock]] = []
            temp[cached[stock]].append(stock)
        return temp



