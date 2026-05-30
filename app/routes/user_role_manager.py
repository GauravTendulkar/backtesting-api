# routes/social_user_role_change.py
from fastapi import APIRouter, HTTPException, Body, Query
from bson import ObjectId
from datetime import datetime
from pymongo import DESCENDING
from typing import Optional
from datetime import datetime
from ..database.mongodb.repositories import social_user_collection

admin_dashboard_social_role_change = APIRouter()


@admin_dashboard_social_role_change.get("/get-all-users")
async def get_all_users(
    page: int = Query(1),
    limit: int = Query(10),
    filter: str = Query("all"),
    role: str = Query(None)
):
    skip = (page - 1) * limit
    query = {}

    if filter == "with":
        query["roles.0"] = {"$exists": True}
    elif filter == "without":
        query["$or"] = [{"roles": {"$exists": False}}, {"roles": {"$size": 0}}]

    if role:
        query["roles.name"] = role

    # total_users = configurations.collection_social_user.count_documents(query)
    # users_cursor = configurations.collection_social_user.find(query).skip(skip).limit(limit)


    search_result = social_user_collection.get_search_Result_with_pagenation(query, skip, limit)
    users_cursor = search_result["search_result"]
    total_users = search_result["total_count"]

    users = []
    for user in users_cursor:
        user["_id"] = str(user["_id"]) 
        if "roles" in user:
            for role in user["roles"]:
                role["start_date"] = role["start_date"].isoformat()
                role["end_date"] = role["end_date"].isoformat()
        users.append(user)

    return {
        "users": users,
        "total": total_users
    }



@admin_dashboard_social_role_change.post("/add-role-to-user")
async def add_role_to_user(
    user_id: str = Body(...),
    name: str = Body(...),
    start_date: str = Body(...),
    end_date: str = Body(...),
    limit: str = Body(...),
):
    role_data = {
        "name": name,
        "start_date": datetime.fromisoformat(start_date),
        "end_date": datetime.fromisoformat(end_date),
        "limit": limit,
    }
    # result = configurations.collection_social_user.update_one(
    #     {"_id": ObjectId(user_id)},
    #     {"$addToSet": {"roles": role_data}},
    # )
    result = social_user_collection.update_one_roles_with_id(user_id, role_data)
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Role added"}


@admin_dashboard_social_role_change.post("/remove-role-from-user")
async def remove_role_from_user(user_id: str = Body(...), role_name: str = Body(...)):
    # result = configurations.collection_social_user.update_one(
    #     {"_id": ObjectId(user_id)},
    #     {"$pull": {"roles": {"name": role_name}}},
    # )
 
    result = social_user_collection.update_one_remove_rolesname_with_id(user_id, role_name)

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Role removed"}


@admin_dashboard_social_role_change.post("/update-role-dates")
async def update_role_dates(
    user_id: str = Body(...),
    name: str = Body(...),
    start_date: str = Body(...),
    end_date: str = Body(...),
    limit: str = Body(...)
):
    try:
        # user = configurations.collection_social_user.find_one({"_id": ObjectId(user_id)})
        user = social_user_collection.get_one_with_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        updated_roles = []
        found = False
        for role in user.get("roles", []):
            if role["name"] == name:
                updated_roles.append({
                    "name": name,
                    "start_date": datetime.fromisoformat(start_date),
                    "end_date": datetime.fromisoformat(end_date),
                    "limit": limit
                })
                found = True
            else:
                updated_roles.append(role)

        if not found:
            raise HTTPException(status_code=404, detail="Role not found")

        # configurations.collection_social_user.update_one(
        #     {"_id": ObjectId(user_id)},
        #     {"$set": {"roles": updated_roles}}
        # )

        social_user_collection.update_one_set_rolesname_with_id(user_id, updated_roles)
        return {"message": "Role updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

