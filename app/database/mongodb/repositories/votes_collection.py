from ..database import db
from bson import ObjectId


collection_votes = db["votes"]

def get_one_with_email_id(email, id):

    return collection_votes.find_one({"email": email, "contentId": id }, {"_id": 0, "vote": 1 })

def update_one_with_email_id(email, content_id, vote, current_datetime):
    return collection_votes.update_one(
            {"email": email, "contentId": content_id},
            {
                "$set": {
                    "vote": vote,
                    "voted_at": current_datetime
                }
            },
            upsert=True
        )

def delete_one_with_email_contentid(email, content_id):
    return collection_votes.delete_one({
            "email": email,
            "contentId": content_id
        })

def get_votes_count(content_id):
    like = collection_votes.count_documents({
        "contentId": content_id,
        "vote": "like"
    })

    dislike = collection_votes.count_documents({
        "contentId": content_id,
        "vote": "dislike"
    })

    return {"like" : like, "dislike" : dislike}


def delete_all_with_email(email):
    return collection_votes.delete_many({"email" : email})