from fastapi import FastAPI, Request, APIRouter, BackgroundTasks
import random
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Body, Security
from database.security_function import verify_password, get_password_hash, create_access_token, create_user, get_user, authenticate_user, get_user_by_id, verify_token, get_current_user
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from database import configurations
from bson import ObjectId
from database import jwt_decoder

stock_list_router = APIRouter()

# stock_list = [
#             # "AARTIIND", "ABB", "ABCAPITAL", "ABFRL", "ACC", "ADANIENT",
#             # "ADANIPORTS", "ALKEM", "AMBUJACEM", "APOLLOHOSP", "APOLLOTYRE",
#             # "ASHOKLEY", "ASIANPAINT", "ASTRAL", "ATUL", "AUBANK", "AUROPHARMA",
#             # "AXISBANK", "BAJAJ_AUTO", "BAJAJFINSV", "BAJFINANCE", "BALKRISIND",
#             # "BALRAMCHIN", "BANDHANBNK", "BANKBARODA",
# "AMBUJACEM",
# "BIOCON",
# "DIVISLAB",
# "FEDERALBNK",
# "GNFC",
# "GRANULES",
# "PEL",
# "PERSISTENT",
# "POLYCAB",
# "SYNGENE",
# "TORNTPHARM",
# "UPL",
# "ZEEL",

# # new list
# "TITAN",
# "TATAMOTORS",
# "LT",
# "BEL",
# "SBIN",
# "HINDALCO",
# "ONGC",
# "DRREDDY",
# "JSWSTEEL",
# "WIPRO",
# "ASIANPAINT",
# "TATACONSUM",
# "TCS",
# "INFY",
# "CIPLA",
# "TECHM",
# "TATASTEEL",
# "HCLTECH",
# "COALINDIA",
# "EICHERMOT",
# "INDUSINDBK",
# "SUNPHARMA",
# "BHARTIARTL",
# "AXISBANK",
# "RELIANCE",
# "BAJFINANCE",
# "ULTRACEMCO",
# "GRASIM",
# "ADANIPORTS",
# "ITC",
# "EICHERMOT"

    
    
#         ]

stock_list = [

    "AARTIIND",
"ABB",
"ABCAPITAL",
"ABFRL",
"ACC",
"ADANIENT",
"ADANIPORTS",
"ALKEM",
"AMBUJACEM",
"APOLLOHOSP",
"APOLLOTYRE",
"ASHOKLEY",
"ASIANPAINT",
"ASTRAL",
"ATUL",
"AUBANK",
"AUROPHARMA",
"AXISBANK",
"BAJAJFINSV",
"BAJAJ_AUTO",
"BAJFINANCE",
"BALKRISIND",
"BALRAMCHIN",
"BANDHANBNK",
"BANKBARODA",
"BATAINDIA",
"BEL",
"BERGEPAINT",
"BHARATFORG",
"BHARTIARTL",
"BHEL",
"BIOCON",
"BPCL",
"BRITANNIA",
"BSOFT",
"CANBK",
"CANFINHOME",
"CHAMBLFERT",
"CHOLAFIN",
"CIPLA",
"COALINDIA",
"COFORGE",
"COLPAL",
"CONCOR",
"COROMANDEL",
"CROMPTON",
"CUB",
"CUMMINSIND",
"DABUR",
"DALBHARAT",
"DEEPAKNTR",
"DIVISLAB",
"DIXON",
"DLF",
"DRREDDY",
"EICHERMOT",
"ESCORTS",
"EXIDEIND",
"FEDERALBNK",
"GAIL",
"GLENMARK",
"GMRINFRA",
"GNFC",
"GODREJPROP",
"GRANULES",
"GRASIM",
"GUJGASLTD",
"HAL",
"HAVELLS",
"HCLTECH",
"HDFCAMC",
"HDFCBANK",
"HDFCLIFE",
"HEROMOTOCO",
"HINDALCO",
"HINDCOPPER",
"HINDPETRO",
"HINDUNILVR",
"ICICIBANK",
"ICICIGI",
"ICICIPRULI",
"IDFCFIRSTB",
"IEX",
"IGL",
"INDHOTEL",
"INDIACEM",
"INDIAMART",
"INDIGO",
"INDUSINDBK",
"INDUSTOWER",
"INFY",
"IOC",
"IPCALAB",
"IRCTC",
"ITC",
"JINDALSTEL",
"JKCEMENT",
"JSWSTEEL",
"JUBLFOOD",
"KOTAKBANK",
"LALPATHLAB",
"LAURUSLABS",
"LICHSGFIN",
"LTF",
"LTIM",
"LTTS",
"LT",
"LUPIN",
"MANAPPURAM",
"MARICO",
"MCDOWELL_N",
"MCX",
"METROPOLIS",
"MFSL",
"MGL",
"MOTHERSON",
"MPHASIS",
"MUTHOOTFIN",
"M_MFIN",
"M_M",
"NATIONALUM",
"NAUKRI",
"NAVINFLUOR",
"NESTLEIND",
"NMDC",
"NTPC",
"OBEROIRLTY",
"OFSS",
"ONGC",
"PEL",
"PERSISTENT",
"PETRONET",
"PFC",
"PIDILITIND",
"PIIND",
"PNB",
"POLYCAB",
"POWERGRID",
"PVRINOX",
"RAMCOCEM",
"RBLBANK",
"RECLTD",
"RELIANCE",
"SAIL",
"SBICARD",
"SBILIFE",
"SBIN",
"SHRIRAMFIN",
"SIEMENS",
"SRF",
"SUNPHARMA",
"SUNTV",
"SYNGENE",
"TATACHEM",
"TATACOMM",
"TATACONSUM",
"TATAMOTORS",
"TATAPOWER",
"TATASTEEL",
"TCS",
"TECHM",
"TITAN",
"TORNTPHARM",
"TRENT",
"TVSMOTOR",
"UBL",
"ULTRACEMCO",
"UPL",
"VEDL",
"VOLTAS",
"WIPRO",
"ZEEL",
"ZYDUSLIFE",
]


