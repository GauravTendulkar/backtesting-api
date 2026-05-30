from ..database.mongodb.repositories import stock_list_collection, social_user_collection
from pydantic import BaseModel
import time

# structure

# stock_list_item = {
#   "stock_id": "hiabsabxj",

#   "current": {
#     "symbol": "PFC",
#     "company_name": "Power Finance Corporation Ltd",
#     "valid_from": "2025-01-01T09:30:00"
#   },

#   "history": [
#     {
#       "symbol": "PFCOLD",
#       "company_name": "Power Finance Corp",
#       "valid_from": "2020-01-01T00:00:00",
#       "valid_to": "2025-01-01T09:30:00"
#     }
#   ],

#   "is_active": True,
#   "updated_at": "2025-01-01T09:30:00"
# }





class StockListManager :
    def __init__(self):
        # cache format:
        # { key: { "value": ..., "expiry": timestamp } }
        self._cache = {}

    # 🔥 SET CACHE
    def set_cache(self, key, value, ttl_seconds: int):
        self._cache[key] = {
            "value": value,
            "expiry": time.time() + ttl_seconds
        }

    # 🔥 GET CACHE
    def get_cache(self, key):
        data = self._cache.get(key)

        if not data:
            return None

        # check expiry
        if time.time() > data["expiry"]:
            # remove expired
            del self._cache[key]
            return None

        return data["value"]

    # 🔥 OPTIONAL: CLEAR CACHE
    def clear_cache(self, key=None):
        if key:
            self._cache.pop(key, None)
        else:
            self._cache.clear()

    # 🚀 YOUR FUNCTION WITH CACHE
    

    # def direct_cache(self, key : str, function ):
    #     result = self.get_cache( key)

    #     if result == None :
    #         result = function()
    #         self.set_cache(key, result, ttl_seconds = 60*5)
    #         return result
        
    #     return result

# stock list crud
    def insert_one_stock(self, symbol :str, company_name :str):
        return stock_list_collection.insert_one(company_name = company_name , symbol = symbol)

    def delete_one_stock(self, stock_id : str ):
        return stock_list_collection.delete_one_stock(stock_id)
        
    
    def update_one_stock(self, stock_id : str ,symbol : str, company_name : str):
        if (symbol != "" and len(symbol) > 0) and (company_name != "" and len(company_name) > 0) :
            return stock_list_collection.update_one_stock(stock_id, symbol, company_name)
        
    def get_all_stocks(self,  limit = None) -> list:
        return stock_list_collection.get_all_stocks(limit=None)
    
    def update_stock_id(self, id, new_stock_id):
        return stock_list_collection.update_stock_id(id, new_stock_id)
    
    def get_stock_list_key_value(self):
        
        result = self.get_cache( "get_stock_list_key_value")

        if result == None :
            result = stock_list_collection.get_all_stocks_key_value()
            self.set_cache("get_stock_list_key_value", result, ttl_seconds = 5)
            # print("Cached just now")
            return result
        
        return result
        
            
    
# history

    def get_stock_history(self, stock_id : str):
        return stock_list_collection.get_stock_history(stock_id)
        
    
        

# status

    def change_stock_status(self, stock_id , is_active = True):
        return stock_list_collection.change_stock_status(stock_id, is_active)
# extra
    def get_all_stocks_key_value(self):
        return stock_list_collection.get_all_stocks_key_value()
    

# users stock list

    def user_get_all_stock_list(self, email):
        return social_user_collection.get_stock_list_with_emailid(email)

    def user_create_stock_list(self, name, email):
        return social_user_collection.create_stock_list(email = email, name=name)

    def save_user_stock_list(self, id, name, email, stock_id_list):
        return social_user_collection.update_stock_list(email = email, list_id = id, name = name, stock_symbols = stock_id_list)

    def user_delete_stock_list(self, email, id):
        return social_user_collection.delete_stock_list(email = email, list_id = id)
    

    def user_get_all_stock_list_name(self, email):
        return social_user_collection.get_stock_list_id_name(email)
    

    def user_get_stock_list_by_id(self, id,  email ):
        return social_user_collection.get_user_stock_list_by_id(email = email, list_id= id)
