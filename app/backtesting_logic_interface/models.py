
from pydantic import BaseModel, Field
from datetime import datetime
import pytz



class PaginationOutput(BaseModel):
    page : int
    items : list
    total_no_of_pages: int

class Equation(BaseModel):
    stockListName: str
    title: str
    description: str
    scanCategory: str
    tags: str = "other"
    equation: str
    # updated_at: int = int(datetime.timestamp(datetime.now())) 
    # created: int = int(datetime.timestamp(datetime.now())) 
    link : str = ""
    updated_at: datetime = datetime.strptime(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    created: datetime = datetime.strptime(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    # email: str
    isPrivate : bool = False
    tradeMode : str = "entry_exit_backtest"
    # user_email : Optional[str] = None


class LinkGetOutput(BaseModel):
    id : str = Field(..., alias="_id")
    stockListName: str
    title : str
    description : str
    scanCategory : str
    tags : str
    equation : str
    link: str
    updated_at : datetime
    created : datetime
    isPrivate : bool
    likes : int
    dislikes : int
    tradeMode : str = "entry_exit_backtest"
    model_config = {
        "populate_by_name": True  # Allows aliasing to work
    }