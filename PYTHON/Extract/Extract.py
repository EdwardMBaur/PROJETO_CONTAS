import pandas
import gspread
from google.oauth2.service_account import Credentials
import numpy as np
from configs import paths

class Extract:
    @staticmethod
    def import_data(spreadsheet_id: str, sheet_ref=0) -> pandas.DataFrame:
        """
        Importa dados de uma aba específica do Google Sheets.
        
        :param spreadsheet_id: ID da Planilha Geral.
        :param sheet_ref: O nome da aba (str) OU o índice da aba (int). Padrão: 0 (primeira aba).
        :return: DataFrame com os dados.
        """
        print(f"[DEBUG] (import_data) Starting import for sheet ref: {sheet_ref}")
        
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        try:
            creds = Credentials.from_service_account_file(paths.PATH_CREDENTIALS, scopes=scopes)
            client = gspread.authorize(creds)

            spreadsheet = client.open_by_key(spreadsheet_id) 

            if isinstance(sheet_ref, int):
                worksheet = spreadsheet.get_worksheet(sheet_ref)
            else:
                worksheet = spreadsheet.worksheet(sheet_ref)

            print(f"[DEBUG] (import_data) Worksheet '{sheet_ref}' selected. Fetching records...")
            
            data = worksheet.get_all_records()

            if not data:
                print("[DEBUG] (import_data) Sheet is empty.")
                return pandas.DataFrame() 

            dataframe = pandas.DataFrame(data)

            dataframe = dataframe.replace(r'^\s*$', np.nan, regex=True)

            print(f"[DEBUG] (import_data) Data extracted successfully from {sheet_ref}.")
            return dataframe

        except Exception as e:
            print(f"[ERROR] (import_data) Failed to import sheet {sheet_ref}: {e}")
            raise ValueError(f"Error importing sheet {sheet_ref}: {e}")