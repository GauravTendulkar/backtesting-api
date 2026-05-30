from ..database import db


collection_user = db["users"]

def get_user_with_email(email):

    return collection_user.find_one({"email": email})

def get_user_with_username(username):
    return collection_user.find_one({"username": username})


def get_user_with_email_o_email_otp(email):
    return collection_user.find_one({"email": email}, { "_id": 0, "email": 1, "otp": 1 })
    # collection_user.find_one({"email": data["email"]}, { "_id": 0, "email": 1, "otp": 1 })

def update_user_with_email_o_email_otp(email, otp, current_datetime):
    return collection_user.update_one( {"email" : email}, {"$set": { "otp": [otp, current_datetime] }} )


def update_with_datetime_password_email(email, datetime, password):
    return collection_user.update_one(
                {"email": email },  
                {"$set": {"otp": ["", datetime], "hashed_password": password } }  )


def insert_one(data):
    return collection_user.insert_one(data)

def delete_all_with_email(email : str):
    return collection_user.delete_many({"email" : email})