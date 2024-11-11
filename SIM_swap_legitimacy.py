# Assumption: All devices under bandwidth enterprise network have registered SIM IDs (ICCIDs) under a JSON file
import json
import numpy as np
import time
import requests
from datetime import datetime
from cryptography.fernet import Fernet

# initialize JSON file containing the registed SIMs (assume provided by network)
json_file_path = 'registered_sims.json'

# generate a key and instantiate a Fernet object
try:
    with open('encryption_key.key', 'rb') as key_file:
        key = key_file.read()
except FileNotFoundError:
    key = Fernet.generate_key()
    with open('encryption_key.key', 'wb') as key_file:
        key_file.write(key)

cipher = Fernet(key)

# encrypt data and save to file
def encrypt_and_save_data(data, file_path):
    json_data = json.dumps(data)  # convert data to JSON string
    encrypted_data = cipher.encrypt(json_data.encode())  # encrypt JSON string
    with open(file_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data)

# decrypt and load data from file
def load_and_decrypt_data(file_path):
    try:
        with open(file_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
        decrypted_data = cipher.decrypt(encrypted_data).decode()
        return np.array(json.loads(decrypted_data))
    except Exception as e:
        print(f"Error loading encrypted ICCIDs: {e}")
        return np.array([])

# put data into a NumPy array
def load_iccids(file_path):
    # Load and decrypt data from JSON file containing registered SIMs
    return load_and_decrypt_data(file_path)

# configure Shabodi's Bandwidth API
API_URL = "https://api.shabodi.com/bandwidth"  
API_HEADERS = {
    "Authorization": "Bearer YOUR_API_TOKEN",   # API TOKEN
    "Content-Type": "application/json"
}

# fetch bandwidth data using API
def fetch_bandwidth_data():
    try:
        response = requests.get(API_URL, headers=API_HEADERS)
        response.raise_for_status()
        return response.json()  # Parse and return JSON response
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

# log bandwidth data 
def log_bandwidth_data(data):
    data['timestamp'] = datetime.now().isoformat() # include a timestamp
    with open('bandwidth_log.json', 'a') as log_file:
        log_file.write(json.dumps(data) + "\n")

# detect duplicated or swapped sims
def detection(current_iccid_data, registered_iccids):
    detected_issues = []
    for entry in current_iccid_data:

        # get SIM number and location of SIM
        iccid = entry.get('iccid')
        location = entry.get('location')  
        
        if iccid not in registered_iccids:
            detected_issues.append(f"Unregistered SIM detected in network: {iccid}, {iccid}: {location}")
        else:
            registered_location = registered_iccids.get(iccid) 
            if location != registered_location:
                detected_issues.append(f"Location change detected for SIM {iccid}: {location}")

    if detected_issues:
        print("Detected SIM issues:", detected_issues)

# loop to perform these checks once an hour
while True:
    # update registed ICCID information from network
    registered_iccids = load_iccids(json_file_path)
    print("Registered ICCIDs:", registered_iccids)

    # fetch current bandwidth data
    bandwidth_data = fetch_bandwidth_data()
    if bandwidth_data:
        log_bandwidth_data(bandwidth_data)
        print("Logged bandwidth data:", bandwidth_data)

    # check for suspicious activity (duplication or removal/addition)
    if 'sims' in bandwidth_data:  # Assuming 'sims' key holds the current SIM data in API response
        detection(bandwidth_data['sims'], registered_iccids)

    time.sleep(3600) # once/hour loop