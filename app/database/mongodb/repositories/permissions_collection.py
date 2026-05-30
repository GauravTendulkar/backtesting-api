from ..database import db
from pydantic import BaseModel

# models 

class Permissions(BaseModel) :
    permissions_name : str
    isActive : bool
 

# _________________________________________________


collection_permissions = db["permissions"]



# ______find_____________________
def get_all_permissions():
    return list(collection_permissions.find({}, {"_id": 0}))

# ______delete_____________________
def delete_all():
    collection_permissions.delete_many({})


# ______insert_____________________
def insert_all(items):
    collection_permissions.insert_many(items)


    
# ______update_____________________


def update_if_not_exist(filter_query, update_query, upsert=False):
    return collection_permissions.update_one(
        filter_query,
        update_query,
        upsert=upsert
    )

# Creating index
try:
    collection_permissions.create_index(
        "permissions_name",
        unique=True
    )
except :
    pass