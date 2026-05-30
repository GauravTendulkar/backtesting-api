

from .config import STOCK_LIST_LIMIT, STOCK_EXECUTION_LIST_LIMIT, STOCK_LIST
from fastapi import  HTTPException, status
from ..database.mongodb.repositories import social_user_collection



def save_stocklist(stockList):
    stockList = dict(stockList)
    user_email = stockList["user_email"]
    
    stockList = stockList["stock_list"]
    stockList = [item.model_dump() for item in stockList]

    # print("put Email", user_email)
    # print(stockList)
    

    
    # Optionally, retrieve current user based on the token.
    # user = dict(get_current_user(token))
    if user_email:
        # print("stockList length", len(stockList))
        if len(stockList) > STOCK_LIST_LIMIT:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Please do not create stock lists more then the limit {STOCK_LIST_LIMIT}",
                headers={"WWW-Authenticate": "Bearer"}
            )
        for i in range(0, len(stockList)):
            if len(stockList[i]["list"]) >  STOCK_EXECUTION_LIST_LIMIT:
                raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Please do not  create individual stock lists more then the limit {STOCK_EXECUTION_LIST_LIMIT}",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        
        social_user_collection.update_one_with_email_o_stocklist(user_email, stockList)

        return {"message": "Stock list saved"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login or create an account to save stock list",
            headers={"WWW-Authenticate": "Bearer"}
        )
        