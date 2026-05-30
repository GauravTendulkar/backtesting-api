from pydantic import BaseModel
from ..id_password_auth import helper
from fastapi import HTTPException
from datetime import datetime, timedelta
import pytz
from ...config import env


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    # user: User  # Use the User model instead of UserInDB
    expire: datetime

def do_user_signin(form_data):
    user = helper.authenticate_user(form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # print(user)
    access_token_expires = timedelta(minutes=env.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = helper.create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)

    ist_timezone = pytz.timezone("Asia/Kolkata")
    expire = datetime.now(ist_timezone) + access_token_expires
    # print(expire)

    return LoginResponse(access_token=access_token, token_type="bearer", expire=expire)  # Updated return statement