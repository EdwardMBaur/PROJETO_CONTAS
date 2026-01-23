from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

PATH_TO_COD = "/opt/airflow/dags/python/Contas"
PATH_TO_DBT = "/opt/airflow/dags/DBT/PAGAMENTOS/pagamento"

with DAG(
    dag_id="dag_conta",
    start_date=datetime(2026, 1, 1),
    schedule="@monthly",
    catchup=False,
):

    run_python = BashOperator(
        task_id="rodar_controller",
        bash_command=f"cd {PATH_TO_COD} && python Controller.py",
    )

    run_dbt = BashOperator(
        task_id="rodar_dbt", 
        bash_command=f"cd {PATH_TO_DBT} && dbt run --profiles-dir ."
    )

    run_python >> run_dbt