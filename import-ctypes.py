import ctypes
import time
import threading
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

# Function to simulate system activity
def simulate_activity():
    ctypes.windll.user32.mouse_event(0x0001, 0, 0, 0, 0)  # invisible mouse move
    ctypes.windll.user32.keybd_event(0x10, 0, 0, 0)       # Shift press
    ctypes.windll.user32.keybd_event(0x10, 0, 2, 0)       # Shift release

# Background thread to keep Teams active
def keep_teams_active(start_time, end_time, interval=60):
    while True:
        now = datetime.now().time()
        if start_time <= now <= end_time:
            simulate_activity()
        time.sleep(interval)

# Function to start the background thread
def start_monitoring():
    try:
        start_hour = int(start_hour_entry.get())
        start_minute = int(start_minute_entry.get())
        end_hour = int(end_hour_entry.get())
        end_minute = int(end_minute_entry.get())
        start_time = datetime.now().replace(hour=start_hour, minute=start_minute, second=0).time()
        end_time = datetime.now().replace(hour=end_hour, minute=end_minute, second=0).time()
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers for hours and minutes.")
        return

    t = threading.Thread(target=keep_teams_active, args=(start_time, end_time), daemon=True)
    t.start()
    messagebox.showinfo("Started", "Teams Keep-Active running in background.")
    hide_window()

# System tray icon
def hide_window():
    root.withdraw()
    icon.run_detached()

def on_quit(icon, item):
    icon.stop()
    root.destroy()

# Create a simple icon for system tray
def create_image():
    width = 64
    height = 64
    color1 = "green"
    color2 = "white"
    image = Image.new("RGB", (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width//4, height//4, width*3//4, height*3//4), fill=color2)
    return image

icon = Icon("TeamsKeepActive", create_image(), "Teams Keep-Active")
icon.menu = Menu(MenuItem("Quit", on_quit))

# Tkinter GUI
root = tk.Tk()
root.title("Teams Keep-Active App")

tk.Label(root, text="Start Time (HH:MM)").grid(row=0, column=0, padx=10, pady=5)
start_hour_entry = tk.Entry(root, width=3)
start_hour_entry.grid(row=0, column=1)
start_minute_entry = tk.Entry(root, width=3)
start_minute_entry.grid(row=0, column=2)

tk.Label(root, text="End Time (HH:MM)").grid(row=1, column=0, padx=10, pady=5)
end_hour_entry = tk.Entry(root, width=3)
end_hour_entry.grid(row=1, column=1)
end_minute_entry = tk.Entry(root, width=3)
end_minute_entry.grid(row=1, column=2)

tk.Button(root, text="Start", command=start_monitoring).grid(row=2, column=0, columnspan=3, pady=10)

root.mainloop()
