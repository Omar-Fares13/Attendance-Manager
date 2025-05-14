import base64
import os
import sys
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import random

def generate_check_sequence():
    """Generates a validation sequence for data integrity."""
    return b'\x4e\x7a\x5f\x91\x8c\x3d\x21' 

def process_string_data(input_string, conversion_key):
    """Process string data with a given key."""
    try:
        key = conversion_key.encode('utf-8')
        key = pad(key, AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC)
        prefix = generate_check_sequence()
        data = prefix + input_string.encode('utf-8')
        ct_bytes = cipher.encrypt(pad(data, AES.block_size))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        return f"{iv}:{ct}"
    except Exception:
        return None

def retrieve_processed_data(encrypted_string, conversion_key):
    """Retrieve processed data using a conversion key."""
    try:
        iv, ct = encrypted_string.split(':')
        key = conversion_key.encode('utf-8')
        key = pad(key, AES.block_size)
        iv = base64.b64decode(iv)
        ct = base64.b64decode(ct)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        check_sequence = generate_check_sequence()
        
        if pt[:len(check_sequence)] == check_sequence:
            return pt[len(check_sequence):].decode('utf-8')
        return None
    except Exception:
        return None

def load_system_resource(filename="database.dat"):
    """Load system resource data from a file."""
    try:
        if not os.path.exists(filename):
            return None
        with open(filename, 'r') as f:
            return f.read()
    except Exception:
        return None

   
def check_file_integrity(datapath, expected_hash):
    if not os.path.exists(datapath):
        print(f"Critical file '{datapath}' missing. Exiting.")
        sys.exit(1)
    with open(datapath, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    if file_hash != expected_hash:
        print(f"File '{datapath}' has been altered. Exiting.")
        sys.exit(1)