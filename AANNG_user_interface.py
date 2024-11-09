import tkinter as tk
from PIL import Image, ImageTk
import folium
import json
from tkhtmlview import HTMLLabel

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

# Function to load coordinates from the JSON file and display the map
def load_map_data_and_display():
    # Load ICCID and coordinates from the JSON file
    json_file_path = 'path/to/your/coordinates.json'  # Replace with your actual JSON file path
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Initialize the map (centered on a specific location, or you can calculate the center dynamically)
    map_center = [37.7749, -122.4194]  # Example center (San Francisco)
    map_object = folium.Map(location=map_center, zoom_start=10)

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

    # Save map to an HTML file
    map_file = 'map.html'
    map_object.save(map_file)

    # Create a new window to display the map
    map_window = tk.Toplevel(window)
    map_window.title("ICCID Location Map")
    map_window.geometry("600x400")

    # Display the HTML map in Tkinter using tkhtmlview
    map_label = HTMLLabel(map_window, html=open(map_file).read())
    map_label.pack(fill="both", expand=True)

# New window for monitoring sim card activity
def open_new_window():
    new_window = tk.Toplevel(window)
    new_window.title("Monitoring Sim Card Activity")
    new_window.geometry("300x200")
    tk.Label(new_window, text="Monitoring Sim Card Activity", font=("Helvetica", 14, "bold")).pack(pady=20)
    tk.Label(new_window, text="Here real-time sim card location should show", font=("Helvetica", 12)).pack()
    tk.Label(new_window, text="The ID of the sim card should be here", font=("Helvetica", 12, "bold")).pack()
    
    # Add a button in the new window to view the map
    map_button = tk.Button(
        new_window, text="View ICCID Map", command=load_map_data_and_display,
        height=2, width=20, background='#ffffff', foreground='black',
        font=("Helvetica", 12, "bold")
    )
    map_button.pack(pady=10)

# New window for sim card history
def open_new_window2():
    new_window2 = tk.Toplevel(window)
    new_window2.title("Review Sim Card History")
    new_window2.geometry("300x200")
    tk.Label(new_window2, text="Sim Card History", font=("Helvetica", 14, "bold")).pack(pady=20)
    tk.Label(new_window2, text="Past alerts or location information should be saved here", font=("Helvetica", 12, "bold")).pack()

# New window for Settings (placeholder)
# We should add an option to see lag time (latency), but there is no rush for this
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
