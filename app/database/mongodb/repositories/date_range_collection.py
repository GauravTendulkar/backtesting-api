from ..database import db
from bson import ObjectId

collection_date_range = db["date_range"]

def get_all_date_range():
    data = list(collection_date_range.find({}))
    for d in data:
        d["_id"] = str(d["_id"]) 
    return data

def find_one_role_name(role_name):
    return collection_date_range.find_one({"role_name": role_name})

def update_one_with_id(id, data):
    update = {
        "role_name": data["role_name"],
        "date_range": data["date_range"]
    }
    return collection_date_range.update_one({"_id": ObjectId(id)}, {"$set": update})


def insert_one(role_name, date_range):
    return collection_date_range.insert_one({
        "role_name": role_name,
        "date_range": date_range
    })


def delete_one_with_id(id):
    return collection_date_range.delete_one({"_id": ObjectId(id)})

def find_all_active_roles(active_roles):
    return  collection_date_range.find(
                {"role_name": {"$in": active_roles}}
            )


