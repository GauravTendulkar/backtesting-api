
from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Body, Security, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import pytz
from database.security_function import verify_password, get_password_hash, create_access_token, create_user, get_user, authenticate_user, get_user_by_id, verify_token, get_current_user
from database.models import UserInDB, LoginResponse, VerifyUser, LoginCheckInput, SignupCheckInput, AuthUserOutput
from database.configurations import collection_user
import os
from dotenv import load_dotenv  # Import load_dotenv
from database.configurations import client
from database import forgotPassword
from functools import partial
from pydantic import BaseModel

load_dotenv()

# Now you can access the variables using os.environ
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))  # Default to 30 if not set


oauth_router = APIRouter()

# Function to create user with unique email
@oauth_router.post("/signup")
async def create_user_endpoint(user: SignupCheckInput):
    # print(user)
    # Check if the email is unique
    user_dict = dict(user)
    # print(user_dict)
    temp = collection_user.find_one({"email": user_dict["email"]})
    
    if temp:
        raise HTTPException(status_code=400, detail="Email already registered")
        # return {"detail":"Email already registered"}
    
    user_return = create_user(user_dict)
    # print(user_return)
    
    
    return {"data" : "Account created successfully!"}



# Function to login user
@oauth_router.post("/signin", response_model=LoginResponse)  # Updated response model
async def login_user_endpoint(form_data: LoginCheckInput):
    user = authenticate_user(form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # print(user)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)

    ist_timezone = pytz.timezone("Asia/Kolkata")
    expire = datetime.now(ist_timezone) + access_token_expires
    # print(expire)

    return LoginResponse(access_token=access_token, token_type="bearer", expire=expire)  # Updated return statement


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="oauth/signin")

# @oauth_router.get("/users/me")
# async def read_users_me(token: str = Depends(oauth2_scheme)):
#     print(token)
#     user = get_current_user(token)
#     if user:

    
#         return {"access_token": "valid" } 
#     else:
#         return {"access_token": "invalid" } 

@oauth_router.get("/users/me", response_model=AuthUserOutput)
# @oauth_router.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    # print(token)
    try:
        user = dict(get_current_user(token))
        # print(user)
        if user:
            # print(AuthUserOutput(**user))
            # print(user)
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
    except Exception as e:
        # print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
def get_datetime_now():
    return datetime.strptime(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

@oauth_router.post("/sendOTP") 
async def forgotOTP_verify_email(background_tasks: BackgroundTasks, email : str = Body(...)  ):
    # print(email)
    otp = forgotPassword.generate_otp(length=6)
    user_data = collection_user.find_one({"email": email}, { "_id": 0, "email": 1, "otp": 1 })
    # print(user_data)
    if user_data:
        # print("OTP", otp)
        collection_user.update_one( {"email" : email}, {"$set": { "otp": [otp, get_datetime_now()] }} )
        # BackgroundTasks.add_task(forgotPassword.send_otp_email, email, otp, sender_email="1248clashofclans8421@gmail.com", sender_password="zuajcznsfdrswnhv")
        background_tasks.add_task(forgotPassword.send_otp_email, email, otp, "1248clashofclans8421@gmail.com", "zuajcznsfdrswnhv")
        return {"message" : f"OTP has been send to {email}"}
    else:
        raise HTTPException(status_code=400, detail="User does not exist")

class OTPRequest(BaseModel):
    email: str
    otp: str        


@oauth_router.post("/verifyOTP") 
async def forgotOTP_verify_email( data : OTPRequest = Body(...)   ):
    data = dict(data)
    # print("data", data)

    user_data = collection_user.find_one({"email": data["email"]}, { "_id": 0, "email": 1, "otp": 1 })
    if user_data:
        # print(user_data, data)
        if user_data["email"] == data["email"] and  user_data["otp"][0] == data["otp"]:
            if (get_datetime_now() - user_data["otp"][1]) < timedelta(minutes=30):
                
                return {"message" : f"OTP has been verified"}
            else:
                raise HTTPException(status_code=400, detail="otp is expired")
        else:
            raise HTTPException(status_code=400, detail="wrong otp entered")




class ChangePasswordRequest(BaseModel):
    email: str
    otp: str    
    password : str

@oauth_router.post("/changePassword") 
async def forgotOTP_verify_email( data : ChangePasswordRequest = Body(...)   ):
    data = dict(data)
    # print("data", data)
    user_data = collection_user.find_one({"email": data["email"]}, { "_id": 0, "email": 1, "otp": 1 })
    if user_data:
        # print(user_data, data)
        if user_data["email"] == data["email"] and  user_data["otp"][0] == data["otp"]:
            if (get_datetime_now() - user_data["otp"][1]) < timedelta(minutes=30):
                hashed_password = get_password_hash(data['password'])
                collection_user.update_one(
                {"email": data["email"] },  
                {"$set": {"otp": ["", get_datetime_now()], "hashed_password": hashed_password } }  )
                return {"message" : f"Your Password has been changed"}
            else:
                raise HTTPException(status_code=400, detail="Your session has been Expired")
        else:
            raise HTTPException(status_code=400, detail="wrong otp entered")
    else:
        raise HTTPException(status_code=400, detail="User does not exist")
    
