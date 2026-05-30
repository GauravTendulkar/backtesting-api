
import random
from .config import STOCK_LIST_LIMIT, STOCK_EXECUTION_LIST_LIMIT, STOCK_LIST
from ..database.mongodb.repositories import social_user_collection

def random_stock_list_no_duplicates(stock_list, l):
    if l >= len(stock_list):
        # raise ValueError("l cannot be greater than the length of the stock list when duplicates are not allowed.")
        return stock_list
    return random.sample(stock_list, l)

def get_stocklist_for_user(user_email):
    stockData = {
        "stockListLimit": STOCK_LIST_LIMIT,
        "stockExecutionListLimit": STOCK_EXECUTION_LIST_LIMIT,
        "fullStockList": STOCK_LIST,
        "defaultStockList": [{
            "name": "default",
            "list": random_stock_list_no_duplicates(STOCK_LIST, 5)
        }
        ],
        "customStockList": [
            # { "name": "list 1", "list": ["AARTIIND", "ABB", "ABCAPITAL", "ABFRL", "ACC", "ADANIENT", "ADANIPORTS"] },
            # { "name": "list 2", "list": ["ATUL", "AUBANK"] },
            # { "name": "list 3", "list": ["BALKRISIND", "BALRAMCHIN", "BANDHANBNK", "BANKBARODA"] },
        ]
    }
    # print("stockData", stockData)
    if user_email == None:
        return stockData
    
    if user_email:
       
        stockData["customStockList"] = social_user_collection.get_one_with_email_o_stocklist(user_email)
        return stockData
    else:
        return stockData