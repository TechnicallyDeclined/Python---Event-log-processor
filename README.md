# Active Directory Log Aggregator and Processor

This project consists of a PowerShell script to gather Active Directory security event logs from local and remote domain controllers, and a Python script to process this data into a more readable Excel format.

## Overview

The PowerShell script (`ad.ps1`) is responsible for:

* Gathering specific security event logs related to Active Directory changes (user and group management, computer account changes, password resets, etc.).
* Retrieving logs from both the local machine and a specified remote domain controller.
* Exporting the raw event log data to a CSV file (`adlogs.csv`).

The Python script (`main.py`) is responsible for:

* Reading the `adlogs.csv` file generated by the PowerShell script.
* Parsing the raw event log messages to extract key information such as:
    * Timestamp of the event.
    * Type of action performed.
    * User who initiated the change.
    * User or group affected by the change.
* Formatting the data into a more user-friendly structure with descriptive column names.
* Saving the processed data into an Excel file (`ad_group_membership_changes_last30days_readable.xlsx`).

## Prerequisites

Before running these scripts, ensure you have the following:

* **Windows Environment:** The PowerShell script is designed to run on a Windows machine that is part of the Active Directory domain or has the necessary remote management tools installed.
* **PowerShell:** Ensure PowerShell is installed and accessible.
* **Python 3:** Ensure Python 3 is installed on the machine where you will run the Python script.
* **Python Libraries:** The Python script depends on the following libraries. You can install them using pip:
    ```bash
    pip install pandas openpyxl
    ```
* **Administrative Privileges:** The PowerShell script needs to be run with administrative privileges to access the Security event log, especially on remote domain controllers.
* **Remote Access Permissions:** The user account running the PowerShell script must have the necessary permissions to access the Security event logs on the remote domain controller. This might involve being a Domain Admin or having specific delegated permissions.
* **Network Connectivity:** Ensure that the machine running the PowerShell script can communicate with the specified remote domain controller over the necessary ports (e.g., WinRM).

## Setup and Usage

1.  **Download the Scripts:** Obtain the PowerShell script (e.g., `ad.ps1`) and the Python script (`main.py`).

2.  **Configure the PowerShell Script:**
    * Open the PowerShell script in a text editor.
    * Locate the `$remoteDC` variable and replace `"YourRemoteDC.yourdomain.com"` with the actual Fully Qualified Domain Name (FQDN) or NetBIOS name of your other domain controller.
    * Review the `$eventIdsToMonitor` array to ensure it includes all the event IDs you are interested in.

3.  **Run the PowerShell Script:**
    * Open PowerShell as an administrator (right-click "Windows PowerShell" in the Start Menu and select "Run as administrator").
    * Navigate to the directory where you saved the PowerShell script using the `cd` command.
    * Execute the script:
        ```powershell
        .\Get-ADLogs.ps1
        ```
    * The script will gather logs from the local and remote domain controllers and save them to `file path you save csv to`. **Note:** You might need to adjust the output path if you prefer a different location.

4.  **Run the Python Script:**
    * Open a Command Prompt or PowerShell window.
    * Navigate to the directory where you saved the Python script (`main.py`).
    * Execute the script:
        ```bash
        python main.py
        ```
    * The Python script will read `adlogs.csv`, process the data, and save the readable output to `file path to where you want to save the xlsx file to`. **Note:** The output path is defined within the Python script and can be modified there.

## Running Together (Orchestration)

You can automate the execution of both scripts sequentially using PowerShell:

```powershell
# Run the PowerShell script (ensure it's run as administrator)
Start-Process powershell -ArgumentList "-NoExit -File `"C:\path\to\your\ad.ps1`"" -Verb RunAs
# Wait for a few seconds to ensure the CSV is created (adjust as needed)
Start-Sleep -Seconds 10
# Run the Python script
python "C:\path\to\your\main.py"