import random
import string
from ...database.mongodb.repositories import users_collection
from ..id_password_auth import helper
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException,  BackgroundTasks
from email.mime.text import MIMEText
import smtplib
from datetime import datetime, timedelta

def generate_otp(length=6):
    """
    Generates a random OTP of a specified length using digits.
    
    Args:
        length (int): Length of the OTP. Defaults to 6.
        
    Returns:
        str: A string representing the generated OTP.
    """
    otp = ''.join(random.choices(string.digits, k=length))
    return otp

def send_otp_email(
    emailid: str,
    otp: str,
    sender_email: str ,
    sender_password: str 
    
):
    
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    
    subject: str = "Your One-Time Password (OTP)"
    """
    Sends an OTP email to the specified email address.

    Args:
        emailid (str): Recipient's email address.
        otp (str): The one-time password to send.
        smtp_server (str): SMTP server address. Default is Gmail's SMTP server.
        smtp_port (int): SMTP server port. Default is 587.
        sender_email (str): The sender's email address.
        sender_password (str): The sender's email password.
        subject (str): Subject line of the email.

    Returns:
        bool: True if email was sent successfully, False otherwise.
    """
    # Construct the email body
    body = f"""
    Hi,

    Your OTP is: {otp}

    If you did not request this, please ignore this email.

    Regards,
    Your Company Name
    """
    
    # Create a multipart email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = emailid
    message["Subject"] = subject

    # Attach the email body as plain text
    message.attach(MIMEText(body, "plain"))

    try:
        # Connect to the SMTP server and send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, emailid, message.as_string())
        server.quit()
        print("OTP email sent successfully!")
        return True
    except Exception as e:
        print("Error sending email:", e)
        return False

# /sendOTP
def send_otp(email, background_tasks ):
    otp = generate_otp(length=6)
    
    user_data =  users_collection.get_user_with_email_o_email_otp(email)
    # print(user_data)
    if user_data:
        # print("OTP", otp)
        
        users_collection.update_user_with_email_o_email_otp(email, otp, helper.get_datetime_now())
        # BackgroundTasks.add_task(forgotPassword.send_otp_email, email, otp, sender_email="1248clashofclans8421@gmail.com", sender_password="zuajcznsfdrswnhv")
        background_tasks.add_task(send_otp_email, email, otp, "1248clashofclans8421@gmail.com", "zuajcznsfdrswnhv")
        return {"message" : f"OTP has been send to {email}"}
    else:
        raise HTTPException(status_code=400, detail="User does not exist")
    

# /verifyOTP
def verify_otp(data):
    data = dict(data)
    # print("data", data)

    # user_data = collection_user.find_one({"email": data["email"]}, { "_id": 0, "email": 1, "otp": 1 })
    user_data = users_collection.get_user_with_email_o_email_otp(data["email"])
    if user_data:
        # print(user_data, data)
        if user_data["email"] == data["email"] and user_data["otp"][0] == data["otp"]:
            if (helper.get_datetime_now() - user_data["otp"][1]) < timedelta(minutes=30):
                
                return {"message" : f"OTP has been verified"}
            else:
                raise HTTPException(status_code=400, detail="otp is expired")
        else:
            raise HTTPException(status_code=400, detail="wrong otp entered")
        

# /changePassword
def change_password_with_otp(data):
    data = dict(data)
    # print("data", data)
    # user_data = collection_user.find_one({"email": data["email"]}, { "_id": 0, "email": 1, "otp": 1 })
    user_data = users_collection.get_user_with_email_o_email_otp(data["email"])
    if user_data:
        # print(user_data, data)
        if user_data["email"] == data["email"] and  user_data["otp"][0] == data["otp"]:
            if (helper.get_datetime_now() - user_data["otp"][1]) < timedelta(minutes=30):
                hashed_password = helper.get_password_hash(data['password'])
                # collection_user.update_one(
                # {"email": data["email"] },  
                # {"$set": {"otp": ["", get_datetime_now()], "hashed_password": hashed_password } }  )
                users_collection.update_with_datetime_password_email(data["email"], helper.get_datetime_now(), hashed_password)
                return {"message" : f"Your Password has been changed"}
            else:
                raise HTTPException(status_code=400, detail="Your session has been Expired")
        else:
            raise HTTPException(status_code=400, detail="wrong otp entered")
    else:
        raise HTTPException(status_code=400, detail="User does not exist")
    
    