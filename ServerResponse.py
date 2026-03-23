import ctypes
import time
import threading
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem
import json
import os
import sys

# Error logging
def log_error(message):
    with open("error.log", "a") as f:
        f.write(f"{datetime.now()}: {message}\n")

# Generate next 7 working days from today
def get_next_7_working_days():
    today = datetime.now()
    working_days = []
    current_date = today
    
    while len(working_days) < 7:
        # Monday is 0, Friday is 4
        if current_date.weekday() < 5:  # Exclude weekends (Sat=5, Sun=6)
            working_days.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    return working_days

# Load schedule from JSON
def load_schedule():
    try:
        if os.path.exists("schedule.json"):
            with open("schedule.json", "r") as f:
                schedule = json.load(f)
                return schedule
    except Exception as e:
        log_error(f"Error loading schedule.json: {e}")
    return None

# Function to simulate system activity
def simulate_activity():
    try:
        ctypes.windll.user32.mouse_event(0x0001, 0, 0, 0, 0)  # invisible mouse move
        ctypes.windll.user32.keybd_event(0x10, 0, 0, 0)       # Shift press
        ctypes.windll.user32.keybd_event(0x10, 0, 2, 0)       # Shift release
    except Exception as e:
        log_error(f"Error simulating activity: {e}")

# Background thread to keep Teams active
def keep_teams_active(start_time, end_time, interval=60):
    while True:
        try:
            now = datetime.now().time()
            if start_time <= now <= end_time:
                simulate_activity()
            time.sleep(interval)
        except Exception as e:
            log_error(f"Error in keep_teams_active: {e}")
            time.sleep(interval)

# Function to start the background thread
def start_monitoring():
    try:
        start_hour = int(start_hour_entry.get())
        start_minute = int(start_minute_entry.get())
        end_hour = int(end_hour_entry.get())
        end_minute = int(end_minute_entry.get())
        
        if not (0 <= start_hour <= 23 and 0 <= start_minute <= 59):
            messagebox.showerror("Error", "Start time must be valid (hours 0-23, minutes 0-59)")
            return
        if not (0 <= end_hour <= 23 and 0 <= end_minute <= 59):
            messagebox.showerror("Error", "End time must be valid (hours 0-23, minutes 0-59)")
            return
            
        start_time = datetime.now().replace(hour=start_hour, minute=start_minute, second=0).time()
        end_time = datetime.now().replace(hour=end_hour, minute=end_minute, second=0).time()
    except ValueError:
        messagebox.showerror("Error", "Please enter valid hours (0-23) and minutes (0-59)")
        return

    t = threading.Thread(target=keep_teams_active, args=(start_time, end_time), daemon=True)
    t.start()
    messagebox.showinfo("Started", f"Server Keep-Alive running from {start_hour}:{start_minute:02d} to {end_hour}:{end_minute:02d}")
    hide_window()

# System tray icon
def hide_window():
    root.withdraw()
    try:
        icon.run_detached()
    except Exception as e:
        log_error(f"Error in tray icon: {e}")

def on_quit(icon, item):
    try:
        icon.stop()
    except:
        pass
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

# Function to save schedule
def save_schedule():
    try:
        start_h = int(start_hour_entry.get())
        start_m = int(start_minute_entry.get())
        end_h = int(end_hour_entry.get())
        end_m = int(end_minute_entry.get())
        
        if not (0 <= start_h <= 23 and 0 <= start_m <= 59):
            messagebox.showerror("Error", "Start time must be valid (hours 0-23, minutes 0-59)")
            return
        if not (0 <= end_h <= 23 and 0 <= end_m <= 59):
            messagebox.showerror("Error", "End time must be valid (hours 0-23, minutes 0-59)")
            return
        
        # Get manual dates entered by user
        dates_text = dates_text_widget.get("1.0", tk.END).strip()
        manual_dates = [d.strip() for d in dates_text.split("\n") if d.strip()]
        
        # Get next 7 working days automatically
        auto_dates = get_next_7_working_days()
        
        # Combine: manual dates + auto-generated next 7 working days
        all_dates = list(dict.fromkeys(manual_dates + auto_dates))  # Remove duplicates while preserving order
        
        schedule_data = {
            "dates": "\n".join(all_dates),
            "start_hour": start_h,
            "start_minute": start_m,
            "end_hour": end_h,
            "end_minute": end_m,
            "exclude_weekends": exclude_var.get()
        }
        
        with open("schedule.json", "w") as f:
            json.dump(schedule_data, f, indent=2)
        
        # Update the text widget to show the merged dates
        dates_text_widget.delete("1.0", tk.END)
        dates_text_widget.insert("1.0", "\n".join(all_dates))
        
        messagebox.showinfo("Success", f"Schedule saved!\nManual dates + Next 7 working days = {len(all_dates)} dates total")
        status_label.config(text="Status: Schedule saved ✓", foreground="green")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid hours (0-23) and minutes (0-59)")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save: {e}")

