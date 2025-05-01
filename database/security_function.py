
from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Body, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional, Dict, Any
from pymongo import MongoClient
from bson import ObjectId
import pytz
from database.models import UserInDB, User
import os
from dotenv import load_dotenv  
from database.configurations import collection_user
from database.configurations import client

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))  

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to verify password
def verify_password(plain_password: str, hashed_password: str) :
    return pwd_context.verify(plain_password, hashed_password)

# Function to get hashed password
def get_password_hash(password: str) :
    return pwd_context.hash(password)

# Function to create access token
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) :
    to_encode = data.copy()
    if expires_delta:
        ist_timezone = pytz.timezone("Asia/Kolkata")
        expire = datetime.now(ist_timezone) + expires_delta
    else:
        ist_timezone = pytz.timezone("Asia/Kolkata")
        expire = datetime.now(ist_timezone) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def get_datetime_now():
    return datetime.strptime(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

def create_user(user_dict) :
    # user_dict = user.copy()
    # print(user_dict)
    user_dict['hashed_password'] = get_password_hash(user_dict['hashed_password'])

    # email_username = user_dict['email'].split('@')[0]
    user_dict['username'] = get_password_hash(user_dict['email'])
    # user_dict['username'] = email_username
    
    # ist_timezone = pytz.timezone("Asia/Kolkata")
    # expire = datetime.now(ist_timezone)
    

    user_dict['account_created'] = get_datetime_now()
    user_dict['stock_list'] = []
    user_dict['otp'] = ["", get_datetime_now()]
    result = collection_user.insert_one(user_dict)
    
    user_dict['_id'] = str(result.inserted_id)
    return user_dict

# Function to get user by username
def get_user(email: str):
    user_data = collection_user.find_one({"email": email})
    
    if user_data:
        
        return user_data

# Function to authenticate user
def authenticate_user(email: str, password: str):
    user = get_user(email)
    # print("user", user)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user

# Function to get user by ID
def get_user_by_id(user_id: str):
    user_data = collection_user.find_one({"_id": ObjectId(user_id)})
    
    if user_data:
        return user_data


def get_user_username(username: str):
    user_data = collection_user.find_one({"username": username})
    
    if user_data:
        return user_data

# Function to decode and verify JWT token
def verify_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        user = get_user_username(username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

# Dependency to get the current user from the token
def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="login"))):
    return verify_token(token)