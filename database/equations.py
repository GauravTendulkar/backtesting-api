from fastapi import FastAPI, Request, APIRouter,Depends, HTTPException, status, Body
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from functions import timeframe, controller, indicators, backtesting_functions
import time
from datetime import date
from filelock import FileLock
import concurrent.futures
from fastapi.middleware.cors import CORSMiddleware
from database import configurations, models
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from datetime import datetime
import os
import re
from fastapi.security import OAuth2PasswordBearer
from database.security_function import get_current_user, get_datetime_now
import pytz
import math
from database.configurations import  client
from pymongo import ReturnDocument
from typing import Optional
from pydantic import BaseModel
from database import jwt_decoder
import secrets
import string
from slugify import slugify

equation_router = APIRouter()


def get_unique_link(link:str ="", list_of_links:list = [] ):
    existing_numbers = []

    for i in range(0, len(list_of_links)):
        try:
            slice_int = int(list_of_links[i][len(link)+1:])
            # print("slice_int", slice_int)
            existing_numbers.append(slice_int)
        except:
            # print("hello")
            pass
    # print(existing_numbers)
    # Generate a unique number
    if existing_numbers:
        new_number = max(existing_numbers) + 1  # Increment the maximum number
        for j in range(1, max(existing_numbers)+1):
            if j in existing_numbers:
                # print(j)
                pass
            else:
                new_number = j
                break
                
    else:
        new_number = 1  


    new_link = f"{link}-{new_number}"
    return new_link



def title_to_string(temp_str: str):

    temp_str = temp_str.lower()
    def check_string(s):
        # Check if the string contains only a-z and 0-9
        if re.fullmatch(r'[a-z0-9]*', s):
            return True
        return False


    link = ""
    flag = 0
    # print(temp_str)
    for i in range(0, len(temp_str)):
        if check_string(temp_str[i]):
            link += temp_str[i]  # Append valid character
            
            flag = 0
        else:
            if flag == 0:
                link += '-'  # Append '-' for invalid character
                
                flag = 1
    if check_string(link[0]) == False:
        link = link[1:len(link) ]
    
    if check_string(link[len(link)-1]) ==  False:
        link = link[:len(link)-1]
    return link

def increment_suffix(temp):
    i = temp.rfind("-")  # Find the last occurrence of '-'
    if i == -1:  
        return temp + "-1"  # If no '-', just append '-1'
    
    prefix, num = temp[:i], temp[i+1:]  
    if num.isdigit():  
        return f"{prefix}-{int(num) + 1}"  # Increment the number
    return temp + "-1"  # If suffix isn't a number, just add '-1'


def generate_unique_slug(text, random_length=20, slug_max_length=50):
    base_slug = slugify(text, max_length=slug_max_length, word_boundary=True)
    timestamp_ms = int(time.time() * 1000)
    allowed_chars = string.ascii_lowercase + string.digits
    random_suffix = ''.join(secrets.choice(allowed_chars) for _ in range(random_length))

    unique_slug = f"{base_slug}-{timestamp_ms}-{random_suffix}"
    return unique_slug

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="oauth/signin")

@equation_router.post("/", response_model=models.PaginationOutput)
async def get_equations(page: int, noOfItems : int, user_email = Depends(jwt_decoder.get_current_user)):
    

    # user = get_current_user(token)
    # print("user", user)
    print(user_email)
    # user_email = dict(user_email)["user_email"]
    if user_email :


        count = configurations.collection.count_documents({"email" : user_email})
        
        print(count)
        print(page)  # Current page
        items_per_page = noOfItems  # Documents per page
        skip_count = (page - 1) * items_per_page  # Calculate number of documents to skip
        total_no_of_pages = int(math.ceil(count / noOfItems))
        equations_list = []

        if count == 0 and page == 1:
            return {"page": page, "items": equations_list, "total_no_of_pages" : total_no_of_pages}

        if 1<= page and page <= total_no_of_pages:
            equations = configurations.collection.find( {"email" : user_email}, {"title": 1, "description": 1, "created": 1, "updated_at": 1, "likes": 1, "dislikes": 1, "link": 1,} ).sort("created", -1).skip(skip_count).limit(items_per_page)
            
            
            # print("equations")
            equations_list = list(equations)
            for i in range(0, len(equations_list)):
                equations_list[i]["_id"] = str(equations_list[i]["_id"])
        
            
            return {"page": page, "items": equations_list, "total_no_of_pages" : total_no_of_pages}
        else:
            # return {"page": total_no_of_pages, "items": equations_list, "total_no_of_pages" : total_no_of_pages}
            raise HTTPException(status_code=404, detail="Page Not Found")
    else:
            
            raise HTTPException(status_code=404, detail="Page Not Found")

class EmailRequest(BaseModel):
    user_email: Optional[str] = None
