import tkinter as tk
import requests
import subprocess

# URL for the decoded keys
url = "https://raw.githubusercontent.com/MuOssama/pr/main/marlin"

def decode_license(license_key):
    odd_chars = license_key[1::2]  # Even indexed characters
    even_chars = license_key[0::2]  # Odd indexed characters
    return odd_chars + even_chars

def check_license():
    entered_license = entry.get()
    decoded_license = decode_license(entered_license)
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        decoded_keys = response.text.splitlines()
        
        if decoded_license in decoded_keys:
            result_label.config(text="License is valid!", fg="green")
            run_beta()  # Launch beta.exe
            app.quit()  # Exit the application
        else:
            result_label.config(text="License is invalid.", fg="red")
    except requests.RequestException as e:
        result_label.config(text="Error fetching license data.", fg="red")

def run_beta():
    try:
        # Start the external program without waiting for it to finish
        subprocess.Popen(['beta.exe'])
    except Exception as e:
        result_label.config(text=f"Error running beta.exe: {e}", fg="red")

# Create the main application window
app = tk.Tk()
app.title("License Checker")

# Create and place the input field and button
entry_label = tk.Label(app, text="Enter License Key:")
entry_label.pack(pady=5)

entry = tk.Entry(app)
entry.pack(pady=5)

check_button = tk.Button(app, text="Check License", command=check_license)
check_button.pack(pady=10)

result_label = tk.Label(app, text="")
result_label.pack(pady=10)

# Start the Tkinter event loop
app.mainloop()
