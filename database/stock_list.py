from fastapi import FastAPI, Request, APIRouter, BackgroundTasks
import random
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Body, Security
from database.security_function import verify_password, get_password_hash, create_access_token, create_user, get_user, authenticate_user, get_user_by_id, verify_token, get_current_user
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from database import configurations
from bson import ObjectId


stock_list_router = APIRouter()

stock_list = [
            # "AARTIIND", "ABB", "ABCAPITAL", "ABFRL", "ACC", "ADANIENT",
            # "ADANIPORTS", "ALKEM", "AMBUJACEM", "APOLLOHOSP", "APOLLOTYRE",
            # "ASHOKLEY", "ASIANPAINT", "ASTRAL", "ATUL", "AUBANK", "AUROPHARMA",
            # "AXISBANK", "BAJAJ_AUTO", "BAJAJFINSV", "BAJFINANCE", "BALKRISIND",
            # "BALRAMCHIN", "BANDHANBNK", "BANKBARODA",
            "INFY", 
            "AMBUJACEM",
            "BAJFINANCE",
            "BIOCON",
            "COALINDIA",
            "DIVISLAB",
            "FEDERALBNK",
            "GNFC",
            "GRANULES",
            "HCLTECH",
            "ITC",
            "ONGC",
            "PEL",
            "PERSISTENT",
            "POLYCAB",
            "RELIANCE",
            "SBIN",
            "SYNGENE",
            "TATAMOTORS",
            "TCS",
            "TORNTPHARM",
            "UPL",
            "ZEEL",
        ]


def random_stock_list_no_duplicates(stock_list, l):
    if l >= len(stock_list):
        # raise ValueError("l cannot be greater than the length of the stock list when duplicates are not allowed.")
        return stock_list
    return random.sample(stock_list, l)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="oauth/signin", auto_error=False)
STOCK_LIST_LIMIT = 20
STOCK_EXECUTION_LIST_LIMIT = 20


@stock_list_router.get("")
async def get_stock_list(token: Optional[str] = Depends(oauth2_scheme)):
    
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
    if token == None:
        return stockData
    # print("token", token)

    user = dict(get_current_user(token))
        # print(user)
    if user:
        stockData["customStockList"] = user["stock_list"]
        return stockData
    else:
        return stockData



class StockListItem(BaseModel):
    name: str
    list: List[str]


@stock_list_router.put("")
async def save_stock_list(
    stockList: List[StockListItem] = Body(...),
    token: Optional[str] = Depends(oauth2_scheme)
):
    # Print the received list (it will be a list of StockListItem objects)
    stockList = [item.model_dump() for item in stockList]
    print(stockList)
    

    
    # Optionally, retrieve current user based on the token.
    user = dict(get_current_user(token))
    if user:
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
        configurations.collection_user.update_one({"_id": user["_id"], "email": user["email"] }, {"$set": {"stock_list" : stockList }})

        return {"message": "Stock list saved"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login or create an account to save stock list",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    
