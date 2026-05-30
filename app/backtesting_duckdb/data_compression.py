import json
import gzip
import base64

def compress_json_for_frontend(data):
    """
    Compress a Python object as gzip+base64 string for frontend transport.

    Args:
        data: Python data to send (dict/list)
    Returns:
        str: base64-encoded gzip-compressed JSON string
    """
    json_bytes = json.dumps(data).encode('utf-8')
    compressed = gzip.compress(json_bytes)
    b64encoded = base64.b64encode(compressed).decode('ascii')
    return b64encoded

# Example usage:
# compressed_str = compress_json_for_frontend(your_json_data)

def decompress_json_from_frontend(b64_gzipped_str):
    """
    Decompress a base64-encoded gzip string sent from frontend.
    Returns the decoded Python object.
    """
    compressed_bytes = base64.b64decode(b64_gzipped_str)
    json_bytes = gzip.decompress(compressed_bytes)
    data = json.loads(json_bytes.decode('utf-8'))
    return data
