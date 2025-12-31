from fastapi import APIRouter, HTTPException
from bson import ObjectId
from database import configurations
from pydantic import BaseModel


date_range = APIRouter()

@date_range.get("/get-default-date-range")
async def get_default_daterange():
    default = [
    {"tf" : 1, "range": {"years": 1, "months" : 0, "days" : 0}},
    {"tf" : 2, "range": {"years": 1, "months" : 0, "days" : 0}},
    {"tf" : 3, "range": {"years": 1, "months" : 0, "days" : 0}},
    {"tf" : 5, "range": {"years": 1, "months" : 0, "days" : 0}},
    {"tf" : 10, "range": {"years": 1, "months" : 0, "days" : 0}},
    {"tf" : 15, "range": {"years": 1, "months" : 0, "days" : 0}},
    {"tf" : 30, "range": {"years": 1, "months" : 0, "days" : 0}},
    {"tf" : 60, "range": {"years": 1, "months" : 0, "days" : 0}},
    {"tf" : 120, "range": {"years": 1, "months" : 0, "days" : 0}},
    {"tf" : 180, "range": {"years": 1, "months" : 0, "days" : 0}},
    {"tf" : 240, "range": {"years": 1, "months" : 0, "days" : 0}},
    {"tf" : "Daily", "range": {"years": 1, "months" : 0, "days" : 0}},
    {"tf" : "Weekly", "range": {"years": 1, "months" : 0, "days" : 0}},
    {"tf" : "Monthly", "range": {"years": 1, "months" : 0, "days" : 0}},
]
    return default


@date_range.get("/get-all-date-range")
async def get_all_daterange():
    data = list(configurations.collection_date_range.find({}))
    for d in data:
        d["_id"] = str(d["_id"])
    return data


@date_range.post("/set-one-date-range")
async def set_one_daterange(payload: dict):
    _id = payload.get("id")
    if not _id:
        raise HTTPException(status_code=400, detail="Missing ID")
    update = {
        "role_name": payload["role_name"],
        "date_range": payload["date_range"]
    }
    result = configurations.collection_date_range.update_one({"_id": ObjectId(_id)}, {"$set": update})
    return {"updated": result.modified_count > 0}


@date_range.post("/create-role-with-date-range")
async def create_role_with_date_range(payload: dict):
    role_name = payload.get("role_name")
    date_range = payload.get("date_range")

    if not role_name or not date_range:
        raise HTTPException(status_code=400, detail="Missing role_name or date_range")

    # Ensure role_name uniqueness (optional)
    existing = configurations.collection_date_range.find_one({"role_name": role_name})
    if existing:
        raise HTTPException(status_code=400, detail="Role name already exists")

    result = configurations.collection_date_range.insert_one({
        "role_name": role_name,
        "date_range": date_range
    })

    return {"inserted_id": str(result.inserted_id)}



class DeleteDateRangeRequest(BaseModel):
    id: str  # MongoDB ObjectId as a string

@date_range.post("/delete-one-date-range")
async def delete_one_date_range(req: DeleteDateRangeRequest):
    try:
        print("_id", req.id)

        # Validate ObjectId
        if not ObjectId.is_valid(req.id):
            raise HTTPException(status_code=400, detail="Invalid ObjectId")

        result = configurations.collection_date_range.delete_one({"_id": ObjectId(req.id)})
        print("result", result)
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Date range not found")
        return {"message": "Deleted successfully"}

    except Exception as e:
        print("Exception:", str(e))  # Log the actual exception for debugging
        raise HTTPException(status_code=500, detail=f"Error deleting date range: {str(e)}")