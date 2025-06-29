
from fastapi import FastAPI, Request, APIRouter, BackgroundTasks, File, UploadFile
from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Body, Security

from admin_dashboard import admin_function
from database import configurations

import os
import shutil

from functions import df_saving, newData_concat, fastCache_saving
from functions_v1 import memory
from typing import Dict, List
from pydantic import BaseModel
import asyncio
from functools import partial
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Optional
from pydantic import BaseModel
from typing import  List
from bson import ObjectId
import json




admin_dashboard = APIRouter()


# permissions_list = [
# ""
# ]

class UserEmail(BaseModel):
    user_email: Optional[str] = None


@admin_dashboard.post("/get-roles")
async def get_stock_list(user_email : UserEmail = Body(...)):
    print("admin_dashboard",user_email)
    user_email = dict(user_email)["user_email"]
    # data = {
    #     "admin" : {"createScan.run" :True},
    #     "user" : {"createScan.run" :True }
    # }
    if user_email != None:
        # get user roles from database
        role = configurations.collection_social_user.find_one({"email": user_email }, {"roles": 1})
        role = dict(role)
        print(role)
        role = role["roles"]
        # role = ["admin"]

        # get active roles from permissions from db or cache
        data = configurations.collection_roles.find(
            {"role_title": {"$in": role}}, 
            {"_id" : 0}
            )
        data = list(data)
        if len(data) > 0:
            temp = {}
            for i in data:
                temp[i["role_title"] ] = i["permissions"]
            data = temp
            
            all_permissions = []
            for i in range(len(role)):
                get_keys = list(data[role[i]].keys() )
                for j in range(len(get_keys)):
                    if  data[role[i]][get_keys[j]] == True and get_keys[j] not in all_permissions:
                        
                        all_permissions.append(get_keys[j])
            return all_permissions  
        else:
            return []





data_list = ["Clean_data/newData", "Clean_data/1min", "Clean_data/RAW_daily_data_tradingview", "indicator_process", "fastCache"]
@admin_dashboard.get("/file-folder")
async def upload_file_list():
    return data_list


UPLOAD_DIR = "Clean_data/newData"

@admin_dashboard.post("/upload-new-data")
async def upload_file(file: UploadFile = File(...)):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file_location = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename, "message": "File saved successfully"}


def get_file_names(folder_name):
    # List all files and directories in a path
    files = os.listdir(folder_name)  # Replace with your path
    try:
        files.remove(".gitkeep")
        
    except:
        pass
    files_details = []
    for i in range(0, len(files)):
        temp = {}
        temp["file_name"] = files[i]
        a = files[i].split(".")
        print("a", a)
        
        if "csv" == a[1] or "parquet" == a[1] or "feather" == a[1] or "pickle" == a[1]:
            if folder_name == "fastCache":
                # print()
                if len(a) < 3:
                    df_clean = fastCache_saving.read_file(f"{folder_name}/{a[0]}", extension = f".{a[1]}")
                    # temp["last_date"] = str(df_clean.index[-1])
                    temp["last_date"] = int(df_clean.loc[df_clean.index[-1] ,"date_number"])
                else:
                    temp["last_date"] = 0
            else:
                if len(a) < 3:
                    df_clean = df_saving.read_file(f"{folder_name}/{a[0]}", extension = f".{a[1]}")
                    temp["last_date"] = str(df_clean.index[-1])
                else:
                    temp["last_date"] = 0
                
        else:
            temp["last_date"] = 0
        

        m_size = memory.sizeof_fmt(os.path.getsize(f"{folder_name}/{files[i]}"),  unit="Mi")
        m_size[0] = round(m_size[0],2)
        temp["file_size"] = m_size
        
        files_details.append(temp)

    return files_details

class FolderName(BaseModel):
    folder_name: str

@admin_dashboard.post("/get-new-data-name")
async def get_upload_file_names(data : FolderName):
    # print(data.folder_name)
    file_name = get_file_names(data.folder_name)

    return file_name




