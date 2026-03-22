from fastapi import FastAPI, Header, HTTPException, Depends
from typing import Optional
import jwt
import os

app = FastAPI()

JWT_SECRET = os.getenv("BACKEND_JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")

# Optional model
from pydantic import BaseModel
class RequestBody(BaseModel):
    someData: Optional[str] = None

# Dependency to decode JWT
def get_current_user(authorization: str = Header(...)):

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    # print("authorization", authorization)
    token = authorization.split(" ")[1]
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        print(decoded)
        return decoded["email"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        return None
        raise HTTPException(status_code=400, detail="Invalid token")

# @app.post("/protected-endpoint")
# def protected_route(body: RequestBody, user=Depends(get_current_user)):
#     return {
#         "message": "Token validated successfully",
#         "user": user,
#         "received_data": body.dict()
#     }
