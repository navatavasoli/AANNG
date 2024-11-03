# Detection of SIM Swap Fraud or Duplication
# Blame: Nava

"""
1. Import JSON library and reader to read files from the network provider on registered SIMs
2. Before parsing, check if user has been authenticated prior to accessing
3. Measure current bandwidth vs capacity (Bandwidth API) (once an hour, looping function)
4. Parse JSON file and read data: ICCID and Location of ICCID (use location API) (once an hour)
5. Function to detect any duplicated ICCID OR a location change of a registered SIM 
"""

#loop function to continuously read the data
# SIM cards currently registered in this enterprise's bandwidth 
# write a function to obtain the SIM of the device from settings OR just have a list and parse the b2andwidth data of registered SIMs in the data 

# import the JSON file, parse the JSON file loop once every hour 


# Pseudocode *INTERNAL*
# Assumption: All devices under bandwidth enterprise network have registered SIM IDs (ICCIDs) under a JSON file
import json
import numpy as np
import time
import requests
from datetime import datetime

# initialize JSON file containing the registed SIMs (assume provided by network)
json_file_path = 'registered_sims.json'

# put data into a NumPy array
def load_iccids(file_path):
    try:
        with open(file_path, 'r') as json_file:
            registered_iccids = json.load(json_file)
        return np.array(registered_iccids)
    except Exception as e:
        print(f"Error loading ICCIDs: {e}")
        return np.array([])

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

    time.sleep(3600)





