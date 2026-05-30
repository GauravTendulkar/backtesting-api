from fastapi import FastAPI, Request, APIRouter,Depends, HTTPException, status, Body

import pandas as pd
import numpy as np


from datetime import date
from filelock import FileLock
# from database.security_function import get_current_user, get_datetime_now
from typing import Optional
from pydantic import BaseModel

# from ..database.mongodb.repositories import equation_collection
from ..backtesting_logic_interface import (dashboard_pagination_logic, get_backtesting_logic_with_url,delete_equation_fn, save_as_logic,save_logic, get_all_links,
                                           PaginationOutput, Equation, LinkGetOutput,
                                           )
from ..auth.id_password_auth import get_current_user
# from database import jwt_decoder


equation_router = APIRouter()




@equation_router.post("/", response_model=PaginationOutput)
async def get_equations(page: int, noOfItems : int, user_email = Depends(get_current_user)):
   
    print("pagination email",user_email, page, noOfItems)
    
    return dashboard_pagination_logic(user_email, page, noOfItems)

class EmailRequest(BaseModel):
    user_email: Optional[str] = None
# get data with the link
@equation_router.post("/{link}", response_model=LinkGetOutput)
async def get_equations(link: str,  user_email = Depends(get_current_user)):
    # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    # print("link", link, user_email)
    return get_backtesting_logic_with_url(link, user_email)
    
        



@equation_router.post("/delete/{id}")
async def delete_equation(id: str, user_email = Depends(get_current_user)):
    
    print("Delete", user_email) 

    return delete_equation_fn(user_email, id)

@equation_router.post("/save-as/")
async def get_equations(equation: Equation, user_email = Depends(get_current_user)): 
    

    return save_as_logic(equation, user_email)

@equation_router.put("/{id}")
async def get_equations(id: str, equation: Equation, user_email = Depends(get_current_user) ):
    
   
    return save_logic(id, equation, user_email)


@equation_router.get("/links")
async def root()-> list: 
    return get_all_links()


