{{ config(materialized='table') }}

SELECT DISTINCT MES AS ID_CARRO, "Mês", "Valor (Pago)" AS PAGAMENTO FROM PUBLIC.STG_NOTEBOOK
  WHERE 
  "Mês" IS NOT NULL AND 
  "Valor (Pago)" IS NOT NULL
  ORDER BY ID_CARRO
