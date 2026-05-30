

from ..database.mongodb.repositories import equation_collection
import math
from fastapi import  HTTPException

def dashboard_pagination_logic(user_email, page, noOfItems):
    print("dashboard_pagination_logic", user_email)
    if user_email :  

        count = equation_collection.get_count_with_email(user_email)
        
        print(count)
        print(page)  # Current page
        items_per_page = noOfItems  # Documents per page
        skip_count = (page - 1) * items_per_page  # Calculate number of documents to skip
        total_no_of_pages = int(math.ceil(count / noOfItems))
        equations_list = []

        if count == 0 and page == 1:
            return {"page": page, "items": equations_list, "total_no_of_pages" : total_no_of_pages}

        if 1<= page and page <= total_no_of_pages:
            # equations = configurations.collection.find( {"email" : user_email}, {"title": 1, "description": 1, "created": 1, "updated_at": 1, "likes": 1, "dislikes": 1, "link": 1,} ).sort("created", -1).skip(skip_count).limit(items_per_page)
            equations = equation_collection.get_page_with_email(user_email, skip_count, items_per_page)
            
            # print("equations")
            equations_list = list(equations)
            for i in range(0, len(equations_list)):
                equations_list[i]["_id"] = str(equations_list[i]["_id"])
        
            
            return {"page": page, "items": equations_list, "total_no_of_pages" : total_no_of_pages}
        else:
            # return {"page": total_no_of_pages, "items": equations_list, "total_no_of_pages" : total_no_of_pages}
            raise HTTPException(status_code=404, detail="Page Not Found")
    else:
            
            raise HTTPException(status_code=404, detail="Page Not Found")