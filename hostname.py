import socket
import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess

# Create a root window (it will be hidden)
root = tk.Tk()
root.withdraw()

# Ask for IP address via popup
ip = simpledialog.askstring("Input", "Enter an IP address:")

if ip:
    # Get hostname
    hostname = "Hostname not found"
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except socket.herror:
        pass
    
    # Ping the IP
    ping_result = subprocess.run(["ping", "-n", "4", ip], capture_output=True, text=True).stdout
    
    # Parse ping result
    lines = ping_result.split('\n')
    sent = received = lost = loss_percent = min_t = max_t = avg_t = "N/A"
    for i, line in enumerate(lines):
        if 'Packets:' in line:
            try:
                parts = line.replace('Packets:', '').strip().split(',')
                sent = parts[0].split('=')[1].strip()
                received = parts[1].split('=')[1].strip()
                lost = parts[2].split('=')[1].strip()
                loss_percent = parts[2].split('(')[1].split('%')[0].strip() if '(' in parts[2] else "0"
            except:
                pass
        if 'Minimum' in line:
            try:
                times_line = lines[i+1]
                min_t = times_line.split(',')[0].split('=')[1].strip()
                max_t = times_line.split(',')[1].split('=')[1].strip()
                avg_t = times_line.split(',')[2].split('=')[1].strip()
            except:
                pass
    
    pingable = int(received) > 0 if received.isdigit() else False
    analysis = f"Packets sent: {sent}, Received: {received}, Lost: {lost} ({loss_percent}% loss)\nRound trip times: Min {min_t}, Max {max_t}, Avg {avg_t}"
    
    # Custom dialog
    dialog = tk.Toplevel(root)
    dialog.title("Ping and Hostname Results")
    dialog.geometry("500x350")
    tk.Label(dialog, text=f"Hostname: {hostname}").pack(pady=5)
    status_text = "The IP is pingable." if pingable else "The IP is not pingable."
    status_color = 'green' if pingable else 'red'
    tk.Label(dialog, text=status_text, fg=status_color, font=('Arial', 12, 'bold')).pack(pady=5)
    tk.Label(dialog, text="Network Analysis:").pack(pady=5)
    tk.Label(dialog, text=analysis).pack(pady=5)
    tk.Button(dialog, text="OK", command=dialog.destroy).pack(pady=10)
    dialog.mainloop()
else:
    messagebox.showinfo("Info", "No IP address entered.")

