import redis

redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

def key_exists(key):
    # Check if the key exists
    return redis_client.exists(key) > 0

def set_cache(key, value):
    # Convert the key and value to strings
    key_str = str(key)  # Convert the key (tuple) to a string
    value_str = value  # Convert the value to a string
    # value_str = value
    redis_client.set(key_str, value_str, ex= 12*60*60)

def get_cache(key):
    key_str = str(key)
    return redis_client.get(key_str)