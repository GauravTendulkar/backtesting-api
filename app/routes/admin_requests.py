
from fastapi import FastAPI, Request, APIRouter, BackgroundTasks, File, UploadFile
from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Body, Security

from bson import ObjectId

from fastapi import APIRouter
from pydantic import BaseModel, field_validator, Field
from typing import List, Optional, Union

from fastapi import APIRouter, UploadFile, File, Form

from ..raw_data_management import (data_list, new_file_upload, upload_by_chunk, 
                                   upload_progress, get_file_names, delete_file_one_by_one, run_in_thread, thread_pool)

from ..database.mongodb.repositories import roles_collection, social_user_collection, groups_collection, permissions_collection

from ..roles_and_permission import (get_user_roles, get_all_roles_from_db, add_role, save_roles ,
                                    save_permission,
                                    get_paginated_groups, add_group, save_group, get_group_count,
                                    delete_role)

from ..auth.id_password_auth import get_current_user

from ..admin import run_once_combined_duckdb

admin_dashboard = APIRouter()




class UserEmail(BaseModel):
    user_email: Optional[str] = None


class GetRolesRequest(BaseModel):
    dummy: str

@admin_dashboard.post("/get-roles")
async def get_user_permissions(user_email=Depends(get_current_user)):
    print("User email from token:", user_email)

    
    return get_user_roles(user_email)

    

#____________________________________________________________________________


@admin_dashboard.get("/file-folder")
async def upload_file_list():
    return data_list
# --------------------------************************

# UPLOAD_DIR = "Clean_data/newData"
# TEMP_DIR = f"{SHARED_FILES_PATH}/Clean_data/temp_chunks"

# admin_dashboard = APIRouter(prefix="/backend/api/admin-dashboard")

# ─── Original multi-file upload (small files) ───────────────────────────────
@admin_dashboard.post("/upload-new-data")
async def upload_files(files: List[UploadFile] = File(...)):
    
    return new_file_upload(files)


# ─── Chunked upload (large files) ────────────────────────────────────────────
@admin_dashboard.post("/upload-chunk")
async def upload_chunk(
    file: UploadFile = File(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    file_name: str = Form(...),
):
    return await upload_by_chunk(file, chunk_index, total_chunks, file_name)


# ─── Check if upload already partially done (resume support) ─────────────────
@admin_dashboard.get("/upload-progress/{file_name}")
async def get_upload_progress(file_name: str):
    return upload_progress(file_name)

# --------------------------------------------------------******************

class FolderName(BaseModel):
    folder_name: str

@admin_dashboard.post("/get-new-data-name")
async def get_upload_file_names(data : FolderName):
    # print(data.folder_name)
    # print(data)
    file_name = get_file_names(data.folder_name)

    return file_name




class FileDeleteRequest(BaseModel):
    files_list: List[str]
    folder_name: str

@admin_dashboard.post("/delete-new-data-name")
async def delete_upload_file_names(payload: FileDeleteRequest):
    return delete_file_one_by_one(payload)


@admin_dashboard.post("/update-new-data")
async def delete_upload_file_names():
    
    try:
        # await run_in_thread(newData_concat.run_once_combined())
        await run_in_thread(run_once_combined_duckdb(), thread_pool)
        
        
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
    # roles = list(roles_collection.get_all_roles())
    # for r in roles:
    #     r["id"] = str(r.pop("_id"))
    # return roles
    return get_all_roles_from_db()

@admin_dashboard.get("/get-all-role-names")
async def get_all_roles():
    roles = roles_collection.get_all_role_names()
    return roles

@admin_dashboard.post("/add-roles")
async def add_roles(data: RoleModel):
    # role_name = data.role_name.strip().lower()
    # if roles_collection.get_one_role_name(role_name):
    #     raise HTTPException(status_code=400, detail="Role already exists")
   
    # result = roles_collection.insert_one(role_name, True, [])
    # return {"message": "Role added successfully", "role_id": str(result.inserted_id)}
    return add_role(data)

@admin_dashboard.delete("/delete-role/{role_id}")
async def delete_role_temp(role_id: str):
    # try:
    #     res = roles_collection.delete_one_role(role_id)
    #     if res.deleted_count == 0:
    #         raise HTTPException(status_code=404, detail="Role not found")
    #     return {"message": "Role deleted"}
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))
    delete_role(role_id)

