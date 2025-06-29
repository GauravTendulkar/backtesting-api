from fastapi import FastAPI, Request, APIRouter, BackgroundTasks, File, UploadFile
from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Body, Security

from admin_dashboard import admin_function
from database import configurations
from typing import Optional, Dict, Any, List
import os
import shutil
from datetime import datetime, timedelta
import pytz
from functions import df_saving, newData_concat, fastCache_saving
from functions_v1 import memory
from bson import ObjectId
from pydantic import BaseModel
import asyncio
from functools import partial
from pydantic import BaseModel

likesdislikes = APIRouter()



def get_datetime_now():
    return datetime.strptime(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

class GetLikes(BaseModel):
    user_email : str
    contentId : str

@likesdislikes.post("/get-vote")
async def get_likes(data : GetLikes = Body(...)):
    print("likes get data", data)
    data = dict(data)
    user_email = data["user_email"]
    content_id = data["contentId"]
    vote = configurations.collection_votes.find_one({"email": user_email, "contentId": content_id }, {"_id": 0, "vote": 1 })
    print("vote", vote)
    if vote == None :
        return {"vote" : None}
    else:
        return {"vote" : vote["vote"]}
    
class SetVote(BaseModel):
    user_email : str
    contentId : str
    vote: Optional[str] = None

@likesdislikes.put("/update-vote")
async def get_user_vote(data: SetVote = Body(...)):
    data = dict(data)
    print("put vote", data)
    user_email = data["user_email"]
    content_id = data["contentId"]
    vote = data["vote"]

    if vote in ["like", "dislike"]:
        # Add or update the vote
        configurations.collection_votes.update_one(
            {"email": user_email, "contentId": content_id},
            {
                "$set": {
                    "vote": vote,
                    "voted_at": get_datetime_now()
                }
            },
            upsert=True
        )
    else:
        # If vote is None, remove the user's vote
        configurations.collection_votes.delete_one({
            "email": user_email,
            "contentId": content_id
        })

    # Count current votes
    like_count = configurations.collection_votes.count_documents({
        "contentId": content_id,
        "vote": "like"
    })

    dislike_count = configurations.collection_votes.count_documents({
        "contentId": content_id,
        "vote": "dislike"
    })

    # Update the content vote counts
    configurations.collection.update_one(
        {"_id": ObjectId(content_id)},
        {
            "$set": {
                "likes": like_count,
                "dislikes": dislike_count
            }
        },
        
    )

    return {
        "message": "Vote recorded" if vote else "Vote removed",
        "likes": like_count,
        "dislikes": dislike_count,
        "vote" : vote
    }