# get data with the link
@equation_router.post("/{link}", response_model=models.LinkGetOutput)
async def get_equations(link: str,  user_email = Depends(jwt_decoder.get_current_user)):
    # print(user_email, link , "******************************************")
    # user_email = data.user_email

    equations = configurations.collection.find_one({"link": link})
    # print(equations)
    
    # Ensure that the equations dictionary contains all required fields
    if equations:
        if equations["isPrivate"] == False:
            equations["_id"] = str(equations["_id"])
            
            
            return models.LinkGetOutput(**equations) # Create an instance of LinkGetOutput
        elif equations["isPrivate"] == True:
            # user = get_current_user(token)
            # print("user", user)
            if user_email:
                if user_email == equations["email"]:
                    equations["_id"] = str(equations["_id"])
                    
                    return models.LinkGetOutput(**equations) # Create an instance of LinkGetOutput
            

        else:
            
            raise HTTPException(status_code=404, detail="Equation not found")
    else:
        
        raise HTTPException(status_code=404, detail="Equation not found")
    
        
    


@equation_router.post("/delete/{id}")
async def delete_equation(id: str, user_email = Depends(jwt_decoder.get_current_user)):
    # user = get_current_user(token)
    # print("user", user)
    # user_email = dict(user_email)["user_email"]
    print("Delete", user_email) 
    if user_email :
        # user = dict(user)
        # print(user["email"])
        result = configurations.collection.delete_one({"_id": ObjectId(id), "email": user_email})
        
        if result.deleted_count == 1:
            
            return JSONResponse(content={"message": "Equation deleted successfully."}, status_code=200)
        else:
            
            return JSONResponse(content={"message": "Equation not found."}, status_code=404)

@equation_router.post("/save-as/")
async def get_equations(equation: models.Equation, user_email = Depends(jwt_decoder.get_current_user)): 
    
    
    equation_dict = dict(equation)
    
    print("save-as", user_email)
    
    if user_email :
        
        if len(equation_dict["title"]) == 0 :
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The 'title' field is required.",
            headers={"WWW-Authenticate": "Bearer"}
        )
        if len(equation_dict["scanCategory"]) == 0 :
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The 'Scan Category' field is required.",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
        # temp_str = title_to_string(equation_dict["title"])
        
        # result = configurations.collection.find({"link": {"$regex": temp_str, "$options": "i"}}, {"link": 1})
        
        # result = list(result)
        
        # result = [item['link'] for item in result]
        
        # if len(result) > 0:
        #     temp_str = get_unique_link(temp_str, result)
            
        # equation_dict["link"] = temp_str'

        equation_dict["link"] = generate_unique_slug(equation_dict["title"])

        equation_dict["updated_at"] = get_datetime_now()
        equation_dict["created"] = get_datetime_now()
        equation_dict["email"] = user_email
        equation_dict["likes"] = 0
        equation_dict["dislikes"] = 0
        
        new_doc = "empty value"
        
        while new_doc:
            new_doc = configurations.collection.find_one_and_update(
                {"link": equation_dict["link"]},                # Query to check if link exists   "new-data-copy-1"}, #
                {"$setOnInsert": equation_dict},                # Insert these fields if not found
                upsert=True,                                    # Create document if it doesn't exist
                # return_document=ReturnDocument.AFTER            # Return the document after the operation
                )
        # print(new_doc["created"], equation_dict["created"])
            # print(new_doc)
            # print(" new link", equation_dict["link"])
            if new_doc is None:
                return equation_dict["link"]
            else:
                equation_dict["link"] = generate_unique_slug(equation_dict["title"])
                # time.sleep(5)


        # result = configurations.collection.insert_one(equation_dict)
        # equation_dict["_id"] = str(result.inserted_id)
        # print(equation_dict["link"])
        

            
       

    else:
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
     

@equation_router.put("/{id}")
async def get_equations(id: str, equation: models.Equation, user_email = Depends(jwt_decoder.get_current_user) ):
    # user = get_current_user(token)
    # print("user", user)
    # print("equation")
    # print(equation)
    # user_email = dict(user_email)["user_email"]

    equation_dict = dict(equation)
    # user_email = equation_dict["user_email"]
    print("save", user_email)
    # equation_dict.pop("user_email", None)
    if user_email :
        print("dict(equation) PUT") 
        # ist_timezone = pytz.timezone("Asia/Kolkata")
        # ist = datetime.now(ist_timezone)
        # currect_time = ist.strftime("%Y-%m-%d %H:%M:%S")
        # currect_time = datetime.strptime(currect_time, "%Y-%m-%d %H:%M:%S")
        
        # equation_dict = dict(equation)
        
        equation_dict["updated_at"] = get_datetime_now()
        # print(equation_dict)
        # equation_dict["_id"] = ObjectId(equation_dict["_id"])
        res = configurations.collection.update_one({"_id": ObjectId(id), "email": user_email }, {"$set": equation_dict})
        # print(res)
        # res = dict(res)
        raw = res.raw_result
        updated_existing = raw.get("updatedExisting")
        print("updated_existing", updated_existing)
        if updated_existing == True:
            return {"message": "Strategy Saved!"}
        else:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    else:
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

