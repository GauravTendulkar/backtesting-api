
from fastapi import FastAPI, Request, APIRouter, BackgroundTasks, File, UploadFile
from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Body, Security

from admin_dashboard import admin_function
from database import configurations

import os
import shutil
from functions import df_saving, newData_concat, fastCache_saving
from functions_v1 import memory
from typing import Dict, List
import asyncio
from functools import partial
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Optional
from bson import ObjectId
from database import jwt_decoder
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator, Field
from typing import List, Optional, Union
from datetime import datetime
from typing import Optional, List
from database import configurations
from fastapi import APIRouter
from bson import ObjectId
from datetime import datetime, timezone

admin_dashboard = APIRouter()




class UserEmail(BaseModel):
    user_email: Optional[str] = None

def getRoles(roles_data: List[dict]) -> List[str]:
    

    if not roles_data:
        return []

    valid_roles = []
    now = datetime.now(timezone.utc)
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    now = datetime.strptime(now, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    print("now", now)
    for role in roles_data:
        if not role.get("isActive", True):
            continue

        limit = role.get("limit", "unlimited")
        print(limit)
        if limit == "limited":
            try:
                end_date = role.get("end_date")
                end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")
                end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                print("end_date", end_date, type(end_date))
                if end_date < now:
                    continue
            except:
                continue

        valid_roles.append(role.get("name"))

    if not valid_roles:
        return []
    
    

    # Fetch roles from DB
    role_docs = configurations.collection_roles.find(
        {"role_name": {"$in": valid_roles}},
        {"_id": 0, "role_name": 1, "groups_permissions": 1, "isActive": 1}
    )
    role_docs = list(role_docs)

    all_permissions = set()
    
    for role in role_docs:
        if role["isActive"]:
            
            for gp in role["groups_permissions"]:
                if gp["isActive"]:
                    
                    keys = gp.keys()
                    if "permissions_name" in keys:
                        if gp["isActive"]:
                            
                            all_permissions.add(gp["permissions_name"])
                    if "group_name" in keys:
                        if gp["isActive"]:
                            for p in gp["permissions"]:
                                if p["isActive"]:
                                    
                                    all_permissions.add(p["permissions_name"])

    return list(all_permissions)

class GetRolesRequest(BaseModel):
    dummy: str

@admin_dashboard.post("/get-roles")
async def get_user_permissions(user_email=Depends(jwt_decoder.get_current_user)):
    print("User email from token:", user_email)

    if user_email:
        user = configurations.collection_social_user.find_one(
            {"email": user_email},
            {"roles": 1}
        )
        roles_data = user.get("roles", []) if user else []
    else:
        roles_data = [{"name": "user-logout", "isActive": True, "limit": "unlimited"}]

    permissions = getRoles(roles_data)
    print("Final permissions:", permissions)
    return permissions
#     return ["createScan.run", 
# "admin-dashboard", 
# "admin-dashboard.upload", 
# "admin-dashboard.roles", 
# "admin-dashboard.permissions", 
# "admin-dashboard.user-role-manager", 
# "stock-list", 
# "dashboard", 
# "categories", 
# "strategy-builder", 
# "home-page"]

#____________________________________________________________________________

data_list = ["Clean_data/newData", "Clean_data/1min", "Clean_data/RAW_daily_data_tradingview", "indicator_process", "fastCache"]
@admin_dashboard.get("/file-folder")
async def upload_file_list():
    return data_list


UPLOAD_DIR = "Clean_data/newData"

@admin_dashboard.post("/upload-new-data")
async def upload_files(files: List[UploadFile] = File(...)):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    saved_files = []

    for file in files:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(file.filename)

    return {"message": "Files uploaded successfully", "files": saved_files}


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
        # print("a", a)
        
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






#_____________________________________________________________________ ROLES









class PermissionModel(BaseModel):
    permissions_name: str
    isActive: bool = True

class GroupModel(BaseModel):
    group_name: str
    isActive: bool = True
    permissions: List[PermissionModel] = []

class FlatPermissionModel(BaseModel):
    permissions_name: str
    isActive: bool = True

class RoleModel(BaseModel):
    id: Optional[str] = None
    role_name: str
    isActive: bool = True
    groups_permissions: List[Union[GroupModel, FlatPermissionModel]] = []

@admin_dashboard.get("/get-all-roles")
async def get_all_roles():
    roles = list(configurations.collection_roles.find())
    for r in roles:
        r["id"] = str(r.pop("_id"))
    return roles

@admin_dashboard.get("/get-all-role-names")
async def get_all_roles():
    roles = list(configurations.collection_roles.find({},{"role_name": 1}))
    for r in roles:
        r["id"] = str(r.pop("_id"))
    return roles

@admin_dashboard.post("/add-roles")
async def add_roles(data: RoleModel):
    role_name = data.role_name.strip().lower()
    if configurations.collection_roles.find_one({"role_name": role_name}):
        raise HTTPException(status_code=400, detail="Role already exists")
    result = configurations.collection_roles.insert_one({
        "role_name": role_name,
        "isActive": True,
        "groups_permissions": []
    })
    return {"message": "Role added successfully", "role_id": str(result.inserted_id)}

@admin_dashboard.delete("/delete-role/{role_id}")
async def delete_role(role_id: str):
    try:
        res = configurations.collection_roles.delete_one({"_id": ObjectId(role_id)})
        if res.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Role not found")
        return {"message": "Role deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@admin_dashboard.post("/save-role")
async def save_role(data: RoleModel):
    try:
        if not data.id:
            raise HTTPException(status_code=400, detail="Missing role ID")

        role_id = ObjectId(data.id)
        data.role_name = data.role_name.strip().lower()

        role_dict = data.dict(exclude={"id"})

        # Populate permissions for groups
        for idx, item in enumerate(role_dict["groups_permissions"]):
            if "group_name" in item and not item.get("permissions"):
                group = configurations.collection_groups.find_one({"group_name": item["group_name"]})
                if group:
                    permissions = group.get("permissions", [])
                    role_dict["groups_permissions"][idx]["permissions"] = permissions

        # Save the updated role
        configurations.collection_roles.update_one(
            {"_id": role_id},
            {"$set": role_dict}
        )

        return {"status": "success", "role": data.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



#_____________________________________________________________________ Permissions

class Permission(BaseModel):
    permissions_name: str
    isActive: bool

    @field_validator("permissions_name")
    @classmethod
    def lowercase_and_strip(cls, v: str) -> str:
        return v.strip().lower()

# GET all permissions
@admin_dashboard.get("/permissions")
def get_permissions():
    temp = list(configurations.collection_permissions.find({}, {"_id": 0}))
    return temp

# POST save permissions (unique + lowercase enforced)
@admin_dashboard.post("/permissions/save")
def save_permissions(data: dict):
    permissions = data.get("permissions", [])

    # Deduplicate by permission name (last one wins)
    unique = {}
    for perm in permissions:
        name = perm["permissions_name"].strip().lower()
        unique[name] = {
            "permissions_name": name,
            "isActive": perm["isActive"]
        }

    # Replace all in DB
    configurations.collection_permissions.delete_many({})
    if unique:
        configurations.collection_permissions.insert_many(list(unique.values()))
    return {"status": "success"}





#_____________________________________________________________________ Groups





def str_objectid(id):
    return str(id) if isinstance(id, ObjectId) else id


# ----------------------------- MODELS -----------------------------

class Permission(BaseModel):
    permissions_name: str
    isActive: bool


class Group(BaseModel):
    id: Optional[str] = None  # Using `id` instead of `_id` for Pydantic compatibility
    group_name: str
    isActive: bool
    permissions: List[Permission] = []

    @field_validator("group_name")
    @classmethod
    def lowercase_and_strip(cls, v: str) -> str:
        return v.strip().lower()




# ✅ Get paginated groups
@admin_dashboard.get("/groups")
def get_groups(skip: int = 0, limit: int = 5, search: Optional[str] = None):
    query = {}
    if search:
        query = {"group_name": {"$regex": search, "$options": "i"}}

    cursor = configurations.collection_groups.find(query).skip(skip).limit(limit)
    groups = []
    for g in cursor:
        g["id"] = str_objectid(g["_id"])
        del g["_id"]
        groups.append(g)
    return groups


# ✅ Count total groups (for pagination)
@admin_dashboard.get("/groups/count")
def get_group_count(search: Optional[str] = None):
    query = {}
    if search:
        query["group_name"] = {"$regex": search, "$options": "i"}
    total = configurations.collection_groups.count_documents(query)
    return {"total": total}


# ✅ Create new group
@admin_dashboard.post("/groups/create")
def create_group(data: Group):
    group_data = data.model_dump()
    group_data["group_name"] = group_data["group_name"].strip().lower()

    # Check for existing group
    if configurations.collection_groups.find_one({"group_name": group_data["group_name"]}):
        raise HTTPException(status_code=400, detail="Group name already exists")

    # Insert into DB
    result = configurations.collection_groups.insert_one(group_data)

    # Clean return object: include only stringified ID
    return {
        "status": "success",
        "group": {
            "id": str(result.inserted_id),
            "group_name": group_data["group_name"],
            "isActive": group_data["isActive"],
            "permissions": group_data["permissions"]
        }
    }



# ✅ Save/update group by ID only (no name check)
@admin_dashboard.post("/groups/save")
def save_group(data: Group):
    group_data = data.model_dump()
    group_data["group_name"] = group_data["group_name"].strip().lower()

    if data.id:
        try:
            group_oid = ObjectId(data.id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid group ID")

        result = configurations.collection_groups.update_one(
            {"_id": group_oid},
            {"$set": {
                "group_name": group_data["group_name"],
                "isActive": group_data["isActive"],
                "permissions": group_data["permissions"]
            }}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Group not found")

        group_data["id"] = str(group_oid)
        return {"status": "success", "group": group_data}

    else:
        if configurations.collection_groups.find_one({"group_name": group_data["group_name"]}):
            raise HTTPException(status_code=400, detail="Group name already exists")

        result = configurations.collection_groups.insert_one(group_data)
        group_data["id"] = str(result.inserted_id)
        return {"status": "success", "group": group_data}


# ✅ Delete group by ID
@admin_dashboard.delete("/groups/delete/{group_id}")
def delete_group(group_id: str):
    try:
        group_oid = ObjectId(group_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")

    result = configurations.collection_groups.delete_one({"_id": group_oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Group not found")
    return {"status": "deleted"}