from ..database import db
from bson import ObjectId

collection_social_user = db["social_user"]

# _________find__________________
def get_user_roles(user_email):
    return collection_social_user.find_one(
            {"email": user_email},
            {"roles": 1}
        )
def get_one_with_id(id):
    return collection_social_user.find_one({"_id": ObjectId(id)})
 
def get_one_with_email(email):
    return collection_social_user.find_one({"email": email}, {"_id": 0, "email": 1})

def insert_one(data):
    return collection_social_user.insert_one(data)
def update_one_social_user_with_email(email, current_datetime):
    collection_social_user.update_one({"email" : email}, {"$set": {"last_signin" : current_datetime,}})


    
def update_admin_role_if_not_exist(email, admin_role):
    collection_social_user.update_one(
        {
            "email": email,
            "roles": {
                "$not": {
                    "$elemMatch": {"name": "admin"}
                }
            }
        },
        {
            "$push": {"roles": admin_role}
        },
        upsert=False  # safer
    )

def get_one_with_email_o_stocklist(email):
    return collection_social_user.find_one({"email": email}, {"stock_list"})["stock_list"]

def find_one_roles_with_user_email(user_email):
    return collection_social_user.find_one({"email" : user_email} , {"roles": 1}) 


# ______________count and find________________________
def get_search_Result_with_pagenation(query, skip, limit):
    

    total_users = collection_social_user.count_documents(query)
    users_cursor = collection_social_user.find(query).skip(skip).limit(limit)

    return {"search_result" : users_cursor, "total_count" : total_users}


# _______________update________________________

def update_one_with_email_o_stocklist(email, stock_list):
    return collection_social_user.update_one({ "email": email }, {"$set": {"stock_list" : stock_list }})

 

def update_one_roles_with_id(id, role_data):
    return collection_social_user.update_one(
        {"_id": ObjectId(id)},
        {"$addToSet": {"roles": role_data}},
    )

def update_one_remove_rolesname_with_id(id, role_name):
    return collection_social_user.update_one(
        {"_id": ObjectId(id)},
        {"$pull": {"roles": {"name": role_name}}},
    )
def update_one_set_rolesname_with_id(id, updated_roles):
    return collection_social_user.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"roles": updated_roles}}
        )


def delete_all_with_email(email : str):
    return collection_social_user.delete_many({"email" : email})

def get_stock_list_with_emailid(email):
    return collection_social_user.find_one({"email": email}, {"_id": 0, "stock_list": 1})


# {
#     "_id" :"qsguhsnkj",
#     "email" : "test@gamail.com",
#     "stock_list" : [
#         {
#             "id"   : "2345678",
#             "name" : "",
#             "list" : [
#                 "sjnjsn" , "ajannsj", "ajnanjn"
#             ]
#         },
#         {
#             "id"   : "2345678",
#             "name" : "",
#             "list" : [
#                 "sjnjsn" , "ajannsj", "ajnanjn"
#             ]
#         },
#     ]

# }


import uuid

def create_stock_list(email, name, stock_symbols=None):
    if stock_symbols is None:
        stock_symbols = []

    new_list = {
        "id": str(uuid.uuid4())[:8],  # short unique id
        "name": name,
        "list": stock_symbols
    }

    result = collection_social_user.update_one(
        {"email": email},
        {
            "$push": {"stock_list": new_list}
        },
        upsert=True  # create user doc if not exists
    )

    return new_list

def delete_stock_list(email, list_id):
    result = collection_social_user.update_one(
        {"email": email},
        {
            "$pull": {"stock_list": {"id": list_id}}
        }
    )

    if result.modified_count == 0:
        return {"message": "List not found or already deleted"}

    return {"message": "Deleted successfully"}

def update_stock_list(email, list_id, name=None, stock_symbols=None):
    update_fields = {}

    if name is not None:
        update_fields["stock_list.$.name"] = name

    if stock_symbols is not None:
        update_fields["stock_list.$.list"] = stock_symbols

    if not update_fields:
        return {"message": "Nothing to update"}

    result = collection_social_user.update_one(
        {
            "email": email,
            "stock_list.id": list_id
        },
        {
            "$set": update_fields
        }
    )

    if result.matched_count == 0:
        return {"message": "Stock list not found"}

    return {"message": "Updated successfully"}


def add_symbol_to_list(email, list_id, symbol):
    return collection_social_user.update_one(
        {
            "email": email,
            "stock_list.id": list_id
        },
        {
            "$addToSet": {"stock_list.$.list": symbol}
        }
    )


def remove_symbol_from_list(email, list_id, symbol):
    return collection_social_user.update_one(
        {
            "email": email,
            "stock_list.id": list_id
        },
        {
            "$pull": {"stock_list.$.list": symbol}
        }
    )



def get_stock_list_id_name(email):
    data = collection_social_user.find_one(
        {"email": email},
        {"_id": 0, "stock_list.id": 1, "stock_list.name": 1}
    )

    if not data or "stock_list" not in data:
        return []

    return [
        {"id": item["id"], "name": item["name"]}
        for item in data["stock_list"]
    ]


def get_user_stock_list_by_id(email: str, list_id: str):
    data = collection_social_user.find_one(
        {
            "email": email,
            "stock_list.id": list_id
        },
        {
            "_id": 0,
            "stock_list.$": 1   # 🔥 only matching element
        }
    )

    if not data or "stock_list" not in data:
        return None

    return data["stock_list"][0]