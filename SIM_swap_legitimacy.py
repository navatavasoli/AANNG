import json
import numpy as np
import time
import requests
from datetime import datetime
from cryptography.fernet import Fernet

# Initialize JSON file containing the registered SIMs (assume provided by the network)
json_file_path = 'registered_sims.json'

# Generate a key and instantiate a Fernet object
try:
    with open('encryption_key.key', 'rb') as key_file:
        key = key_file.read()
except FileNotFoundError:
    key = Fernet.generate_key()
    with open('encryption_key.key', 'wb') as key_file:
        key_file.write(key)

cipher = Fernet(key)

# Encrypt data and save to file
def encrypt_and_save_data(data, file_path):
    json_data = json.dumps(data)  # convert data to JSON string
    encrypted_data = cipher.encrypt(json_data.encode())  # encrypt JSON string
    with open(file_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data)

# Decrypt and load data from file
def load_and_decrypt_data(file_path):
    try:
        with open(file_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
        decrypted_data = cipher.decrypt(encrypted_data).decode()
        return np.array(json.loads(decrypted_data))
    except Exception as e:
        print(f"Error loading encrypted ICCIDs: {e}")
        return np.array([])

# Load ICCIDs into a NumPy array
def load_iccids(file_path):
    return load_and_decrypt_data(file_path)

# Bandwidth API configuration
API_URL = "http://127.0.0.1:7999/qos/v1/bandwidth"
DEVICE_ID = "17"  # Set the device ID you want to query
API_HEADERS = {
    "accept": "application/json"
}

# Fetch bandwidth data using API
def fetch_bandwidth_data():
    try:
        # Include deviceId in the query string
        response = requests.get(f"{API_URL}?deviceId={DEVICE_ID}", headers=API_HEADERS)
        
        if response.status_code == 200:
            return response.json()  # Parse and return JSON response
        else:
            print(f"API request failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

# Log bandwidth data
def log_bandwidth_data(data):
    data['timestamp'] = datetime.now().isoformat()  # Include a timestamp
    with open('bandwidth_log.json', 'a') as log_file:
        log_file.write(json.dumps(data) + "\n")

# Detect duplicated or swapped SIMs
def detection(current_iccid_data, registered_iccids):
    detected_issues = []
    for entry in current_iccid_data:
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

# Main loop to perform checks once an hour
while True:
    # Update registered ICCID information from network
    registered_iccids = load_iccids(json_file_path)
    print("Registered ICCIDs:", registered_iccids)

    # Fetch current bandwidth data
    bandwidth_data = fetch_bandwidth_data()
    if bandwidth_data:
        log_bandwidth_data(bandwidth_data)
        print("Logged bandwidth data:", bandwidth_data)

    # Check for suspicious activity (duplication or removal/addition)
    if 'sessions' in bandwidth_data:  # Assuming 'sessions' key holds the current SIM data in API response
        detection(bandwidth_data['sessions'], registered_iccids)

    time.sleep(3600)  # Loop every hour