def random_stock_list_no_duplicates(stock_list, l):
    if l >= len(stock_list):
        # raise ValueError("l cannot be greater than the length of the stock list when duplicates are not allowed.")
        return stock_list
    return random.sample(stock_list, l)

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="oauth/signin", auto_error=False)
STOCK_LIST_LIMIT = 30
STOCK_EXECUTION_LIST_LIMIT = 200


@stock_list_router.post("/get/")
async def get_stock_list(user_email = Depends(jwt_decoder.get_current_user)):
    print(user_email, "get_stock_list" "**********************************************")
    stockData = {
        "stockListLimit": STOCK_LIST_LIMIT,
        "stockExecutionListLimit": STOCK_EXECUTION_LIST_LIMIT,
        "fullStockList": stock_list,
        "defaultStockList": [{
            "name": "default",
            "list": random_stock_list_no_duplicates(stock_list, 5)
        }
        ],
        "customStockList": [
            # { "name": "list 1", "list": ["AARTIIND", "ABB", "ABCAPITAL", "ABFRL", "ACC", "ADANIENT", "ADANIPORTS"] },
            # { "name": "list 2", "list": ["ATUL", "AUBANK"] },
            # { "name": "list 3", "list": ["BALKRISIND", "BALRAMCHIN", "BANDHANBNK", "BANKBARODA"] },
        ]
    }
    print("stockData", stockData)
    if user_email == None:
        return stockData
    # print("token", token)

    # user = dict(get_current_user(token))
    # user_email = dict(user_email)["user_email"]
        # print(user)
    if user_email:
        # stockData["customStockList"] = user["stock_list"]
        stockData["customStockList"] = configurations.collection_social_user.find_one({"email": user_email}, {"stock_list"})["stock_list"]
        return stockData
    else:
        return stockData



class StockListItem(BaseModel):
    name: str
    list: List[str]
    


class StockListItemWithEmail(BaseModel):
    stock_list : List[StockListItem]
    user_email : str

@stock_list_router.put("")
async def save_stock_list(stockList: StockListItemWithEmail = Body(...)):
    # Print the received list (it will be a list of StockListItem objects)
    print(stockList)
    print("****************************")
    stockList = dict(stockList)
    user_email = stockList["user_email"]
    
    stockList = stockList["stock_list"]
    stockList = [item.model_dump() for item in stockList]

    print("put Email", user_email)
    print(stockList)
    

    
    # Optionally, retrieve current user based on the token.
    # user = dict(get_current_user(token))
    if user_email:
        print("stockList length", len(stockList))
        if len(stockList) > STOCK_LIST_LIMIT:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Please do not create stock lists more then the limit {STOCK_LIST_LIMIT}",
                headers={"WWW-Authenticate": "Bearer"}
            )
        for i in range(0, len(stockList)):
            if len(stockList[i]["list"]) >  STOCK_EXECUTION_LIST_LIMIT:
                raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Please do not  create individual stock lists more then the limit {STOCK_EXECUTION_LIST_LIMIT}",
                headers={"WWW-Authenticate": "Bearer"}
            )
        # print(user)
        configurations.collection_social_user.update_one({ "email": user_email }, {"$set": {"stock_list" : stockList }})

        return {"message": "Stock list saved"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login or create an account to save stock list",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    
