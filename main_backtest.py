from fastapi import FastAPI

import time
from fastapi.middleware.cors import CORSMiddleware
from app.routes.router import app_backtesting


app = FastAPI()




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as necessary
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


@app.get("/backend/api/test")
def get_data():
    start = time.time()
    
    # df = df.to_dict(orient="records")
    print((time.time() - start)/60)
    # return  df # send as JSON
    return {"hello":"world"}


app.include_router(app_backtesting) 