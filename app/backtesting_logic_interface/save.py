

from ..backtesting_logic_interface import helper 
from ..database.mongodb.repositories import equation_collection
from fastapi import  HTTPException, status


# /{id}
def save_logic(id, equation, user_email):
    equation_dict = dict(equation)
    
    # print("save", user_email)
    
    if user_email :
        print("dict(equation) PUT") 
        
        equation_dict["updated_at"] = helper.get_datetime_now()
        
        res = equation_collection.update_one_with_id_email(id, user_email, equation_dict)
        
        raw = res.raw_result
        updated_existing = raw.get("updatedExisting")
        print("updated_existing", updated_existing)
        if updated_existing == True:
            return {"message": "Strategy Saved!"}
        else:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    else:
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )