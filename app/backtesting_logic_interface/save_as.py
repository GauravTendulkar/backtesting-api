
from fastapi import  HTTPException, status
from ..backtesting_logic_interface import helper 
from ..database.mongodb.repositories import equation_collection


def save_as_logic(equation, user_email):
    equation_dict = dict(equation)
    
    print("save-as", user_email)
    
    if user_email :
        
        if len(equation_dict["title"]) == 0 :
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The 'title' field is required.",
            headers={"WWW-Authenticate": "Bearer"}
        )
        if len(equation_dict["scanCategory"]) == 0 :
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The 'Scan Category' field is required.",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
 

        equation_dict["link"] = helper.generate_unique_slug(equation_dict["title"])

        equation_dict["updated_at"] = helper.get_datetime_now()
        equation_dict["created"] = helper.get_datetime_now()
        equation_dict["email"] = user_email
        equation_dict["likes"] = 0
        equation_dict["dislikes"] = 0
        
        new_doc = "empty value"
        
        while new_doc:
           
            new_doc = equation_collection.find_one_and_update_with_link(equation_dict["link"], equation_dict)
       
            if new_doc is None:
                return equation_dict["link"]
            else:
                equation_dict["link"] = helper.generate_unique_slug(equation_dict["title"])
      
    else:
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )