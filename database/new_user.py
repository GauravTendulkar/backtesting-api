from fastapi import FastAPI, Request, APIRouter,Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from database import configurations
from datetime import datetime, timedelta
import pytz


new_user_social = APIRouter()

class SocalLogin(BaseModel):
    fullName : str
    userEmail : str
    provider: str
    providerId: str


def get_datetime_now():
    return datetime.strptime(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

@new_user_social.post("/")
async def get_new_user(data : SocalLogin):
    print(data, "*********************************")
    data = dict(data)
    if configurations.collection_social_user.find_one({"email": data["userEmail"]}, {"_id": 0, "email": 1}) is None:
        data_dict = {
            "full_name" : data["fullName"],
            "email" : data["userEmail"],
            "account_created" : get_datetime_now(),
            "last_signin" : get_datetime_now(),
            "provider" : data["provider"],
            "providerId" : data["providerId"],
            "stock_list" : [],
            "roles" : ["user"]
        }

        configurations.collection_social_user.insert_one(data_dict)
    else:
        configurations.collection_social_user.update_one({"email" : data["userEmail"]}, {"$set": {"last_signin" : get_datetime_now(),}})
        
    





