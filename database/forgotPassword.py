import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter
from database.configurations import collection_user
from fastapi import Body

# oauth_router = APIRouter()



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

# Example usage:
# if __name__ == "__main__":
#     recipient = "recipient@example.com"
#     otp_code = "123456"
#     # Make sure to replace the sender_email and sender_password with real credentials or use environment variables.
#     send_otp_email(recipient, otp_code, sender_email="your_email@gmail.com", sender_password="your_email_password")


# @oauth_router.post("/sendOTP") 
# async def forgotOTP_verify_email(email : str = Body(...)):
#     print(email)
#     # otp = generate_otp(length=6)
#     # user_data = collection_user.find_one({"email": email})#, { "_id": 0, "email": 1, "otp": 1 })
#     # print(user_data)

#     return {"message" : f"OTP has been send to {email}"}
    