class FileDeleteRequest(BaseModel):
    files_list: List[str]
    folder_name: str

@admin_dashboard.post("/delete-new-data-name")
async def delete_upload_file_names(payload: FileDeleteRequest):
    for file_name in payload.files_list:
        try:
            os.remove(f"{payload.folder_name}/{file_name}")
        except:
            pass
    return {"status": "success"}

thread_pool = ThreadPoolExecutor(max_workers=1)


async def run_in_thread(func):
    """Run function in thread pool"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(thread_pool, partial(func))

@admin_dashboard.post("/update-new-data")
async def delete_upload_file_names():
    
    try:
        await run_in_thread(newData_concat.run_once_combined())
        
    except:
        pass
    return {"status": "success"}






PERMISSIONS_FILE = "permissions.json"

# ----------------------------
# Models
# ----------------------------
class Role(BaseModel):
    role_title: str
    permissions: Dict[str, bool] = {}

# ----------------------------
# Get All Roles
# ----------------------------
@admin_dashboard.get("/get-all-roles")
async def get_all_roles():
    data = list(configurations.collection_roles.find())
    for doc in data:
        doc["_id"] = str(doc["_id"])
    return data

# ----------------------------
# Create Role
# ----------------------------
@admin_dashboard.post("/create-role")
async def create_role(role: Role):
    result = configurations.collection_roles.insert_one(role.dict())
    return {"_id": str(result.inserted_id)}

# ----------------------------
# Update Role
# ----------------------------
@admin_dashboard.put("/update-role/{role_id}")
async def update_role(role_id: str, updated_role: Role):
    result = configurations.collection_roles.update_one(
        {"_id": ObjectId(role_id)},
        {"$set": updated_role.dict()}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Role not found or no change")
    return {"message": "Role updated successfully"}

# ----------------------------
# Delete Role
# ----------------------------
@admin_dashboard.delete("/delete-role/{role_id}")
async def delete_role(role_id: str):
    result = configurations.collection_roles.delete_one({"_id": ObjectId(role_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted successfully"}

# ----------------------------
# Get Permissions from permissions.json
# ----------------------------
@admin_dashboard.get("/get-permissions")
async def get_permissions():
    if not os.path.exists(PERMISSIONS_FILE):
        return []
    with open(PERMISSIONS_FILE, "r") as f:
        return json.load(f)

# ----------------------------
# Update Permission Options in permissions.json
# ----------------------------
@admin_dashboard.put("/update-permissions")
async def update_permissions(permissions: List[str]):
    with open(PERMISSIONS_FILE, "w") as f:
        json.dump(permissions, f)
    return {"message": "Permissions updated"}

# ----------------------------
# Add Permission Option to permissions.json
# ----------------------------
@admin_dashboard.post("/add-permission")
async def add_permission(permission: str):
    permissions = []
    if os.path.exists(PERMISSIONS_FILE):
        with open(PERMISSIONS_FILE, "r") as f:
            permissions = json.load(f)
    if permission not in permissions:
        permissions.append(permission)
        with open(PERMISSIONS_FILE, "w") as f:
            json.dump(permissions, f)
    return {"message": "Permission added"}

# ----------------------------
# Delete Permission Option from permissions.json
# ----------------------------
@admin_dashboard.delete("/delete-permission/{permission}")
async def delete_permission(permission: str):
    if not os.path.exists(PERMISSIONS_FILE):
        raise HTTPException(status_code=404, detail="Permission list not found")
    with open(PERMISSIONS_FILE, "r") as f:
        permissions = json.load(f)
    if permission in permissions:
        permissions.remove(permission)
        with open(PERMISSIONS_FILE, "w") as f:
            json.dump(permissions, f)
    return {"message": "Permission deleted"}

# ----------------------------
# Import Roles
# ----------------------------
@admin_dashboard.post("/import-roles")
async def import_roles(roles: List[Role]):
    documents = [role.dict() for role in roles]
    configurations.collection_roles.delete_many({})
    configurations.collection_roles.insert_many(documents)
    return {"message": "Roles imported successfully"}
