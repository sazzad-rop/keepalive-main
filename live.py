import ctypes
import time
import threading
from datetime import datetime
import json
import os
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
def keep_teams_active(start_dt, end_dt, interval=60):
    while True:
        now = datetime.now()
        if start_dt <= now <= end_dt:
            simulate_activity()
        # stop the thread after end_dt is passed
        if now > end_dt:
            break
        time.sleep(interval)


def monitor_selected_dates(dates_list, sh, sm, eh, em, exclude_weekends=False, interval=60):
    """
    dates_list: list of datetime.date objects
    For each date in sorted order, waits until the start datetime then runs keep_teams_active
    for that date's start/end. Skips weekends if exclude_weekends is True.
    """
    dates = sorted({d for d in dates_list})
    for d in dates:
        if exclude_weekends and d.weekday() >= 5:
            continue
        start_dt = datetime(d.year, d.month, d.day, sh, sm)
        end_dt = datetime(d.year, d.month, d.day, eh, em)
        # skip invalid ranges (end <= start)
        if end_dt <= start_dt:
            continue
        now = datetime.now()
        # if this date is already past, skip
        if end_dt < now:
            continue
        # wait until start_dt
        if start_dt > now:
            wait = (start_dt - now).total_seconds()
            # sleep in chunks so the thread can be responsive if needed
            while wait > 0:
                chunk = min(wait, 60)
                time.sleep(chunk)
                wait -= chunk
        # If within running window, run keep_teams_active (this will block until end_dt)
        if datetime.now() <= end_dt:
            keep_teams_active(start_dt, end_dt, interval)


# Function to start the background thread
def start_monitoring():
    try:
        # parse selected dates (comma or newline separated)
        dates_raw = dates_text.get("1.0", tk.END).strip()
        if not dates_raw:
            messagebox.showerror("Error", "Please enter at least one date (YYYY-MM-DD).")
            return
        # normalize separators
        dates_raw_norm = dates_raw.replace(',', '\n')
        date_lines = [l.strip() for l in dates_raw_norm.splitlines() if l.strip()]
        selected_dates = []
        for ds in date_lines:
            try:
                d = datetime.fromisoformat(ds).date()
                selected_dates.append(d)
            except Exception:
                messagebox.showerror("Error", f"Invalid date format: {ds}")
                return

        start_hour = int(start_hour_entry.get())
        start_minute = int(start_minute_entry.get())
        end_hour = int(end_hour_entry.get())
        end_minute = int(end_minute_entry.get())
        
        # Validate hours and minutes
        if not (0 <= start_hour <= 23) or not (0 <= start_minute <= 59):
            messagebox.showerror("Error", "Start time: hours must be 0-23, minutes must be 0-59.")
            return
        if not (0 <= end_hour <= 23) or not (0 <= end_minute <= 59):
            messagebox.showerror("Error", "End time: hours must be 0-23, minutes must be 0-59.")
            return
        
        # Validate that end_time > start_time
        if end_hour < start_hour or (end_hour == start_hour and end_minute <= start_minute):
            messagebox.showerror("Error", "End time must be after start time.")
            return
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers for hours and minutes.")
        return

    # optionally save schedule (store dates as lines)
    if save_var.get():
        try:
            save_schedule('\n'.join(date_lines), start_hour, start_minute, end_hour, end_minute, exclude_weekends_var.get())
        except Exception:
            pass

    # start a scheduler thread that will process each selected date
    t = threading.Thread(target=monitor_selected_dates, args=(selected_dates, start_hour, start_minute, end_hour, end_minute, exclude_weekends_var.get()), daemon=True)
    t.start()
    messagebox.showinfo("Started", "Teams Keep-Active running in background.")
    hide_window()


def get_schedule_path():
    base = os.path.dirname(__file__)
    return os.path.join(base, 'schedule.json')


def save_schedule(dates_raw, sh, sm, eh, em, exclude_weekends=False):
    """Save the selected dates block and time parameters to schedule.json.

    dates_raw: newline-separated string of dates (YYYY-MM-DD)
    sh, sm: start hour/minute
    eh, em: end hour/minute
    exclude_weekends: bool
    """
    path = get_schedule_path()
    data = {
        'dates': dates_raw,
        'start_hour': sh,
        'start_minute': sm,
        'end_hour': eh,
        'end_minute': em,
        'exclude_weekends': bool(exclude_weekends)
    }
    with open(path, 'w') as f:
        json.dump(data, f)


def load_schedule():
    path = get_schedule_path()
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception:
        return None

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

# Time inputs
tk.Label(root, text="Start Time (HH:MM)").grid(row=0, column=0, padx=10, pady=5)
start_hour_entry = tk.Entry(root, width=3)
start_hour_entry.grid(row=0, column=1, sticky='W')
start_hour_entry.insert(0, "07")
start_minute_entry = tk.Entry(root, width=3)
start_minute_entry.grid(row=0, column=2, sticky='W')
start_minute_entry.insert(0, "00")

tk.Label(root, text="End Time (HH:MM)").grid(row=1, column=0, padx=10, pady=5)
end_hour_entry = tk.Entry(root, width=3)
end_hour_entry.grid(row=1, column=1, sticky='W')
end_hour_entry.insert(0, "17")
end_minute_entry = tk.Entry(root, width=3)
end_minute_entry.grid(row=1, column=2, sticky='W')
end_minute_entry.insert(0, "00")

# Save/Load controls
save_var = tk.BooleanVar()
save_check = tk.Checkbutton(root, text="Save schedule", variable=save_var)
save_check.grid(row=2, column=0, columnspan=2, pady=6)

# Selected dates input (multiple specific dates)
tk.Label(root, text="Selected Dates (YYYY-MM-DD) - comma or newline separated").grid(row=4, column=0, padx=10, pady=5)
dates_text = tk.Text(root, width=25, height=4)
dates_text.grid(row=4, column=1, columnspan=2)
dates_text.insert('1.0', '2026-03-20\n2026-03-21\n2026-03-22')

exclude_weekends_var = tk.BooleanVar()
exclude_check = tk.Checkbutton(root, text="Exclude weekends", variable=exclude_weekends_var)
exclude_check.grid(row=5, column=0, columnspan=2, pady=4)

def populate_schedule(data):
    if not data:
        return
    # load time fields
    start_hour_entry.delete(0, tk.END)
    start_hour_entry.insert(0, str(data.get('start_hour', '07')))
    start_minute_entry.delete(0, tk.END)
    start_minute_entry.insert(0, str(data.get('start_minute', '00')))

    end_hour_entry.delete(0, tk.END)
    end_hour_entry.insert(0, str(data.get('end_hour', '17')))
    end_minute_entry.delete(0, tk.END)
    end_minute_entry.insert(0, str(data.get('end_minute', '00')))

    # load multi-date field and weekend exclusion
    dates_text.delete('1.0', tk.END)
    if 'dates' in data:
        if isinstance(data.get('dates'), list):
            dates_text.insert('1.0', '\n'.join(data.get('dates')))
        else:
            dates_text.insert('1.0', str(data.get('dates')))
    exclude_weekends_var.set(bool(data.get('exclude_weekends', False)))

def on_load_saved():
    data = load_schedule()
    if not data:
        messagebox.showinfo("No schedule", "No saved schedule found.")
        return
    populate_schedule(data)

tk.Button(root, text="Load Saved", command=on_load_saved).grid(row=2, column=2, pady=6)

tk.Button(root, text="Start", command=start_monitoring).grid(row=6, column=0, columnspan=3, pady=10)

# Load any saved schedule
saved = load_schedule()
if saved:
    populate_schedule(saved)

root.mainloop()
