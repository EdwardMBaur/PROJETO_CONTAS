from configs import paths
from Extract.Extract import Extract
from Transform.transform import Transform
from load.load import Load

class ImportacaoPlanilhaController:
    @staticmethod
    def run():
        print("--- Processando Aba 1 (Carro) ---")
        try:
            df_carro = Extract.import_data(paths.SHEET, sheet_ref=0)
            
            if not df_carro.empty:
                df_carro_clean = Transform.transform_dados_financeiros(df_carro)
                Load.load_carro(df_carro_clean)
            else:
                print("[AVISO] Aba Carro vazia. Nada a processar.")
        
        except Exception as e:
            print(f"[ERRO CRÍTICO] Falha no fluxo Carro: {e}")
            raise 

        print("\n--- Processando Aba 2 (Notebook) ---")
        try:
            df_notebook = Extract.import_data(paths.SHEET, sheet_ref=1)
            
            if not df_notebook.empty:
                df_notebook_clean = Transform.transform_dados_financeiros(df_notebook)
                Load.load_notebook(df_notebook_clean)
            else:
                print("[AVISO] Aba Notebook vazia. Nada a processar.")

        except Exception as e:
            print(f"[ERRO CRÍTICO] Falha no fluxo Notebook: {e}")
            raise

if __name__ == "__main__":
    ImportacaoPlanilhaController.run()