try:
    # Create Tkinter GUI
    root = tk.Tk()
    root.title("Server Keep-Alive App")
    root.geometry("500x580")
    root.resizable(False, False)
    
    # Load schedule
    schedule = load_schedule()
    
    # Set defaults from schedule if available
    default_start_hour = "7"
    default_start_minute = "0"
    default_end_hour = "17"
    default_end_minute = "0"
    scheduled_dates = ""
    exclude_weekends = False
    
    # Load manual dates from schedule
    manual_dates = []
    if schedule:
        default_start_hour = str(schedule.get("start_hour", 7))
        default_start_minute = str(schedule.get("start_minute", 0)).zfill(2)
        default_end_hour = str(schedule.get("end_hour", 17))
        default_end_minute = str(schedule.get("end_minute", 0)).zfill(2)
        exclude_weekends = schedule.get("exclude_weekends", False)
        dates = schedule.get("dates", "")
        if isinstance(dates, str):
            manual_dates = [d.strip() for d in dates.split("\n") if d.strip()]
        elif isinstance(dates, list):
            manual_dates = dates
    
    # Auto-generate next 7 working days
    auto_dates = get_next_7_working_days()
    
    # Combine manual + auto-generated dates (remove duplicates, preserve order)
    all_dates = list(dict.fromkeys(manual_dates + auto_dates))
    scheduled_dates = "\n".join(all_dates)
    
    # Title
    title_label = tk.Label(root, text="Server Keep-Alive Console", font=("Arial", 12, "bold"))
    title_label.pack(padx=10, pady=10)
    
    tk.Label(root, text="─" * 60, foreground="gray").pack(padx=10)
    
    # Time Settings Section
    tk.Label(root, text="Time Settings", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=5)
    
    # Start Time Frame
    start_frame = tk.Frame(root)
    start_frame.pack(padx=10, pady=5)
    
    tk.Label(start_frame, text="Start time (HH:MM):", font=("Arial", 10)).pack(side="left", padx=5)
    start_hour_entry = tk.Entry(start_frame, width=3, font=("Arial", 11))
    start_hour_entry.pack(side="left", padx=2)
    start_hour_entry.insert(0, default_start_hour)
    
    tk.Label(start_frame, text=":", font=("Arial", 11)).pack(side="left", padx=2)
    
    start_minute_entry = tk.Entry(start_frame, width=3, font=("Arial", 11))
    start_minute_entry.pack(side="left", padx=2)
    start_minute_entry.insert(0, default_start_minute)

    # End Time Frame
    end_frame = tk.Frame(root)
    end_frame.pack(padx=10, pady=5)
    
    tk.Label(end_frame, text="End time (HH:MM):", font=("Arial", 10)).pack(side="left", padx=5)
    end_hour_entry = tk.Entry(end_frame, width=3, font=("Arial", 11))
    end_hour_entry.pack(side="left", padx=2)
    end_hour_entry.insert(0, default_end_hour)
    
    tk.Label(end_frame, text=":", font=("Arial", 11)).pack(side="left", padx=2)
    
    end_minute_entry = tk.Entry(end_frame, width=3, font=("Arial", 11))
    end_minute_entry.pack(side="left", padx=2)
    end_minute_entry.insert(0, default_end_minute)
    
    tk.Label(root, text="─" * 60, foreground="gray").pack(padx=10, pady=5)
    
    # Schedule Dates Section
    tk.Label(root, text="Scheduled Dates (manual + auto-next 7 working days)", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=5)
    
    dates_text_widget = tk.Text(root, height=5, width=60, font=("Courier", 9))
    dates_text_widget.pack(padx=10, pady=5)
    dates_text_widget.insert("1.0", scheduled_dates)
    
    tk.Label(root, text="─" * 60, foreground="gray").pack(padx=10)
    
    # Exclude Weekends Section
    exclude_var = tk.BooleanVar(value=exclude_weekends)
    exclude_check = tk.Checkbutton(root, text="Exclude Weekends", variable=exclude_var, font=("Arial", 10))
    exclude_check.pack(anchor="w", padx=10, pady=5)
    
    tk.Label(root, text="─" * 60, foreground="gray").pack(padx=10)
    
    # Status Label
    status_label = tk.Label(root, text="Status: Ready", foreground="blue")
    status_label.pack(padx=10, pady=5)
    
    # Buttons
    button_frame = tk.Frame(root)
    button_frame.pack(padx=10, pady=10)
    
    tk.Button(button_frame, text="Save Schedule", command=save_schedule, bg="blue", fg="white", width=15).pack(side="left", padx=5)
    tk.Button(button_frame, text="Start Monitoring", command=start_monitoring, bg="green", fg="white", width=15).pack(side="left", padx=5)
    tk.Button(button_frame, text="Exit", command=root.quit, bg="red", fg="white", width=15).pack(side="left", padx=5)

    # System tray icon
    icon = Icon("ServerKeepAlive", create_image(), "Server Keep-Alive")
    icon.menu = Menu(MenuItem("Quit", on_quit))
    
    # Bring window to front
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    
    root.mainloop()
    
except Exception as e:
    log_error(f"Critical error: {e}")
    messagebox.showerror("Error", f"Failed to start application: {e}")
