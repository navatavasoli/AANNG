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

# encrypt data and save to file
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
     #   return np.array(json.loads(decrypted_data))
    except Exception as e:
        print(f"Error loading encrypted ICCIDs: {e}")
        return np.array([])

# Load ICCIDs into a NumPy array
def load_iccids(file_path):
    return load_and_decrypt_data(file_path)

# Bandwidth API configuration
API_URL = "http://127.0.0.1:7999/qos/v1/bandwidth"
LOCATION_API_URL = "http://127.0.0.1:7999/location/v1/center"
DEVICE_ID = "17"  # Set the device ID you want to query
AEP_HOST = "192.168.3.18"  # Shabodi server IP
CLIENT_ID = "380dfca1-6539-4890-9595-21a57c8f907d"
CLIENT_SECRET = "enMKQcRauITqqdsDGsbNDUN_JlNgLYQkkdPhe5IF8Ws"

# Function to request the access token
def get_token(client_id, client_secret):
    url = f"http://{AEP_HOST}:31002/security/v1/token"  # Adjusted port and endpoint
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "client_id": client_id,
        "client_secret": client_secret
    }

    # Making the POST request to obtain the token
    response = requests.post(url, headers=headers, json=data, verify=False)
    if response.status_code == 200:
        token = response.json().get("access_token")
        print("Access Token:", token)
        return token
    else:
        print("Failed to retrieve token:", response.status_code, response.json())
        return None

# fetch the device's location
def fetch_device_location(token, device_id):
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
        response = requests.get(f"{LOCATION_API_URL}?deviceId={device_id}", headers=headers)

        if response.status_code == 200:
            location_data = response.json()
            if "location" in location_data:
                device_location = location_data["location"][0]
                return device_location  # return device latitude, longitude, and altitude
            else:
                print(f"Failed to retrieve location: {response.status_code}, {response.json()}")
                return None
        else:
            print(f"Failed to fetch device location: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching location: {e}")
        return None

# verify the location within a specific area
def verify_device_location(token, device_id, latitude, longitude, radius):
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
        body = {
            "device": {
                "deviceId": device_id
            },
            "area": {
                "areaType": "CIRCLE",
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": radius
            },
            "maxAge": 120  # maxAge in seconds, adjust if needed
        }
        response = requests.post(f"{LOCATION_API_URL}/verify", headers=headers, json=body)

        if response.status_code == 200:
            verification_result = response.json()
            return verification_result
        else:
            print(f"Failed to verify device location: {response.status_code}, {response.json()}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error verifying location: {e}")
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

        # space to accept the SIM Swap

if __name__ == "__main__":
    token = get_token(CLIENT_ID, CLIENT_SECRET)  # Get the token

    if token:
        while True:
            registered_iccids = load_iccids(json_file_path)
            print("Registered ICCIDs:", registered_iccids)

            # fetch current data with token
            bandwidth_data = fetch_bandwidth_data(token)
            if bandwidth_data:
                log_bandwidth_data(bandwidth_data)
                print("Logged bandwidth data:", bandwidth_data)

            if 'sessions' in bandwidth_data:
                detection(bandwidth_data['sessions'], registered_iccids)

            device_location = fetch_device_location(token, DEVICE_ID)
            if device_location:
                print(f"Device {DEVICE_ID} location: Latitude={device_location['latitude']}, Longitude={device_location['longitude']}, Altitude={device_location['altitude']}")

                center_latitude = 50.735851
                center_longitude = 7.10066
                radius = 50000  # 50 km radius

                location_verification = verify_device_location(token, DEVICE_ID, center_latitude, center_longitude, radius)
                if location_verification:
                    print(f"Location verification result: {location_verification['verificationResult']}")

            time.sleep(3600)  # hourly loop
