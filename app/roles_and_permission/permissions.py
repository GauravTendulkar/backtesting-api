from ..database.mongodb.repositories import roles_collection, social_user_collection, groups_collection, permissions_collection

from ..roles_and_permission import admin_roles_permission_list

# /permissions/save
def save_permission(data):
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
    
    permissions_collection.delete_all()
    if unique:
        
        permissions_collection.insert_all(list(unique.values()))
        
    return {"status": "success"}



def insert_all_admin_permission():
    admin_permission_list = admin_roles_permission_list.ADMIN_PERMISSION_LIST
    
    for perm in admin_permission_list:
        permissions_collection.update_if_not_exist(
            {"permissions_name": perm},   # filter
            {
                "$setOnInsert": {
                    "permissions_name": perm,
                    "isActive": True
                }
            },
            upsert=True
        )

