from pydantic import BaseModel, Field
from datetime import datetime

from pydantic import BaseModel
from typing import Optional, Dict, Any
import pytz
ist_timezone = pytz.timezone("Asia/Kolkata")
currect_time = datetime.now(ist_timezone)
class Equation(BaseModel):
    stockListName: str
    title: str
    description: str
    scanCategory: str
    equation: str
    # updated_at: int = int(datetime.timestamp(datetime.now())) 
    # created: int = int(datetime.timestamp(datetime.now())) 
    link : str = ""
    updated_at: datetime = datetime.strptime(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    created: datetime = datetime.strptime(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    # email: str
    isPrivate : bool = False


# _______________________________________

class SignupCheckInput(BaseModel):

    full_name: str
    email : str
    hashed_password : str

class LoginCheckInput(BaseModel):
    email : str
    password : str


class User(BaseModel):
    # username: str
    email: str
    full_name: str = None
    account_created: datetime = datetime.strptime(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    # disabled: Optional[bool] = None


# Define a UserInDB model
class UserInDB(User):
    hashed_password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    # user: User  # Use the User model instead of UserInDB
    expire: datetime



class VerifyUser(BaseModel):
    access_token: str


class PaginationOutput(BaseModel):
    page : int
    items : list
    total_no_of_pages: int


class LinkGetOutput(BaseModel):
    id : str = Field(..., alias="_id")
    stockListName: str
    title : str
    description : str
    scanCategory : str
    equation : str
    link: str
    updated_at : datetime
    created : datetime
    isPrivate : bool
    model_config = {
        "populate_by_name": True  # Allows aliasing to work
    }


class AuthUserOutput(BaseModel):
    full_name:str
    email:str
    account_created: datetime