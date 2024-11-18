import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import os
import folium
import webbrowser
import numpy as np
from datetime import datetime
from cryptography.fernet import Fernet
import requests
import time

# window configuration and greeting label
window = tk.Tk()
window.configure(bg="#017cfe")  # shabodi color background
window.geometry("500x500")

# creating the Shabodi greeting image 
greeting_image_path = 'C:/Users/Neyssa/Downloads/shabodi_icon.jpg'
greeting_image = Image.open(greeting_image_path)
resized_image = greeting_image.resize((50, 50)) 
photo = ImageTk.PhotoImage(resized_image)

# greeting labels 
greeting = tk.Label(
    text=" Welcome To AANNG's SIM Fraud Alert Application!",
    background='#ffffff', foreground='black', image=photo, compound='left',
    font=("Helvetica", 16, "bold")
)
greeting2 = tk.Label(
    text="How Would You Like To Proceed?",
    background='#ffffff', foreground='black',
    font=("Helvetica", 14, "bold")
)
greeting.pack(pady=10)
greeting2.pack(pady=5)
greeting.image = photo

# shabodi icon on the window
path = "C:/Users/Neyssa/Downloads/shabodi_icon.jpg"
load = Image.open(path)
render = ImageTk.PhotoImage(load)
window.iconphoto(False, render)

# function to load JSON data and display map
def load_map_data_and_display():
    # check that the JSON file exists in the same directory as the script
    json_file_path = 'sample_json_callback.json'
    
    if not os.path.exists(json_file_path):
        messagebox.showerror("File Error", "The JSON file was not found.")
        return
    
    # load ICCID and coordinates from JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # initialize map (centered on an average location or a specific point)
    map_center = [37.7749, -122.4194]  # Example center (San Francisco)
    map_object = folium.Map(location=map_center, zoom_start=5)

    # add markers for each ICCID location
    for item in data:
        iccid = item["ICCID"]
        lat = item["location"]["latitude"]
        lon = item["location"]["longitude"]
        folium.Marker(
            location=[lat, lon],
            popup=f"ICCID: {iccid}",
            tooltip="Click for more info"
        ).add_to(map_object)

    # save map to HTML
    map_file = 'map.html'
    map_object.save(map_file)

    # open the map in the default web browser
    webbrowser.open(f'file://{os.path.realpath(map_file)}')

# new window for monitoring sim card activity
def open_new_window():
    new_window = tk.Toplevel(window)
    new_window.title("Monitoring Sim Card Activity")
    new_window.geometry("400x300")
    
    json_file_path = 'sample_json_callback.json'
    
    # check if the JSON file exists
    if not os.path.exists(json_file_path):
        messagebox.showerror("File Error", "The JSON file with SIM data was not found.")
        return
    
    # load the JSON data and display it
    with open(json_file_path, 'r') as file:
        sim_data = json.load(file)
    
    # create a text widget to display the JSON data in the new window
    text_widget = tk.Text(new_window, wrap='word', font=("Helvetica", 10))
    text_widget.pack(expand=True, fill='both')
    
    # insert formatted JSON data into the text widget
    formatted_data = json.dumps(sim_data, indent=4)
    text_widget.insert(tk.END, formatted_data)
    text_widget.config(state=tk.DISABLED)  # make the text widget read-only

# new window for sim card history
def open_new_window2():
    new_window2 = tk.Toplevel(window)
    new_window2.title("Review Sim Card History")
    new_window2.geometry("300x200")
    tk.Label(new_window2, text="Sim Card History", font=("Helvetica", 14, "bold")).pack(pady=20)
    tk.Label(new_window2, text="Past alerts or location information should be saved here", font=("Helvetica", 12, "bold")).pack()

# new window for Settings (placeholder)
def open_new_window3():
    new_window3 = tk.Toplevel(window)
    new_window3.title("Settings")
    new_window3.geometry("300x200")
    tk.Label(new_window3, text="Settings", font=("Helvetica", 14, "bold")).pack(pady=20)

# create inter-file algorithm to create a pop-up alert and a history record of past alerts
# accept change/decline change
# get data of coordinates w/a picture
def alert_mechanism():
    # if detected issues from 

# create buttons with larger font size and dimensions
buttons = [
    tk.Button(
        window, text="Monitor Sim Card Activity", command=open_new_window, 
        height=3, width=25, background='#ffffff', foreground='black', 
        font=("Helvetica", 14, "bold")
    ),
    tk.Button(
        window, text="Review Sim Card History", command=open_new_window2, 
        height=3, width=25, background='#ffffff', foreground='black', 
        font=("Helvetica", 14, "bold")
    ),
    tk.Button(
        window, text="Settings", command=open_new_window3, 
        height=3, width=25, background='#ffffff', foreground='black', 
        font=("Helvetica", 14, "bold")
    ),
    tk.Button(
        window, text="View ICCID Map", command=load_map_data_and_display, 
        height=3, width=25, background='#ffffff', foreground='black', 
        font=("Helvetica", 14, "bold")
    )
]

# center the buttons for the user interface
for button in buttons:
    button.pack(pady=5, expand=True)


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

window.mainloop()  # display the window
