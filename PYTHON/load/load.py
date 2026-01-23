import pandas as pd
import psycopg2 as pg
from psycopg2.extras import execute_values
from configs.settings import get_db_config

class Load:
    
    @staticmethod
    def _get_connection():
        config = get_db_config()
        return pg.connect(**config)

    @staticmethod
    def _prepare_dataframe(dataframe: pd.DataFrame, columns_order: list):
        """
        Método auxiliar para garantir a ordem das colunas e tratar NULLs.
        """
        df_sorted = dataframe[columns_order]
        return df_sorted.where(pd.notnull(df_sorted), None)

    @staticmethod
    def load_carro(dataframe: pd.DataFrame):
        print("[LOAD] Iniciando carga STG_CARRO...")
        conn = None
        try:
            cols_order = ["Mes", "Valor (Pago)", "Mês", "Total que Falta Pagar"]
            df_ready = Load._prepare_dataframe(dataframe, cols_order)
            
            data_to_insert = [tuple(x) for x in df_ready.to_numpy()]

            conn = Load._get_connection()
            cursor = conn.cursor()

            print("[LOAD] Limpando tabela STG_CARRO...")
            cursor.execute("TRUNCATE TABLE PUBLIC.STG_CARRO;")

            sql_insert = """
                INSERT INTO PUBLIC.STG_CARRO (
                    Mes, "Valor (Pago)", "Mês", "Total que Falta Pagar"
                ) VALUES %s
            """

            execute_values(cursor, sql_insert, data_to_insert)
            conn.commit()
            print(f"[LOAD] SUCESSO! Tabela limpa e {len(data_to_insert)} novos registros inseridos em STG_CARRO.")

        except Exception as e:
            if conn: conn.rollback()
            print(f"[ERROR] Falha ao carregar STG_CARRO: {e}")
            raise
        finally:
            if conn:
                cursor.close()
                conn.close()

    @staticmethod
    def load_notebook(dataframe: pd.DataFrame):
        print("[LOAD] Iniciando carga STG_NOTEBOOK...")
        conn = None
        try:
            cols_order = ["Mes", "Valor (Pago)", "Mês", "Total que Falta Pagar"]
            df_ready = Load._prepare_dataframe(dataframe, cols_order)
            
            data_to_insert = [tuple(x) for x in df_ready.to_numpy()]

            conn = Load._get_connection()
            cursor = conn.cursor()

            print("[LOAD] Limpando tabela STG_NOTEBOOK...")
            cursor.execute("TRUNCATE TABLE PUBLIC.STG_NOTEBOOK;")

            sql_insert = """
                INSERT INTO PUBLIC.STG_NOTEBOOK (
                    Mes, "Valor (Pago)", "Mês", "Total que Falta Pagar"
                ) VALUES %s
            """

            execute_values(cursor, sql_insert, data_to_insert)
            conn.commit()
            print(f"[LOAD] SUCESSO! Tabela limpa e {len(data_to_insert)} novos registros inseridos em STG_NOTEBOOK.")

        except Exception as e:
            if conn: conn.rollback()
            print(f"[ERROR] Falha ao carregar STG_NOTEBOOK: {e}")
            raise
        finally:
            if conn:
                cursor.close()
                conn.close()