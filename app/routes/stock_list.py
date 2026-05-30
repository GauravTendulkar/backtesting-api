from fastapi import FastAPI, Request, APIRouter, BackgroundTasks
import random
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Body, Security
# from database.security_function import verify_password, get_password_hash, create_access_token, create_user, get_user, authenticate_user, get_user_by_id, verify_token, get_current_user
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from bson import ObjectId
# from database import jwt_decoder
from ..database.mongodb.repositories import social_user_collection
from ..stocklist_manager import get_stocklist_for_user, save_stocklist, slm
# from ..auth.id_password_auth import get_current_user
from ..auth.id_password_auth import get_current_user




stock_list_router = APIRouter()





def random_stock_list_no_duplicates(stock_list, l):
    if l >= len(stock_list):
        # raise ValueError("l cannot be greater than the length of the stock list when duplicates are not allowed.")
        return stock_list
    return random.sample(stock_list, l)

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="oauth/signin", auto_error=False)
STOCK_LIST_LIMIT = 30
STOCK_EXECUTION_LIST_LIMIT = 200


# @stock_list_router.post("/get/")
# async def get_stock_list(user_email = Depends(get_current_user)):
#     # print(user_email, "get_stock_list" "**********************************************")
#     return get_stocklist_for_user(user_email)



class StockListItem(BaseModel):
    name: str
    list: List[str]
    


class StockListItemWithEmail(BaseModel):
    stock_list : List[StockListItem]
    user_email : str

# @stock_list_router.put("")
# async def save_stock_list(stockList: StockListItemWithEmail = Body(...)):
#     # Print the received list (it will be a list of StockListItem objects)
#     # print(stockList)
#     print("****************************")
#     return save_stocklist(stockList)
        
# print("slm" , type(slm) )

# _____________Modals__________________________

class InsertStock(BaseModel):
    symbol : str
    company_name : str

class Status(BaseModel):
    is_active : bool

class StockList(BaseModel) : 
    name : str


class CreateUserStockList(BaseModel):
    name : str

class UpdateUserStockList(BaseModel):
    name: Optional[str] = None
    list: Optional[List[str]] = None

class UpdateStockId(BaseModel):
    stock_id : str

# _______________________________________

# insert one
@stock_list_router.put("")
async def root(data : InsertStock) :
    # print("PUT", data, data.symbol, data.company_name)
    result =  slm.insert_one_stock(symbol = data.symbol ,company_name = data.company_name)
    return {"id" : str(result)}
 

# get all stock
@stock_list_router.get("")
async def root() :
    # print("GET")
    return slm.get_all_stocks()

@stock_list_router.patch("/{id}/stock-id")
async def root(id, data : UpdateStockId):
    # print("DELETE", id)
    return slm.update_stock_id(id = id, stock_id = data.stock_id)

# delete by id
@stock_list_router.delete("/{id}")
async def root(id : str):
    # print("DELETE", id)
    return slm.delete_one_stock(stock_id=id)
     

@stock_list_router.patch("/{id}")
async def root(id, data : InsertStock):
    return slm.update_one_stock(stock_id = id ,symbol = data.symbol ,company_name = data.company_name)
    

@stock_list_router.get("/history/{id}")
async def root(id :  str):
    # print("GET", id)
    return slm.get_stock_history( stock_id = id )
    


@stock_list_router.patch("/status/{id}")
async def root(id :  str, data : Status):
    # print(id, data)
    return slm.change_stock_status(stock_id = id, is_active= data.is_active )


@stock_list_router.patch("/status/{id}")
async def root(id :  str, data : Status):
    # print(id, data)
    return slm.change_stock_status(stock_id = id, is_active= data.is_active )


@stock_list_router.get("/key-value")
async def root():
    return slm.get_stock_list_key_value()

@stock_list_router.get("/default")
async def root():
    output  = slm.get_stock_list_key_value()
    stock_list = list(output.keys())  
    l = 5
    if len(stock_list) < l:
        return stock_list
    return random.sample(stock_list, l)
     

# ________________________________________

# get all user stock list
@stock_list_router.get("/user")
async def root(email = Depends(get_current_user)):
    
    return slm.user_get_all_stock_list(email)
    

# create 
@stock_list_router.put("/user")
async def root(data : CreateUserStockList, email = Depends(get_current_user)):
    
    return slm.user_create_stock_list(name = data.name, email = email)
    


#  save stock
@stock_list_router.patch("/user/{id}")
async def root(id : str, data : UpdateUserStockList, email = Depends(get_current_user)):
    # email = ""
    # return slm.user_create_stock_list(name = id, email = email)
    print("email", email)
    return  slm.save_user_stock_list(id = id, email = email, name = data.name , stock_id_list = data.list)
    
# save stock list 
@stock_list_router.delete("/user/{id}")
async def root(id : str, email = Depends(get_current_user)):
    print("email", email)
    return slm.user_delete_stock_list(email = email, id = id)

#  {id , name }
@stock_list_router.get("/user/meta")
async def root( email = Depends(get_current_user)):
    
    return slm.user_get_all_stock_list_name(email)

@stock_list_router.get("/user/{id}")
async def root(id : str, email = Depends(get_current_user)):
    return slm.user_get_stock_list_by_id(id,  email )