import pandas as pd
import re

pd.set_option('display.max_colwidth', None)  # Display full column width
pd.set_option('display.max_rows', None)     # If you also have many rows
pd.set_option('display.max_columns', None)  # If you also have many columns

csv_path = "C:/proit/ad_group_membership_changes_last30days.csv"

def csv_to_dataframe(csv_path):
    try:
        df = pd.read_csv(csv_path)
        return df
    except FileNotFoundError:
        print(f"file not found: {csv_path}")
        return None
    except Exception as e:
        print(f"an occurred error: {e}")
        return None

dataframe = csv_to_dataframe(csv_path)

# Function to extract account name using regex
def extract_account_name(text, label_pattern):
    match = re.search(rf"{label_pattern}:\s+(.+)", text)
    if match:
        return match.group(1).strip()
    return None

if dataframe is not None:
    print("Data successfully loaded.")

    # Extract Subject Account Name
    dataframe['User Initiating Change'] = dataframe['Message'].apply(lambda x: extract_account_name(x, r"Subject:\s*\n\tSecurity ID:.*?\n\tAccount Name"))

    # Extract Member Account Name (Simplifying the name)
    dataframe['Member Affected'] = dataframe['Message'].apply(lambda x: extract_account_name(x, r"Member:\s*\n\tSecurity ID:.*?\n\tAccount Name"))
    dataframe['Member Affected'] = dataframe['Member Affected'].str.split(',').str[0].str.replace('CN=', '').str.strip() # Simplify

    # Extract Group Name
    dataframe['Group Affected'] = dataframe['Message'].apply(lambda x: extract_account_name(x, r"Group:\s*\n\tSecurity ID:.*?\n\tGroup Name"))

    # Extract Action (First line of the message)
    dataframe['Action'] = dataframe['Message'].apply(lambda x: x.split('\n')[0].strip())

    # Format Timestamp
    dataframe['Timestamp'] = pd.to_datetime(dataframe['TimeCreated']).dt.strftime('%Y-%m-%d %I:%M %p') # Example format

    # Select and order the desired columns
    readable_df = dataframe[['Timestamp', 'Action', 'User Initiating Change', 'Member Affected', 'Group Affected']]

    readable_df.to_excel("C:/proit/ad_group_membership_changes_last30days_readable.xlsx", index=False)
    print("Data successfully processed and saved to Excel.")


else:
    print("Failed to load data.")

