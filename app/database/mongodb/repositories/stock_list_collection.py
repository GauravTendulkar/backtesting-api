from app.database.mongodb.database import db
from bson import ObjectId
import time
import random
import pytz
from datetime import datetime

collection_stock_list = db["stock_list"]

def get_datetime_now():
    return datetime.strptime(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")


def generate_stock_id():
    timestamp_part = int(time.time() * 1000) % 10_000  # last 4 digits
    random_part = random.randint(1000, 9999)           # 4 digits
    return f"t{timestamp_part:04d}{random_part}"



def insert_one(symbol :str, company_name :str):
    now = get_datetime_now()

    stock_doc = {
        
        "stock_id": generate_stock_id(),             # optional if you still want separate field
        "current": {
            "symbol": symbol.upper(),
            "company_name": company_name,
            "valid_from": now
        },
        "history": [],
        "is_active": True,
        "updated_at": now
    }

    # If you want stock_id separate from _id
    # stock_doc["stock_id"] = stock_doc["_id"]

    result = collection_stock_list.insert_one(stock_doc)

    return result.inserted_id




def update_one_stock(stock_id: str, symbol: str, company_name: str):
    now = get_datetime_now()

    # Normalize input
    symbol = symbol.upper()

    # Step 1: Fetch existing document
    stock = collection_stock_list.find_one({"stock_id": stock_id})

    if not stock:
        raise ValueError(f"Stock with stock_id={stock_id} not found")

    current = stock.get("current", {})

    # Step 2: Check if update is needed
    if (
        current.get("symbol") == symbol and
        current.get("company_name") == company_name
    ):
        return {"message": "No changes detected"}

    # Step 3: Prepare history entry (move current → history)
    history_entry = {
        "symbol": current.get("symbol"),
        "company_name": current.get("company_name"),
        "valid_from": current.get("valid_from"),
        "valid_to": now
    }

    # Step 4: Perform atomic update
    result = collection_stock_list.update_one(
        {"stock_id": stock_id},
        {
            "$push": {"history": history_entry},
            "$set": {
                "current.symbol": symbol,
                "current.company_name": company_name,
                "current.valid_from": now,
                "updated_at": now
            }
        }
    )

    return {
        "message": "Stock updated successfully",
        "modified_count": result.modified_count
    }



def get_stock_history(stock_id: str):
    stock = collection_stock_list.find_one(
        {"stock_id": stock_id},
        {"_id": 0}  # exclude mongo _id
    )

    if not stock:
        raise ValueError(f"Stock with stock_id={stock_id} not found")

    history = stock.get("history", [])
    current = stock.get("current", {})

    # Combine history + current into timeline
    timeline = []

    # Add past history
    for h in history:
        timeline.append({
            "symbol": h.get("symbol"),
            "company_name": h.get("company_name"),
            "valid_from": h.get("valid_from"),
            "valid_to": h.get("valid_to"),
            "is_current": False
        })

    # Add current record
    if current:
        timeline.append({
            "symbol": current.get("symbol"),
            "company_name": current.get("company_name"),
            "valid_from": current.get("valid_from"),
            "valid_to": None,
            "is_current": True
        })

    # Sort by valid_from (oldest → latest)
    timeline.sort(key=lambda x: x["valid_from"] or "")

    return {
        "stock_id": stock_id,
        "is_active": stock.get("is_active", True),
        "timeline": timeline
    }





def get_all_stocks(limit=None) -> list:
    query = {}
    projection = {
        "_id": 1,
        "stock_id": 1,
        "current.symbol": 1,
        "current.company_name": 1,
        "is_active": 1,
        "updated_at": 1
    }

    cursor = collection_stock_list.find(query, projection).sort("current.symbol", 1)

    if limit:
        cursor = cursor.limit(limit)

    stocks = []

    for doc in cursor:
        stocks.append({
            "id" : str(doc.get("_id")),
            "stock_id": doc.get("stock_id"),
            "symbol": doc.get("current", {}).get("symbol"),
            "company_name": doc.get("current", {}).get("company_name"),
            "is_active": doc.get("is_active", True),
            "updated_at": doc.get("updated_at")
        })

    return stocks

def update_stock_id(id, new_stock_id):
    result = collection_stock_list.update_one(
        {"_id": ObjectId(id)},   # filter
        {
            "$set": {
                "stock_id": new_stock_id
            }
        }
    )
    
    return result.modified_count



def get_all_stocks_key_value():
    query = {"is_active": True}
    projection = {
        "_id": 0,
        "stock_id": 1,
        "current.symbol": 1,
        "current.company_name": 1
    }

    cursor = collection_stock_list.find(query, projection)

    result = {}

    for doc in cursor:
        stock_id = doc.get("stock_id")
        current = doc.get("current", {})

        if stock_id and current:
            result[stock_id] = {
                "symbol": current.get("symbol"),
                "company_name": current.get("company_name")
            }

    return result

def change_stock_status(stock_id, is_active=True):
    now = get_datetime_now()

    result = collection_stock_list.update_one(
        {"stock_id": stock_id},
        {
            "$set": {
                "is_active": is_active,
                "updated_at": now
            }
        }
    )

    if result.matched_count == 0:
        raise ValueError(f"Stock with stock_id={stock_id} not found")

    return {
        "message": "Stock status updated successfully",
        "stock_id": stock_id,
        "is_active": is_active,
        "modified_count": result.modified_count
    }



def delete_one_stock(stock_id: str):
    result = collection_stock_list.delete_one({"stock_id": stock_id})

    if result.deleted_count == 0:
        raise ValueError(f"Stock with stock_id={stock_id} not found")

    return {
        "message": "Stock deleted permanently",
        "stock_id": stock_id
    }






