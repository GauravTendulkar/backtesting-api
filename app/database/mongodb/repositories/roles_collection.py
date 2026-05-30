from ..database import db
from bson import ObjectId


collection_roles = db["roles"]

# ______find_____________________

def get_all_roles():
    return collection_roles.find()  


def get_all_role_names():
    roles =  list(collection_roles.find({},{"role_name": 1}))
    for r in roles:
        r["id"] = str(r.pop("_id"))
    return roles

def get_one_role_name(role_name):
    return collection_roles.find_one({"role_name": role_name}) 


# ______insert_____________________

def insert_one(role_name, isActive, groups_permissions):
    return collection_roles.insert_one({
        "role_name": role_name,
        "isActive": isActive,
        "groups_permissions": groups_permissions
    })

def delete_one_role(role_id):

    return collection_roles.delete_one({"_id": ObjectId(role_id)})

# ______update_____________________


def update_with_id(role_id, role_dict):
    role_id =  ObjectId(role_id)
    collection_roles.update_one(
            {"_id": role_id},
            {"$set": role_dict}
        )


def get_roles_from_list(valid_roles):

    role_docs = collection_roles.find(
        {"role_name": {"$in": valid_roles}},
        {"_id": 0, "role_name": 1, "groups_permissions": 1, "isActive": 1}
    )
    role_docs = list(role_docs)
    return role_docs


def update_if_not_exist(filter_query, update_query, upsert=False):
    return collection_roles.update_one(
        filter_query,
        update_query,
        upsert=upsert
    )



# Creating index
try:
    collection_roles.create_index(
        "role_name",
        unique=True
    )
except :
    pass