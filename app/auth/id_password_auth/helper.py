
from passlib.context import CryptContext
from datetime import datetime, timedelta
import pytz
from typing import Optional, Dict, Any
from ...database.mongodb.repositories import users_collection
from ...config import env
from jose import JWTError, jwt
from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Body, Security, BackgroundTasks

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def get_datetime_now():
    return datetime.strptime(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")



def get_password_hash(password: str) :
    return pwd_context.hash(password)

def create_user(user_dict) :
    user_dict['hashed_password'] = get_password_hash(user_dict['hashed_password'])

    
    user_dict['username'] = get_password_hash(user_dict['email'])
   
    

    user_dict['account_created'] = get_datetime_now()
    user_dict['stock_list'] = []
    user_dict['otp'] = ["", get_datetime_now()]
    result = users_collection.insert_one(user_dict)
    
    user_dict['_id'] = str(result.inserted_id)
    return user_dict


def get_user(email: str):
    
    user_data = users_collection.get_user_with_email(email)
    
    if user_data:
        
        return user_data

def verify_password(plain_password: str, hashed_password: str) :
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(email: str, password: str):
    user = get_user(email)
   
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) :
    to_encode = data.copy()
    if expires_delta:
        ist_timezone = pytz.timezone("Asia/Kolkata")
        expire = datetime.now(ist_timezone) + expires_delta
    else:
        ist_timezone = pytz.timezone("Asia/Kolkata")
        expire = datetime.now(ist_timezone) + timedelta(minutes=env.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, env.SECRET_KEY, algorithm=env.ALGORITHM)
    return encoded_jwt


def get_user_username(username: str):
    # user_data = collection_user.find_one({"username": username})
    user_data = users_collection.get_user_with_username(username)
    if user_data:
        return user_data

def verify_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, env.SECRET_KEY, algorithms=[env.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        user = get_user_username(username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="login"))):
    return verify_token(token)