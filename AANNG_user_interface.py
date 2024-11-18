import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import folium
import json
import os
import webbrowser  # open the map in the web browser
import numpy as np
import requests  # For API call to limit bandwidth

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
    text=" Welcome To AANNG Sim Swap Fraud Alert Application!",
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

# function to load and decrypt ICCID data from JSON file
def load_and_decrypt_data(file_path):
    try:
        with open(file_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
        # Load encrypted data and decrypt it
        cipher = Fernet(key)
        decrypted_data = cipher.decrypt(encrypted_data).decode()
        return np.array(json.loads(decrypted_data))
    except Exception as e:
        print(f"Error loading encrypted ICCIDs: {e}")
        return np.array([])

# Function to limit bandwidth for a specific SIM using API
def limit_bandwidth_for_sim(iccid):
    url = 'http://127.0.0.1:7999/qos/v1/bandwidth'  # Bandwidth API endpoint
    data = {
        "iccid": iccid,  # The ICCID of the fraudulent SIM
        "action": "limit",  # Action to limit bandwidth
        "limit": "128kbps"  # Set a lower bandwidth limit, modify as necessary
    }

    # Send API request to limit bandwidth
    try:
        response = requests.post(url, json=data)
        response_data = response.json()
        if response.status_code == 200 and response_data.get("status") == "success":
            messagebox.showinfo("Success", f"Bandwidth successfully limited for SIM: {iccid}")
        else:
            messagebox.showerror("Error", f"Failed to limit bandwidth for SIM: {iccid}")
    except requests.exceptions.RequestException as e:
        print(f"Error limiting bandwidth: {e}")
        messagebox.showerror("Error", "An error occurred while limiting bandwidth.")

# function to detect fraudulent activity (unregistered or location-swapped SIM cards)
def detection(current_iccid_data, registered_iccids, window):
    detected_issues = []
    for entry in current_iccid_data:
        # get SIM number and location of SIM
        iccid = entry.get('iccid')
        location = entry.get('location')

        if iccid not in registered_iccids:
            detected_issues.append(f"Unregistered SIM detected in network: {iccid}, {location}")
        else:
            registered_location = registered_iccids.get(iccid)
            if location != registered_location:
                detected_issues.append(f"Location change detected for SIM {iccid}: {location}")

    if detected_issues:
        # Show an alert in the Tkinter window
        if messagebox.askyesno("Fraudulent Activity Detected", "\n".join(detected_issues) + "\nDo you want to limit the bandwidth?"):
            # If user chooses yes, prompt for action to limit bandwidth
            iccid_to_limit = messagebox.askstring("Limit Bandwidth", "Enter ICCID to limit bandwidth:")
            if iccid_to_limit:
                limit_bandwidth_for_sim(iccid_to_limit)

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

    # load registered SIM ICCIDs from the second script
    registered_iccids = load_and_decrypt_data('registered_sims.json')

    # Check for fraudulent activity
    detection(data, registered_iccids, window)

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
    
    # Check if the JSON file exists
    if not os.path.exists(json_file_path):
        messagebox.showerror("File Error", "The JSON file with SIM data was not found.")
        return
    
    # Load the JSON data and display it
    with open(json_file_path, 'r') as file:
        sim_data = json.load(file)
    
    # Create a text widget to display the JSON data in the new window
    text_widget = tk.Text(new_window, wrap='word', font=("Helvetica", 10))
    text_widget.pack(expand=True, fill='both')
    
    # Insert formatted JSON data into the text widget
    formatted_data = json.dumps(sim_data, indent=4)
    text_widget.insert(tk.END, formatted_data)
    text_widget.config(state=tk.DISABLED)  # Make the text widget read-only

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
