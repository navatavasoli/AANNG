import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import folium
import json
import os
import webbrowser
import requests

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

# load and decrypt ICCID data from JSON file
def load_and_decrypt_data(file_path):
    try:
        with open(file_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
        # Load encrypted data and decrypt it
        # cipher = Fernet(key)
        # decrypted_data = cipher.decrypt(encrypted_data).decode()
        # return np.array(json.loads(decrypted_data))
    except Exception as e:
        print(f"Error loading encrypted ICCIDs: {e}")
        return np.array([])

# bandwidth choking for a fraudulent SIM using API
def limit_bandwidth_for_sim(iccid):
    url = 'http://127.0.0.1:7999/qos/v1/bandwidth'  # bandwidth API endpoint
    data = {
        "iccid": iccid,  # suspicious SIM's ICCID
        "action": "limit",  # limit bandwidth
        "limit": "128kbps"  # set a lower bandwidth limit (arbitrary)
    }

    # send API request to limit bandwidth
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

# detect fraudulent activity (unregistered or location-swapped SIM cards)
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
        # Create a pop-up alert for fraudulent activity detection
        if messagebox.askyesno(
            "Fraudulent Activity Detected",
            "\n".join(detected_issues) + "\nDo you want to accept the SIM swap?"
        ):
            # If user chooses yes, process SIM swap acceptance
            iccid_to_swap = messagebox.askstring("Accept SIM Swap", "Enter ICCID to accept SIM swap:")
            if iccid_to_swap:
                process_sim_swap_acceptance(iccid_to_swap)
        else:
            # Optionally, limit bandwidth if swap is not accepted
            if messagebox.askyesno("Limit Bandwidth", "Do you want to limit the bandwidth for this SIM?"):
                iccid_to_limit = messagebox.askstring("Limit Bandwidth", "Enter ICCID to limit bandwidth:")
                if iccid_to_limit:
                    limit_bandwidth_for_sim(iccid_to_limit)

# Process SIM swap acceptance
def process_sim_swap_acceptance(iccid):
    try:
        # Simulate an API call or log the acceptance
        log_message = f"SIM swap accepted for ICCID: {iccid}"
        print(log_message)  # For demonstration; replace with an API call or database update
        with open("sim_swap_log.txt", "a") as log_file:
            log_file.write(f"{log_message}\n")
        messagebox.showinfo("SIM Swap Accepted", f"SIM swap successfully accepted for ICCID: {iccid}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to process SIM swap acceptance: {e}")

# load JSON data and display map
def view_iccid_map():
    # check that the JSON file exists in the same directory as the script
    json_file_path = 'sample_json_callback.json'

    if not os.path.exists(json_file_path):
        messagebox.showerror("File Error", "The JSON file was not found.")
        return

    # load ICCID and coordinates from JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # initialize map (centered on an average location or a specific point)
    map_center = [37.7749, -122.4194]  # ex. center (San Francisco)
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

# window for monitoring sim card activity
def open_new_window():
    new_window = tk.Toplevel(window)
    new_window.title("Monitoring Sim Card Activity")
    new_window.geometry("400x300")

    json_file_path = 'sample_json_callback.json'

    # check if the JSON file exists
    if not os.path.exists(json_file_path):
        messagebox.showerror("File Error", "The JSON file with SIM data was not found.")
        return

    # load and display JSON data
    with open(json_file_path, 'r') as file:
        sim_data = json.load(file)

    # create a text widget to display the JSON data in new window
    text_widget = tk.Text(new_window, wrap='word', font=("Helvetica", 10))
    text_widget.pack(expand=True, fill='both')

    # insert formatted JSON data into text widget
    formatted_data = json.dumps(sim_data, indent=4)
    text_widget.insert(tk.END, formatted_data)
    text_widget.config(state=tk.DISABLED)  # make the text widget read-only

# new window for sim card history
def open_new_window2():
    new_window2 = tk.Toplevel(window)
    new_window2.title("Sim Card History")
    new_window2.geometry("400x300")
    tk.Label(new_window2, text="Sim Card History", font=("Helvetica", 14, "bold")).pack(pady=20)
    tk.Label(new_window2, text="Past alerts or location information should be saved here", font=("Helvetica", 12, "bold")).pack()

# new window for Settings (placeholder)
def open_settings_window():
    settings_window = tk.Toplevel(window)
    settings_window.title("Settings")
    settings_window.geometry("400x300")

    tk.Label(settings_window, text="API Information", font=("Helvetica", 14, "bold")).pack(pady=20)

    # create buttons for each API info
    tk.Button(
        settings_window, text="Bandwidth API Info", command=lambda: open_api_window("Bandwidth"),
        height=3, width=25, background='#ffffff', foreground='black',
        font=("Helvetica", 14, "bold")
    ).pack(pady=10)

    tk.Button(
        settings_window, text="Location API Info", command=lambda: open_api_window("Location"),
        height=3, width=25, background='#ffffff', foreground='black',
        font=("Helvetica", 14, "bold")
    ).pack(pady=10)

    # SIM Swap API Button in Settings
    tk.Button(
        settings_window, text="SIM Swap API", command=lambda: open_api_window("SIM Swap"),
        height=3, width=25, background='#ffffff', foreground='black',
        font=("Helvetica", 14, "bold")
    ).pack(pady=10)

def open_api_window(api_type):
    api_window = tk.Toplevel(window)
    api_window.title(f"{api_type} API Information")
    api_window.geometry("400x300")
    tk.Label(api_window, text=f"{api_type} API Information", font=("Helvetica", 14, "bold")).pack(pady=20)

# create the main buttons for the user interface
monitor_button = tk.Button(
    window, text="Monitor Sim Activity", command=open_new_window,
    height=3, width=25, background='#ffffff', foreground='black',
    font=("Helvetica", 14, "bold")
)
monitor_button.pack(pady=20)

history_button = tk.Button(
    window, text="Sim Card History", command=open_new_window2,
    height=3, width=25, background='#ffffff', foreground='black',
    font=("Helvetica", 14, "bold")
)
history_button.pack(pady=20)

view_iccid_map_button = tk.Button(
    window, text="View ICCID Map", command=view_iccid_map,
    height=3, width=25, background='#ffffff', foreground='black',
    font=("Helvetica", 14, "bold")
)
view_iccid_map_button.pack(pady=20)

settings_button = tk.Button(
    window, text="Settings", command=open_settings_window,
    height=3, width=25, background='#ffffff', foreground='black',
    font=("Helvetica", 14, "bold")
)
settings_button.pack(pady=20)

# Exit button is now at the bottom
exit_button = tk.Button(window, text="Exit", command=window.quit, height=3, width=25, background='#ffffff', foreground='black',
                        font=("Helvetica", 14, "bold"))
exit_button.pack(pady=10)

window.mainloop()
