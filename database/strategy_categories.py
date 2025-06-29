from fastapi import APIRouter, Query
from database import configurations
from datetime import datetime, timedelta
from bson import ObjectId
from pymongo import DESCENDING

strategy_categories = APIRouter()

@strategy_categories.get("/trending-last-24-hours")
async def get_trending_strategies(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    now = datetime.utcnow()
    last_24_hours = now - timedelta(hours=24)

    # Step 1: Get trending links in last 24 hours
    pipeline = [
        {
            "$match": {
                "strategy_run_at": {"$gte": last_24_hours}
            }
        },
        {
            "$group": {
                "_id": "$link",
                "count": {"$sum": 1},
                "link": {"$first": "$link"}
            }
        },
        {"$sort": {"count": -1}}
    ]

    trending_links = list(configurations.collection_strategy_run.aggregate(pipeline))
    links = [doc["link"] for doc in trending_links]

    # Step 2: Query collection for only public strategies
    content_docs = list(configurations.collection.find(
        {
            "link": {"$in": links},
            "isPrivate": False
        },
        {
            "link": 1,
            "title": 1,
            "description": 1,
            "tags": 1,
            "likes": 1,
            "dislikes": 1
        }
    ))

    content_map = {doc["link"]: doc for doc in content_docs}

    # Step 3: Merge and filter only those in content_map
    public_trending = []
    for doc in trending_links:
        content = content_map.get(doc["link"])
        if content:
            public_trending.append({
                "link": doc["link"],
                "title": content.get("title", ""),
                "description": content.get("description", ""),
                "tags": content.get("tags", []),
                "likes": content.get("likes", 0),
                "dislikes": content.get("dislikes", 0),
                "count": doc["count"]
            })

    # Step 4: Apply pagination
    start = (page - 1) * limit
    end = start + limit
    paginated = public_trending[start:end]

    return {
        "data": paginated,
        "total": len(public_trending),
        "page": page,
        "limit": limit,
        "pages": (len(public_trending) + limit - 1) // limit
    }







@strategy_categories.get("/top-liked-strategies")
async def get_top_liked_strategies(tag: str = Query(...)):
    query = {
        "isPrivate": False,
        "tags": tag
    }

    projection = {
        "_id": 1,
        "link": 1,
        "title": 1,
        "description": 1,
        "likes": 1,
        "tags": 1
    }

    documents = list(configurations.collection.find(query, projection).sort("likes", -1).limit(20))

    # Convert ObjectId to string
    for doc in documents:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])

    return documents







@strategy_categories.get("/search")
def search_strategies(
    query: str = Query(..., min_length=1), 
    page: int = 1,
    page_size: int = 20
):
    skip = (page - 1) * page_size

    # Case-insensitive partial match on title or link
    regex = {"$regex": query, "$options": "i"}
    filters = {
        "is_private": {"$ne": True},
        "$or": [
            {"title": regex},
            {"link": regex}
        ]
    }

    cursor = configurations.collection.find(filters).sort("likes", -1).skip(skip).limit(page_size)
    total = configurations.collection.count_documents(filters)

    results = []
    for doc in cursor:
        results.append({
            "title": doc.get("title", ""),
            "link": doc.get("link", ""),
            "likes": doc.get("likes", 0)
        })

    return {
        "total": total,
        "results": results,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }