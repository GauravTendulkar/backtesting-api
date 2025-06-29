from fastapi import APIRouter, HTTPException, Body, Query
from database import configurations
from bson import ObjectId, Regex
from database import configurations
from datetime import datetime, timedelta


admin_dashboard_social_role_change = APIRouter()

# @admin_dashboard_social_role_change.get("/get-all-users")
# async def get_all_users():
#     users = list(configurations.collection_social_user.find())
#     for u in users:
#         u["_id"] = str(u["_id"])
#     return users


@admin_dashboard_social_role_change.get("/get-all-users")
async def get_all_users(
    search: str = Query(default="", alias="search"),
    role: str = Query(default=""),
    date_filter: str = Query(default="all"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=5, ge=1, le=100),
):
    query = {}

    if search:
        regex = {"$regex": search, "$options": "i"}
        query["$or"] = [{"full_name": regex}, {"email": regex}]

    if role == "none":
        query["$or"] = [{"roles": {"$exists": False}}, {"roles": {"$size": 0}}]
    elif role:
        query["roles"] = role


    if date_filter in ["recent", "older"]:
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        if date_filter == "recent":
            query["account_created"] = {"$gte": cutoff_date}
        else:
            query["account_created"] = {"$lt": cutoff_date}

    total_count = configurations.collection_social_user.count_documents(query)
    total_pages = (total_count + limit - 1) // limit

    users = list(
        configurations.collection_social_user.find(query)
        .sort("account_created", -1)
        .skip((page - 1) * limit)
        .limit(limit)
    )

    for u in users:
        u["_id"] = str(u["_id"])

    return {
        "users": users,
        "total_pages": total_pages,
    }

@admin_dashboard_social_role_change.post("/add-role-to-user")
async def add_role_to_user(user_id: str = Body(...), role: str = Body(...)):
    result = configurations.collection_social_user.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"roles": role}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Role added"}

@admin_dashboard_social_role_change.post("/remove-role-from-user")
async def remove_role_from_user(user_id: str = Body(...), role: str = Body(...)):
    result = configurations.collection_social_user.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"roles": role}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Role removed"}
