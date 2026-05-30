from ..database.mongodb.repositories import roles_collection, social_user_collection, groups_collection, permissions_collection
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import List, Optional, Union
from fastapi import  HTTPException
from bson import ObjectId
from ..roles_and_permission import admin_roles_permission_list


class UserEmail(BaseModel):
    user_email: Optional[str] = None

def getRoles(roles_data: List[dict]) -> List[str]:
    

    if not roles_data:
        return []

    valid_roles = []
    now = datetime.now(timezone.utc)
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    now = datetime.strptime(now, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    # print("now", now)
    for role in roles_data:
        if not role.get("isActive", True):
            continue

        limit = role.get("limit", "unlimited")
        # print(limit)
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
    
    

    
    role_docs = roles_collection.get_roles_from_list(valid_roles)

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


# endpoint # /get-roles
def get_user_roles(user_email : str) -> List[str] :
    if user_email:
        
        user = social_user_collection.get_user_roles(user_email)
        roles_data = user.get("roles", []) if user else []
    else:
        roles_data = [{"name": "user-logout", "isActive": True, "limit": "unlimited"}]

    permissions = getRoles(roles_data)


    return permissions


# /get-all-roles
def get_all_roles_from_db():
    roles = list(roles_collection.get_all_roles())
    for r in roles:
        r["id"] = str(r.pop("_id"))
    return roles
     


#  /add-roles
def add_role(data):
    role_name = data.role_name.strip().lower()
    if roles_collection.get_one_role_name(role_name):
        raise HTTPException(status_code=400, detail="Role already exists")
   
    result = roles_collection.insert_one(role_name, True, [])
    return {"message": "Role added successfully", "role_id": str(result.inserted_id)}

# /delete-role/{role_id}
def delete_role(role_id): 
    
    try:
        res = roles_collection.delete_one_role(role_id)
        if res.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Role not found")
        return {"message": "Role deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# /save-role
def save_roles(data):
    try:
        if not data.id:
            raise HTTPException(status_code=400, detail="Missing role ID")

        role_id = ObjectId(data.id)
        data.role_name = data.role_name.strip().lower()

        role_dict = data.dict(exclude={"id"})

        # Populate permissions for groups
        for idx, item in enumerate(role_dict["groups_permissions"]):
            if "group_name" in item and not item.get("permissions"):
                group = groups_collection.get_one_group_name(item["group_name"])
                if group:
                    permissions = group.get("permissions", [])
                    role_dict["groups_permissions"][idx]["permissions"] = permissions

        # Save the updated role
        
        roles_collection.update_with_id(data.id, role_dict)

        return {"status": "success", "role": data.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

def create_admin_roles_if_not_exists():
    admin_permission_list = admin_roles_permission_list.ADMIN_PERMISSION_LIST
    
    for i in range(0, len(admin_permission_list)):
        admin_permission_list[i] = { "permissions_name": admin_permission_list[i], "isActive": True }
    # admin
    roles_collection.update_if_not_exist(
        {"role_name": "admin"},   # filter
        {
            "$setOnInsert": {
                "role_name": "admin",
                "isActive": True,
                "groups_permissions": admin_permission_list
            }
        },
        upsert=True
    )
    # user-login
    roles_collection.update_if_not_exist(
        {"role_name": "user-login"},   # filter
        {
            "$setOnInsert": {
                "role_name": "user-login",
                "isActive": True,
                "groups_permissions": []
            }
        },
        upsert=True
    )
    # user-logout
    roles_collection.update_if_not_exist(
        {"role_name": "user-logout"},   # filter
        {
            "$setOnInsert": {
                "role_name": "user-logout",
                "isActive": True,
                "groups_permissions": []
            }
        },
        upsert=True
    )
 

    