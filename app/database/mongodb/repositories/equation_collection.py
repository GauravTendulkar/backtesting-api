from ..database import db
from bson import ObjectId

collection = db["equation"]


def get_count_with_email(email):
    return collection.count_documents({"email" : email})


def get_page_with_email(email, skip_count, items_per_page):
    return collection.find( {"email" : email}, {"title": 1, "description": 1, "created": 1, "updated_at": 1, "likes": 1, "dislikes": 1, "link": 1,} ).sort("created", -1).skip(skip_count).limit(items_per_page)

def get_one_with_link(link):
    return collection.find_one({"link": link})

def delete_one_with_id_email(id, email):
    return collection.delete_one({"_id": ObjectId(id), "email": email})

def find_one_and_update_with_link(link, insert_item):
    return collection.find_one_and_update(
                {"link": link},                # Query to check if link exists   "new-data-copy-1"}, #
                {"$setOnInsert": insert_item},                # Insert these fields if not found
                upsert=True,                                    # Create document if it doesn't exist
                # return_document=ReturnDocument.AFTER            # Return the document after the operation
                )


def update_one_with_id_email(id, email, data):
    return collection.update_one({"_id": ObjectId(id), "email": email }, {"$set": data})


def update_votes_count_with_contentid(content_id, like_count, dislike_count):
    collection.update_one(
        {"_id": ObjectId(content_id)},
        {
            "$set": {
                "likes": like_count,
                "dislikes": dislike_count
            }
        },
        
    )


def get_link_info_with_link_isprivate(links):
    return list(collection.find(
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

def get_top_20_liked_content(query, projection):
    return list(collection.find(query, projection).sort("likes", -1).limit(20))


def get_search_Result_with_pagenation(filters, skip, page_size):
    cursor = collection.find(filters).sort("likes", -1).skip(skip).limit(page_size)
    total = collection.count_documents(filters)

    return {"search_result" : cursor, "total_count" : total}

def delete_all_with_email(email):
    return collection.delete_many({"email" : email})


def get_all_links():
    return collection.find({}, {"_id" : 0, "link" : 1})
