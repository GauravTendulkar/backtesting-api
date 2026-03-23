from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import requests
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import os

protected = APIRouter()
security = HTTPBearer()
# Must match NEXTAUTH_SECRET in your Next.js app
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")  # 32 bytes
IV = os.getenv("IV")  # 16 bytes

class EncryptedData(BaseModel):
    encrypted_email: str

def decrypt_email(encrypted_email: str) -> str:
    try:
        # Convert from hex to bytes
        encrypted_bytes = bytes.fromhex(encrypted_email)
        
        cipher = AES.new(
            bytes.fromhex(ENCRYPTION_KEY),
            AES.MODE_CBC,
            bytes.fromhex(IV)
        )
        
        decrypted_bytes = unpad(
            cipher.decrypt(encrypted_bytes),
            AES.block_size
        )
        
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Decryption failed: {str(e)}"
        )

@protected.post("/get")
async def decrypt_email_endpoint(data: EncryptedData):
    decrypted_email = decrypt_email(data.encrypted_email)
    return {"decrypted_email": decrypted_email}


# @protected.get("/get")
# def protected_route(payload: dict = Depends(verify_google_access_token)):
#     print("payload", payload)
#     return {"message": "Access granted", "user": payload}
