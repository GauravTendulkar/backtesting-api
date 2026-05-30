
from ...database.mongodb.repositories import (users_collection)
from fastapi import HTTPException
from ..id_password_auth import helper

def do_user_signup(user):
    user_dict = dict(user)
    temp = users_collection.get_user_with_email(user_dict["email"])
    if temp:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    user_return = helper.create_user(user_dict)
    return {"data" : "Account created successfully!"}