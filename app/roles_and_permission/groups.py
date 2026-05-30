from ..database.mongodb.repositories import roles_collection, social_user_collection, groups_collection, permissions_collection
from bson import ObjectId
from fastapi import  HTTPException


def str_objectid(id):
    return str(id) if isinstance(id, ObjectId) else id


# /groups

def get_paginated_groups(search, skip, limit ):
    query = {}
    if search:
        query = {"group_name": {"$regex": search, "$options": "i"}}

    
    cursor = groups_collection.find_skip_limit(query, skip, limit)
    groups = []
    for g in cursor:
        g["id"] = str_objectid(g["_id"])
        del g["_id"]
        groups.append(g)
    return groups

# /groups/count
def get_group_count(search):
    query = {}
    if search:
        query["group_name"] = {"$regex": search, "$options": "i"}

    
    total = groups_collection.get_count(query)
    return {"total": total}


# /groups/create

def add_group(data):
    group_data = data.model_dump()
    group_data["group_name"] = group_data["group_name"].strip().lower()

    # Check for existing group
    if groups_collection.get_one_group_name(group_data["group_name"]):
        raise HTTPException(status_code=400, detail="Group name already exists")

    # Insert into DB
    result = groups_collection.insert_one_group(group_data)

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

# /groups/save

def save_group(data):
    group_data = data.model_dump()
    group_data["group_name"] = group_data["group_name"].strip().lower()

    if data.id:
        try:
            group_oid = ObjectId(data.id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid group ID")

        result = groups_collection.update_one_by_id(group_oid, group_data)

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Group not found")

        group_data["id"] = str(group_oid)
        return {"status": "success", "group": group_data}

    else:
        if groups_collection.get_one_group_name(group_data["group_name"]):
            raise HTTPException(status_code=400, detail="Group name already exists")

        result = groups_collection.insert_one_group(group_data)

        group_data["id"] = str(result.inserted_id)
        return {"status": "success", "group": group_data}
    

# /groups/delete/{group_id}

def delete_group(group_id):
    try:
        group_oid = ObjectId(group_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")

    # result = configurations.collection_groups.delete_one({"_id": group_oid})  
    result = groups_collection.delete_one_with_id(group_oid)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Group not found")
    return {"status": "deleted"}