import gspread
import pandas as pd
import os
from dotenv import load_dotenv

"""
Runs ETL pipeline to load survey responses and annotated data from Google Sheet.

Setup:
1. Go to Google Cloud Console.
2. Create a new project (or select an existing one) and enable the Google Sheets API and Google Drive API.
3. Navigate to IAM & Admin > Service Accounts, create a service account.
4. Generate a new JSON key. Download this file and save it in the ./etl folder with the name service_account.json. 
5. Open the Google Sheet, click "Share," and share it with the email address of the service account you just created (it looks like name@project.iam.gserviceaccount.com).
6. Add GSHEETS_ID = "<YOUR_GOOGLE_SHEET_ID" to .env. (The ID is in your Google Sheet URL: https://docs.google.com/spreadsheets/d/<THIS_IS_THE_ID>/edit)
"""

def run_etl():
    print("Starting ETL...")
    
    # Authentication
    gc = gspread.service_account(filename='etl/service_account.json')
    
    load_dotenv()
    spreadsheet_id = os.getenv('GSHEETS_ID', '')
    sh = gc.open_by_key(spreadsheet_id)

    # Ensure target directory exists
    os.makedirs('data', exist_ok=True)

    print("Processing Form Responses...")
    form_responses_sheet = sh.worksheet('Form Responses')
    form_responses_data = form_responses_sheet.get_all_records()
    form_responses_df = pd.DataFrame(form_responses_data)
    form_responses_df = transform_form_responses(form_responses_df)
    form_responses_csv_path = 'data/form_responses.csv'
    form_responses_df.to_csv(form_responses_csv_path, index=False)
    print(f"Successfully loaded into {form_responses_csv_path}")

    print("Processing Label Master...")
    label_master_sheet = sh.worksheet('Label_Master')
    label_master_data = label_master_sheet.get_all_records()
    label_master_df = pd.DataFrame(label_master_data)
    label_master_csv_path = 'data/label_master.csv'
    label_master_df.to_csv(label_master_csv_path, index=False)
    print(f"Successfully loaded into {label_master_csv_path}")

    labeller_sheets = {
        'Wai Yan': 'label_1',
        'Hu Can': 'label_2',
        'Tran': 'label_3',
        'Pink Ray': 'label_4',
        'Zheng Min': 'label_5',
        'Ming Hui': 'label_6'
    }
    for labeller, table in labeller_sheets.items():
        print(f"Processing Labeller {labeller}...")
        lebeller_sheet = sh.worksheet(labeller)
        labeller_data = lebeller_sheet.get_all_records()
        labeller_df = pd.DataFrame(labeller_data)
        labeller_df = transform_labeller(labeller_df)
        labeller_csv_path = f'data/{table}.csv'
        labeller_df.to_csv(labeller_csv_path, index=False)
        print(f"Successfully loaded into {labeller_csv_path}")

    print("ETL complete!")

def transform_form_responses(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = pd.read_csv('data/survey_qns_data_dict.csv')['Code']
    return df

def transform_labeller(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={
        'Relevant?': 'is_relevant',
        'D1 (Personal Ability)': 'feas_pa',
        'D2 (Knowledge Application)': 'feas_ka',
        'D3 (Career Replaceability)': 'feas_cr',
        'D4 (Social Relations)': 'feas_sr'
    })
    df = df[['entry_id', 'is_relevant', 'feas_pa', 'feas_ka', 'feas_cr', 'feas_sr']]
    return df

if __name__ == "__main__":
    run_etl()