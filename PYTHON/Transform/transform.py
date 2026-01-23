import pandas as pd
import datetime
from datetime import datetime as dt

class Transform:
    @staticmethod
    def _clean_currency(val):
        """Remove 'R$', pontos de milhar e troca vírgula decimal por ponto."""
        if pd.isna(val) or val == "":
            return None
        if isinstance(val, (int, float)):
            return float(val)

        clean_str = str(val).replace("R$", "").replace(" ", "").replace(".", "")
        clean_str = clean_str.replace(",", ".")
        
        try:
            return float(clean_str)
        except ValueError:
            return None

    @staticmethod
    def _clean_date(val):
        """Tenta converter strings de data parciais (ex: 01/12) para formato date."""
        if pd.isna(val) or val == "":
            return None
        
        str_val = str(val).strip()
        
        try:
            return pd.to_datetime(str_val).date()
        except:
            pass

        try:
            return dt.strptime(str_val, "%d/%m").replace(year=dt.now().year).date()
        except ValueError:
            pass
            
        return None

    @staticmethod
    def transform_dados_financeiros(dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica limpezas e remove linhas de rodapé (Totais) que não são dados válidos.
        """
        print("[TRANSFORM] Iniciando limpeza de dados...")
        df_transformed = dataframe.copy()

        if "Mes" in df_transformed.columns:
            df_transformed["Mes"] = pd.to_numeric(df_transformed["Mes"], errors='coerce')
            
            num_linhas_antes = len(df_transformed)
            df_transformed = df_transformed.dropna(subset=["Mes"])
            num_linhas_depois = len(df_transformed)
            
            if num_linhas_antes != num_linhas_depois:
                print(f"[TRANSFORM] Removidas {num_linhas_antes - num_linhas_depois} linhas de rodapé/totais.")

            df_transformed["Mes"] = df_transformed["Mes"].astype(int)

        cols_moeda = ["Valor (Pago)", "Total que Falta Pagar"]
        for col in cols_moeda:
            if col in df_transformed.columns:
                df_transformed[col] = df_transformed[col].apply(Transform._clean_currency)

        if "Mês" in df_transformed.columns:
            df_transformed["Mês"] = df_transformed["Mês"].apply(Transform._clean_date)

        print("[TRANSFORM] Dados limpos com sucesso.")
        return df_transformed