import tkinter as tk
window = tk.Tk()
window.configure(bg="white") #maroon colour 
window.geometry("400x400")
greeting = tk.Label(text="USER INTERFACE PROTOTYPE FOR AANNG")
greeting.pack()

#new window for monitoring sim card activity
def open_new_window():
    new_window = tk.Toplevel(window)
    new_window.title("Monitoring Sim Card Activity")
    new_window.geometry("300x200")
    tk.Label(new_window, text="Monitoring Sim Card Activity").pack(pady=20)
    tk.Label(new_window, text="here real time sim card location should show") #fix this
    tk.Label(new_window, text="The id of the sim card should be here")

# new window for sim card history
def open_new_window2():
    new_window2 = tk.Toplevel(window)
    new_window2.title("Sim Card History")
    new_window2.geometry("300x200")
    tk.Label(new_window2, text="Sim Card History").pack(pady=20)
    tk.Label(new_window2, text="here past alerts or locations, information of that sort should be saved here")

#new window for Settings (again this is a placeholder)
def open_new_window3():
    new_window3 = tk.Toplevel(window)
    new_window3.title("Settings")
    new_window3.geometry("300x200")
    tk.Label(new_window3, text="Settings").pack(pady=20)

# create 3 buttons (settings is a place holder for potentially something else) I will want the buttons closer together in the near future.
def on_button_click(button_number):
    print("redirecting to {button_number} window ")

buttons = [
    tk.Button(window, text="Monitor Sim Card Activity", command=open_new_window, height=2, width=20),
    tk.Button(window, text="Sim Card History", command=open_new_window2, height=2, width=20),
    tk.Button(window, text="Settings", command=open_new_window3, height=2, width=20),
]

# Center the buttons for the user interface
for button in buttons:
    button.pack(expand=True)
if on_button_click(1):
    button1 = tk.Button(window, text="Open New Window", command=open_new_window, height=2, width=20)


button.pack(expand=True)



window.mainloop() # need a mainloop so that the window actually pops up and stays up or else if you dont have that, you won't see anything
