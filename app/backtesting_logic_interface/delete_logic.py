
from ..database.mongodb.repositories import equation_collection
from fastapi.responses import JSONResponse

# /delete/{id}
def delete_equation_fn(user_email, id):
    if user_email :
        
        result = equation_collection.delete_one_with_id_email(id, user_email)

        if result.deleted_count == 1:
            
            return JSONResponse(content={"message": "Equation deleted successfully."}, status_code=200)
        else:
            
            return JSONResponse(content={"message": "Equation not found."}, status_code=404)
        

