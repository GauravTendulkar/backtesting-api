
from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Body, Security, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import pytz
# from database.security_function import verify_password, get_password_hash, create_access_token, create_user, get_user, authenticate_user, get_user_by_id, verify_token, get_current_user
# from database.models import UserInDB, LoginResponse, VerifyUser, LoginCheckInput, SignupCheckInput, AuthUserOutput
# from database.configurations import collection_user
import os
from dotenv import load_dotenv  # Import load_dotenv

from functools import partial
from pydantic import BaseModel
from ..database.mongodb.repositories import users_collection
from ..auth.id_password_auth import (do_user_signup, do_user_signin, verify_user_fn, send_otp, verify_otp, change_password_with_otp)



oauth_router = APIRouter()
# ----------------------------------------------Model---------------------------
class SignupCheckInput(BaseModel): 

    full_name: str
    email : str
    hashed_password : str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    # user: User  # Use the User model instead of UserInDB
    expire: datetime

class LoginCheckInput(BaseModel):
    email : str
    password : str

class AuthUserOutput(BaseModel):
    full_name:str
    email:str
    account_created: datetime

# ----------------------------------------------Routes---------------------------

# Function to create user with unique email
@oauth_router.post("/signup")
async def create_user_endpoint(user: SignupCheckInput):
    
    return do_user_signup(user)



# Function to login user
@oauth_router.post("/signin", response_model=LoginResponse)  # Updated response model
async def login_user_endpoint(form_data: LoginCheckInput):
   
    return do_user_signin(form_data)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="oauth/signin")


@oauth_router.get("/users/me", response_model=AuthUserOutput)
# @oauth_router.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    
    return verify_user_fn(token)
    
def get_datetime_now():
    return datetime.strptime(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

@oauth_router.post("/sendOTP") 
async def forgotOTP_verify_email(background_tasks: BackgroundTasks, email : str = Body(...)  ):
    # print(email)
    return send_otp(email, background_tasks)

class OTPRequest(BaseModel):
    email: str
    otp: str        


@oauth_router.post("/verifyOTP") 
async def forgotOTP_verify_email( data : OTPRequest = Body(...)   ):
   
    return verify_otp(data)




class ChangePasswordRequest(BaseModel):
    email: str
    otp: str    
    password : str

@oauth_router.post("/changePassword") 
async def forgotOTP_verify_email( data : ChangePasswordRequest = Body(...)   ):
    
    return change_password_with_otp(data)
    
