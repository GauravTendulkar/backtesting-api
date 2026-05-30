from ..database import db
from bson import ObjectId


collection_groups = db["groups"]


# ______find_____________________
def get_one_group_name(item):
    return collection_groups.find_one({"group_name": item})


def find_skip_limit(query, skip, limit):
    cursor = collection_groups.find(query).skip(skip).limit(limit)
    return cursor

# ______count_____________________
def get_count(query):
    return collection_groups.count_documents(query)


# def get_one_group_name(data):
#     return collection_groups.find_one({"group_name": data})


# ______insert_____________________
def insert_one_group(group_data):
    return collection_groups.insert_one(group_data)

# ______update_____________________

def update_one_by_id(group_oid, group_data):
    return collection_groups.update_one(
            {"_id": group_oid},
            {"$set": {
                "group_name": group_data["group_name"],
                "isActive": group_data["isActive"],
                "permissions": group_data["permissions"]
            }}
        )


# ______delete_____________________

def delete_one_with_id(id):
    if type(id) == str:
        id = ObjectId(id)
    return collection_groups.delete_one({"_id": id})


