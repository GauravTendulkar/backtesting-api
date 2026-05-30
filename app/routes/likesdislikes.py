from fastapi import FastAPI, Request, APIRouter, BackgroundTasks, File, UploadFile, Body
from typing import Optional
from datetime import datetime
import pytz
from pydantic import BaseModel
from pydantic import BaseModel
from ..database.mongodb.repositories import votes_collection, equation_collection


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
    
    vote = votes_collection.get_one_with_email_id(user_email, content_id)
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
        
        votes_collection.update_one_with_email_id(user_email, content_id, vote, get_datetime_now())
    else:
       
        votes_collection.delete_one_with_email_contentid(user_email, content_id)
    votes_count = votes_collection.get_votes_count(content_id)
    like_count = votes_count["like"]
    dislike_count = votes_count["dislike"]
    equation_collection.update_votes_count_with_contentid(content_id, like_count, dislike_count)

    return {
        "message": "Vote recorded" if vote else "Vote removed",
        "likes": like_count,
        "dislikes": dislike_count,
        "vote" : vote
    }


