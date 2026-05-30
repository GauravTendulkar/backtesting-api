from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime, timezone
import pytz
from ..database.mongodb.repositories import social_user_collection, equation_collection, votes_collection, users_collection, strategy_run_collection

from ..auth.id_password_auth import get_current_user
from ..config import env

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
    print("###############################") 
    print(data, "*********************************") 
    data = dict(data)
    if social_user_collection.get_one_with_email(data["userEmail"]) is None:
        data_dict = {}
        if data["userEmail"] == env.INITIAL_ADMIN_EMAIL_ID:
            data_dict = {
                "full_name" : data["fullName"],
                "email" : data["userEmail"],
                "account_created" : get_datetime_now(),
                "last_signin" : get_datetime_now(),
                "provider" : data["provider"],
                "providerId" : data["providerId"],
                "stock_list" : [],
                "roles" : [{"name": "user-login", "start_date":get_current_date(),"end_date":get_current_date(),  "isActive": True, "limit": "unlimited"},
                           {"name": "admin", "start_date":get_current_date(),"end_date":get_current_date(),  "isActive": True, "limit": "unlimited"},
                           ]
            }
        else:
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


        
        social_user_collection.insert_one(data_dict)
    else:
        # add a function to append admin role after login
        social_user_collection.update_one_social_user_with_email(data["userEmail"], get_datetime_now())
        if data["userEmail"] == env.INITIAL_ADMIN_EMAIL_ID:
            social_user_collection.update_admin_role_if_not_exist(data["userEmail"], 
                {
                    "name": "admin",
                    "start_date": get_current_date(),
                    "end_date": get_current_date(),
                    # "isActive": True,
                    "limit": "unlimited"
                })
        



class DeleteUser(BaseModel):
    
    email : str
    

@new_user_social.post("/delete")
async def get_new_user(user_email=Depends(get_current_user)):
    print("#########################")
    print("delete email", user_email)
    print("**************************")
    # email = "intraday.trading1000@gmail.com"
    social_user_collection.delete_all_with_email(user_email)
    equation_collection.delete_all_with_email(user_email)
    # delete_all_user_data(email)
    votes_collection.delete_all_with_email(user_email)
    users_collection.delete_all_with_email(user_email)
    strategy_run_collection.delete_all_with_email(user_email)

    