@admin_dashboard.post("/save-role")
async def save_role(data: RoleModel):
    
    return save_roles(data)



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
    
    temp = permissions_collection.get_all_permissions()
    return temp

# POST save permissions (unique + lowercase enforced)
@admin_dashboard.post("/permissions/save")
def save_permissions(data: dict):
    # permissions = data.get("permissions", [])

    # # Deduplicate by permission name (last one wins)
    # unique = {}
    # for perm in permissions:
    #     name = perm["permissions_name"].strip().lower()
    #     unique[name] = {
    #         "permissions_name": name,
    #         "isActive": perm["isActive"]
    #     }

    # # Replace all in DB
    
    # permissions_collection.delete_all()
    # if unique:
        
    #     permissions_collection.insert_all(list(unique.values()))
        
    # return {"status": "success"}
    return save_permission(data)





#_____________________________________________________________________ Groups








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
    # query = {}
    # if search:
    #     query = {"group_name": {"$regex": search, "$options": "i"}}

    
    # cursor = groups_collection.find_skip_limit(query, skip, limit)
    # groups = []
    # for g in cursor:
    #     g["id"] = str_objectid(g["_id"])
    #     del g["_id"]
    #     groups.append(g)
    # return groups
    return get_paginated_groups(search, skip, limit)


# ✅ Count total groups (for pagination)
@admin_dashboard.get("/groups/count")
def get_group_count_temp(search: Optional[str] = None):
    # query = {}
    # if search:
    #     query["group_name"] = {"$regex": search, "$options": "i"}

    
    # total = groups_collection.get_count(query)
    # return {"total": total}
    return get_group_count(search)


# ✅ Create new group
@admin_dashboard.post("/groups/create")
def create_group(data: Group):
    # group_data = data.model_dump()
    # group_data["group_name"] = group_data["group_name"].strip().lower()

    # # Check for existing group
    # if groups_collection.get_one_group_name(group_data["group_name"]):
    #     raise HTTPException(status_code=400, detail="Group name already exists")

    # # Insert into DB
    # result = groups_collection.insert_one_group(group_data)

    # # Clean return object: include only stringified ID
    # return {
    #     "status": "success",
    #     "group": {
    #         "id": str(result.inserted_id),
    #         "group_name": group_data["group_name"],
    #         "isActive": group_data["isActive"],
    #         "permissions": group_data["permissions"]
    #     }
    # }
    return add_group(data)



# ✅ Save/update group by ID only (no name check)
@admin_dashboard.post("/groups/save")
def root(data: Group):
    # group_data = data.model_dump()
    # group_data["group_name"] = group_data["group_name"].strip().lower()

    # if data.id:
    #     try:
    #         group_oid = ObjectId(data.id)
    #     except Exception:
    #         raise HTTPException(status_code=400, detail="Invalid group ID")

    #     result = groups_collection.update_one_by_id(group_oid, group_data)

    #     if result.matched_count == 0:
    #         raise HTTPException(status_code=404, detail="Group not found")

    #     group_data["id"] = str(group_oid)
    #     return {"status": "success", "group": group_data}

    # else:
    #     if groups_collection.get_one_group_name(group_data["group_name"]):
    #         raise HTTPException(status_code=400, detail="Group name already exists")

    #     result = groups_collection.insert_one_group(group_data)

    #     group_data["id"] = str(result.inserted_id)
    #     return {"status": "success", "group": group_data}
    return save_group(data)

# ✅ Delete group by ID
@admin_dashboard.delete("/groups/delete/{group_id}")
def delete_group(group_id: str):
    # try:
    #     group_oid = ObjectId(group_id)
    # except Exception:
    #     raise HTTPException(status_code=400, detail="Invalid ID")

    # # result = configurations.collection_groups.delete_one({"_id": group_oid})  
    # result = groups_collection.delete_one_with_id(group_oid)
    # if result.deleted_count == 0:
    #     raise HTTPException(status_code=404, detail="Group not found")
    # return {"status": "deleted"}
    return delete_group(group_id)

