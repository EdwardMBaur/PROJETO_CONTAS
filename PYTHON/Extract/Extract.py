import pandas
import gspread
from google.oauth2.service_account import Credentials
import numpy as np
from configs import paths

class Extract:
    @staticmethod
    def _get_worksheet(spreadsheet_id: str, sheet_ref):
        """Método auxiliar privado para conectar na planilha"""
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_file(paths.PATH_CREDENTIALS, scopes=scopes)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(spreadsheet_id)
        
        if isinstance(sheet_ref, int):
            return spreadsheet.get_worksheet(sheet_ref)
        else:
            return spreadsheet.worksheet(sheet_ref)

    @staticmethod
    def import_data(spreadsheet_id: str, sheet_ref=0) -> pandas.DataFrame:
        try:
            worksheet = Extract._get_worksheet(spreadsheet_id, sheet_ref)
            data = worksheet.get_all_records()
            
            if not data:
                return pandas.DataFrame()

            dataframe = pandas.DataFrame(data)
            dataframe = dataframe.replace(r'^\s*$', np.nan, regex=True)
            return dataframe
        except Exception as e:
            print(f"[ERROR] Import failed: {e}")
            return pandas.DataFrame()

    @staticmethod
    def add_row(spreadsheet_id: str, sheet_ref, row_data: list):
        """
        Adiciona uma linha baseada na ordem do ID com formatação correta.
        """
        try:
            worksheet = Extract._get_worksheet(spreadsheet_id, sheet_ref)

            novo_id = int(row_data[0])
            
            input_option = 'USER_ENTERED' 

            if novo_id == 1:
                worksheet.insert_row(row_data, index=2, value_input_option=input_option)
                print(f"[SUCCESS] ID 1 inserido no início da aba {sheet_ref}")
                return True

            id_anterior = novo_id - 1
            
            try:
                cell = worksheet.find(str(id_anterior), in_column=1)

                worksheet.insert_row(row_data, index=cell.row + 1, value_input_option=input_option)
                
                print(f"[SUCCESS] Linha inserida abaixo do ID {id_anterior}")
                return True
                
            except gspread.exceptions.CellNotFound:
                print(f"[WARNING] ID anterior ({id_anterior}) não encontrado. Adicionando ao final.")
                worksheet.append_row(row_data, value_input_option=input_option)
                return True

        except Exception as e:
            print(f"[ERROR] Erro ao adicionar linha: {e}")
            raise e

    @staticmethod
    def delete_row_by_id(spreadsheet_id: str, sheet_ref, id_value, id_column_index=1):
        """
        Busca um valor numa coluna específica e deleta a linha correspondente.
        id_value: O ID que queremos deletar.
        id_column_index: O número da coluna onde está o ID (1 = Coluna A, 2 = B...)
        """
        try:
            worksheet = Extract._get_worksheet(spreadsheet_id, sheet_ref)

            cell = worksheet.find(str(id_value), in_column=id_column_index)
            
            if cell:
                worksheet.delete_rows(cell.row)
                print(f"[SUCCESS] Linha {cell.row} deletada (ID: {id_value})")
                return True
            else:
                print(f"[WARNING] ID {id_value} não encontrado na planilha.")
                return False
        except gspread.exceptions.CellNotFound:
             print(f"[WARNING] ID {id_value} não encontrado.")
             return False
        except Exception as e:
            print(f"[ERROR] Erro ao deletar linha: {e}")
            raise e