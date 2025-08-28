import gspread
import os
from dotenv import dotenv_values
import json

class GoogleSheet:
    def __init__(self):
        env_value = dotenv_values(".env")  # Load environment variables from .env file
        self.sheet_id = env_value.get('GOOGLE_SHEET_ID')  # Replace with your default sheet ID if not set
        self.credentials_str = env_value.get('GOOGLE_SHEETS_CREDENTIALS_JSON')
        self.credentials_json = json.loads(self.credentials_str)  # Parse JSON string to dictionary
        # Define the scope for Google Sheets API
        scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Authenticate using the service account credentials
        self.gc = gspread.service_account_from_dict(self.credentials_json)
        self.sheet = self.gc.open_by_key(self.sheet_id)
    
    def add_sheet(self, sheet_name, user_name):
        try:
            # Chreate a new worksheet with the specified name
            worksheet = self.sheet.add_worksheet(title = sheet_name, rows=8, cols=8)
            worksheet.update_acell('A1', f'{user_name}')  
            worksheet.update('A2:A8', [[x] for x in ["月", "火", "水", "木", "金", "土", "日"]])
            worksheet.update('B1:H1', [["1", "2", "3", "4", "5", "6", "7"]])
            return "Spreadsheet created successfully"
        except Exception as e:
            return f"Error creating spreadsheet: {str(e)}"
        
    def edit_value(self, sheet_name, row, col, value):
        try:
            # Open the specified sheet
            worksheet = self.sheet.worksheet(sheet_name)
            # Update the specified cell with the new value
            worksheet.update_cell(row, col, value)
            return "Value updated successfully"
        except Exception as e:
            return f"Error updating value: {str(e)}"
        
    def get_value(self, sheet_name, row, col):
        try:
            # Open the specified sheet
            worksheet = self.sheet.worksheet(sheet_name)
            # Get the value of the specified cell
            value = worksheet.cell(row, col).value
            return value
        except Exception as e:
            return f"Error retrieving value: {str(e)}"
        
    def get_row_values(self, sheet_name, row):
        try:
            # Open the specified sheet
            worksheet = self.sheet.worksheet(sheet_name)
            # Get all values in the specified row
            values = worksheet.row_values(row)
            return values
        except Exception as e:
            return f"Error retrieving row values: {str(e)}"
        
    def delete_sheet(self, sheet_name):
        try:
            # Open the specified sheet
            worksheet = self.sheet.worksheet(sheet_name)
            # Delete the specified sheet
            self.sheet.del_worksheet(worksheet)
            return "Sheet deleted successfully"
        except Exception as e:
            return f"Error deleting sheet: {str(e)}"
        
    def get_sheet_names(self):
        try:
            # Get all sheet names in the spreadsheet
            return self.sheet.worksheets()
        except Exception as e:
            return f"Error retrieving sheet names: {str(e)}"