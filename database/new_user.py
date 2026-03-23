from fastapi import FastAPI, Request, APIRouter,Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from database import configurations
from datetime import datetime, timedelta, timezone
import pytz


new_user_social = APIRouter()

class SocalLogin(BaseModel):
    fullName : str
    userEmail : str
    provider: str
    providerId: str


def get_datetime_now():
    return datetime.strptime(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

def get_current_date():
    now = datetime.now(timezone.utc)
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    now = datetime.strptime(now, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    return now

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
            "roles" : [{"name": "user-login", "start_date":get_current_date(),"end_date":get_current_date(),  "isActive": True, "limit": "unlimited"}]
        }

        configurations.collection_social_user.insert_one(data_dict)
    else:
        configurations.collection_social_user.update_one({"email" : data["userEmail"]}, {"$set": {"last_signin" : get_datetime_now(),}})
        
    





