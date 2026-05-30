
from ..database.mongodb.repositories import equation_collection
from pydantic import BaseModel, Field
from datetime import datetime
from fastapi import  HTTPException
from .models import LinkGetOutput



# /{link}
def get_backtesting_logic_with_url(link, user_email):
    equations = equation_collection.get_one_with_link(link)

    
    if equations:
        if equations["isPrivate"] == False:
            equations["_id"] = str(equations["_id"])
            
            
            return LinkGetOutput(**equations) # Create an instance of LinkGetOutput
        elif equations["isPrivate"] == True:
            # user = get_current_user(token)
            # print("user", user)
            if user_email:
                if user_email == equations["email"]:
                    equations["_id"] = str(equations["_id"])
                    
                    return LinkGetOutput(**equations) # Create an instance of LinkGetOutput
        else:           
            raise HTTPException(status_code=404, detail="Equation not found")
    else:        
        raise HTTPException(status_code=404, detail="Equation not found")