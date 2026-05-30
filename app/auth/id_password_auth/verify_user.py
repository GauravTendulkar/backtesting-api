

from ..id_password_auth import helper
from fastapi import HTTPException, status
# from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Body, Security, BackgroundTasks




def verify_user_fn(token):
    try:
        user = dict(helper.get_current_user(token))
        if user:
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
    except Exception as e:
        # print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )