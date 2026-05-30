

from slugify import slugify
import secrets
import string
import time
import re
from datetime import datetime, timedelta
import pytz

def get_unique_link(link:str ="", list_of_links:list = [] ):
    existing_numbers = []

    for i in range(0, len(list_of_links)):
        try:
            slice_int = int(list_of_links[i][len(link)+1:])
            # print("slice_int", slice_int)
            existing_numbers.append(slice_int)
        except:
            # print("hello")
            pass
    # print(existing_numbers)
    # Generate a unique number
    if existing_numbers:
        new_number = max(existing_numbers) + 1  # Increment the maximum number
        for j in range(1, max(existing_numbers)+1):
            if j in existing_numbers:
                # print(j)
                pass
            else:
                new_number = j
                break
                
    else:
        new_number = 1  


    new_link = f"{link}-{new_number}"
    return new_link

def title_to_string(temp_str: str):

    temp_str = temp_str.lower()
    def check_string(s):
        # Check if the string contains only a-z and 0-9
        if re.fullmatch(r'[a-z0-9]*', s):
            return True
        return False


    link = ""
    flag = 0
    # print(temp_str)
    for i in range(0, len(temp_str)):
        if check_string(temp_str[i]):
            link += temp_str[i]  # Append valid character
            
            flag = 0
        else:
            if flag == 0:
                link += '-'  # Append '-' for invalid character
                
                flag = 1
    if check_string(link[0]) == False:
        link = link[1:len(link) ]
    
    if check_string(link[len(link)-1]) ==  False:
        link = link[:len(link)-1]
    return link

def increment_suffix(temp):
    i = temp.rfind("-")  # Find the last occurrence of '-'
    if i == -1:  
        return temp + "-1"  # If no '-', just append '-1'
    
    prefix, num = temp[:i], temp[i+1:]  
    if num.isdigit():  
        return f"{prefix}-{int(num) + 1}"  # Increment the number
    return temp + "-1"  # If suffix isn't a number, just add '-1'


def generate_unique_slug(text, random_length=20, slug_max_length=50):
    base_slug = slugify(text, max_length=slug_max_length, word_boundary=True)
    timestamp_ms = int(time.time() * 1000)
    allowed_chars = string.ascii_lowercase + string.digits
    random_suffix = ''.join(secrets.choice(allowed_chars) for _ in range(random_length))

    unique_slug = f"{base_slug}-{timestamp_ms}-{random_suffix}"
    return unique_slug


def get_datetime_now():
    return datetime.strptime(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
