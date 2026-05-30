from fastapi import  Header, HTTPException
from ...config import env
import jwt
import os
# from dotenv import load_dotenv 





def get_current_user(authorization: str = Header(...)):
   
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.split(" ")[1]
    try:
        decoded = jwt.decode(token, env.JWT_SECRET, algorithms=[env.ALGORITHM])
        
        return decoded["email"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        return None
        raise HTTPException(status_code=400, detail="Invalid token")
    
# def get_current_user(authorization: str = Header(...)):

#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=401, detail="Invalid authorization format")
#    
#     token = authorization.split(" ")[1]
#     try:
#         decoded = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
#         
#         return decoded["email"]
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Token expired")
#     except jwt.InvalidTokenError:
#         return None
#         raise HTTPException(status_code=400, detail="Invalid token")
