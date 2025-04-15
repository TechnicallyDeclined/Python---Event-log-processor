import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import pandas as pd
import re
import datetime

# --- Configuration ---
powershell_script_path = "c:/Users/hunter/OneDrive - Pro IT, LLC/Documents/WindowsPowerShell/Scripts/ad.ps1"
default_excel_output_path = "C:/proit/ad_group_membership_changes_readable.xlsx"

def run_powershell():
    status_label.config(text="Running PowerShell script...")
    try:
        result = subprocess.run(['powershell', '-File', powershell_script_path], capture_output=True, text=True, check=True)
        log_text.insert(tk.END, "PowerShell script executed successfully:\n")
        log_text.insert(tk.END, result.stdout)
        status_label.config(text="PowerShell script finished.")
        process_data_button.config(state=tk.NORMAL) # Enable the next button
    except subprocess.CalledProcessError as e:
        error_message = f"Error executing PowerShell script:\n{e}\n{e.stderr}"
        messagebox.showerror("PowerShell Error", error_message)
        log_text.insert(tk.END, error_message + "\n")
        status_label.config(text="PowerShell script failed.")
        process_data_button.config(state=tk.DISABLED)

def process_data():
    status_label.config(text="Processing data with Python...")
    csv_path = "C:/proit/ad_group_membership_changes_last30days.csv"
    excel_output_path = filedialog.asksaveasfilename(
        initialfile=default_excel_output_path,
        defaultextension=".xlsx",
        title="Save Readable Excel File"
    )
    if not excel_output_path:
        status_label.config(text="Processing cancelled.")
        return

    try:
        dataframe = pd.read_csv(csv_path)

        def extract_account_name(text, label_pattern):
            match = re.search(rf"{label_pattern}:\s+(.+)", text)
            if match:
                return match.group(1).strip()
            return None

        dataframe['User Initiating Change'] = dataframe['Message'].apply(lambda x: extract_account_name(x, r"Subject:\s*\n\tSecurity ID:.*?\n\tAccount Name"))
        dataframe['Member Affected'] = dataframe['Message'].apply(lambda x: extract_account_name(x, r"Member:\s*\n\tSecurity ID:.*?\n\tAccount Name"))
        dataframe['Member Affected'] = dataframe['Member Affected'].str.split(',').str[0].str.replace('CN=', '').str.strip()
        dataframe['Group Affected'] = dataframe['Message'].apply(lambda x: extract_account_name(x, r"Group:\s*\n\tSecurity ID:.*?\n\tGroup Name"))
        dataframe['Action'] = dataframe['Message'].apply(lambda x: x.split('\n')[0].strip())
        dataframe['Timestamp'] = pd.to_datetime(dataframe['TimeCreated']).dt.strftime('%Y-%m-%d %I:%M %p')
        readable_df = dataframe[['Timestamp', 'Action', 'User Initiating Change', 'Member Affected', 'Group Affected']]
        readable_df.to_excel(excel_output_path, index=False)
        status_label.config(text=f"Data processed and saved to: {excel_output_path}")
        log_text.insert(tk.END, f"Data processed and saved to: {excel_output_path}\n")
    except FileNotFoundError:
        messagebox.showerror("File Error", f"CSV file not found at: {csv_path}")
        status_label.config(text="Error processing data.")
        log_text.insert(tk.END, f"Error: CSV file not found at: {csv_path}\n")
    except Exception as e:
        messagebox.showerror("Python Error", f"An error occurred during Python processing:\n{e}")
        status_label.config(text="Error processing data.")
        log_text.insert(tk.END, f"An error occurred during Python processing:\n{e}\n")

# --- GUI Setup ---
window = tk.Tk()
window.title("AD Log Processor")

run_ps_button = tk.Button(window, text="Run PowerShell Script", command=run_powershell)
run_ps_button.pack(pady=10)

process_data_button = tk.Button(window, text="Process Data & Save to Excel", command=process_data, state=tk.DISABLED)
process_data_button.pack(pady=10)

status_label = tk.Label(window, text="Ready")
status_label.pack(pady=5)

log_text = tk.Text(window, height=10, width=60)
log_text.pack(pady=10)

window.mainloop()