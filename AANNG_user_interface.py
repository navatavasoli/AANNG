import tkinter as tk
from PIL import Image, ImageTk
import folium
import json
import webbrowser  # Used to open the map in a browser
from tkinter import messagebox  # Import messagebox explicitly

# Load JSON data and create the map
def load_map_data_and_display():
    try:
        # Load ICCID and coordinates from the generated JSON file
        json_file_path = 'sample_json_callback.json'  # File name if it's in the same directory
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        # Initialize map (centered on an average location or a specific point)
        map_center = [37.7749, -122.4194]  # Example center (San Francisco)
        map_object = folium.Map(location=map_center, zoom_start=5)

        # Add markers for each ICCID location
        for item in data:
            iccid = item["ICCID"]
            lat = item["location"]["latitude"]
            lon = item["location"]["longitude"]
            folium.Marker(
                location=[lat, lon],
                popup=f"ICCID: {iccid}",
                tooltip="Click for more info"
            ).add_to(map_object)

        # Save map to HTML
        map_file = 'map.html'
        map_object.save(map_file)

        # Open the map HTML file in the default web browser
        webbrowser.open(map_file)  # Opens the map in the browser

    except FileNotFoundError:
        print("Error: JSON file not found.")
        messagebox.showerror("File Error", "The JSON file was not found.")
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

# Window configuration and greeting label
window = tk.Tk()
window.configure(bg="#017cfe")  # Shabodi color background
window.geometry("500x500")

# Creating the Shabodi greeting image 
greeting_image_path = 'C:/Users/Neyssa/Downloads/shabodi_icon.jpg'
greeting_image = Image.open(greeting_image_path)
resized_image = greeting_image.resize((50, 50))  # Resize to 50x50 pixels
photo = ImageTk.PhotoImage(resized_image)

# Greeting labels with increased font size
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

# Shabodi icon on the window
path = "C:/Users/Neyssa/Downloads/shabodi_icon.jpg"
load = Image.open(path)
render = ImageTk.PhotoImage(load)
window.iconphoto(False, render)

# New window for monitoring sim card activity
def open_new_window():
    new_window = tk.Toplevel(window)
    new_window.title("Monitoring Sim Card Activity")
    new_window.geometry("300x200")
    tk.Label(new_window, text="Monitoring Sim Card Activity", font=("Helvetica", 14, "bold")).pack(pady=20)
    tk.Label(new_window, text="Here real-time sim card location should show", font=("Helvetica", 12)).pack()
    tk.Label(new_window, text="The ID of the sim card should be here", font=("Helvetica", 12, "bold")).pack()

    # Add the map button inside the new window for sim card activity
    tk.Button(new_window, text="View ICCID Map", command=load_map_data_and_display, height=2, width=20, font=("Helvetica", 12)).pack(pady=10)

# New window for sim card history
def open_new_window2():
    new_window2 = tk.Toplevel(window)
    new_window2.title("Review Sim Card History")
    new_window2.geometry("300x200")
    tk.Label(new_window2, text="Sim Card History", font=("Helvetica", 14, "bold")).pack(pady=20)
    tk.Label(new_window2, text="Past alerts or location information should be saved here", font=("Helvetica", 12, "bold")).pack()

# New window for Settings (placeholder)
def open_new_window3():
    new_window3 = tk.Toplevel(window)
    new_window3.title("Settings")
    new_window3.geometry("300x200")
    tk.Label(new_window3, text="Settings", font=("Helvetica", 14, "bold")).pack(pady=20)

# Create buttons with larger font size and dimensions
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
]

# Center the buttons for the user interface
for button in buttons:
    button.pack(pady=5, expand=True)

window.mainloop()  # Display the window
