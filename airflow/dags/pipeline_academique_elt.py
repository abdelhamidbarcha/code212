from __future__ import annotations
from datetime import datetime, timedelta
import sys
import os

from airflow.decorators import dag, task

sys.path.append("/opt/airflow/src")

default_args = {
    "owner": "data-team",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

@dag(
    dag_id="pipeline_academique_elt",
    description="Pipeline ELT complet : extract -> load -> dbt run -> dbt test",
    default_args=default_args,
    schedule_interval="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["academique", "elt", "dbt"],
)
def pipeline_academique():

    @task
    def extract_task():
        from extract import main as extract_main
        extract_main()

    @task
    def load_task():
        from load import main as load_main
        load_main()

    @task
    def dbt_run_task():
        import subprocess
        import logging
        import os
        
        log = logging.getLogger("airflow.task")
        
        
        dbt_env = os.environ.copy()
        dbt_env["DBT_LOG_PATH"] = "/opt/airflow/dbt_target/logs"
        dbt_env["DBT_TARGET_PATH"] = "/opt/airflow/dbt_target/target"
        
        result = subprocess.run(
            ["dbt", "run", "--project-dir", "/opt/airflow/dbt_project", "--profiles-dir", "/opt/airflow/dbt_project"],
            env=dbt_env,
            capture_output=True, text=True,
        )
        
        log.info("---- DBT STDOUT ----\n%s", result.stdout)
        if result.stderr:
            log.error("---- DBT STDERR ----\n%s", result.stderr)
            
        if result.returncode != 0:
            raise RuntimeError(f"dbt run a échoué (code {result.returncode}). Chouf les logs l-foq bash t-3ref l-mochkil.")

    @task
    def dbt_test_task():
        import subprocess
        import logging
        import os
        
        log = logging.getLogger("airflow.task")
        
        
        dbt_env = os.environ.copy()
        dbt_env["DBT_LOG_PATH"] = "/opt/airflow/dbt_target/logs"
        dbt_env["DBT_TARGET_PATH"] = "/opt/airflow/dbt_target/target"
        
        result = subprocess.run(
            ["dbt", "test", "--project-dir", "/opt/airflow/dbt_project", "--profiles-dir", "/opt/airflow/dbt_project"],
            env=dbt_env,
            capture_output=True, text=True,
        )
        
        log.info("---- DBT STDOUT ----\n%s", result.stdout)
        if result.stderr:
            log.error("---- DBT STDERR ----\n%s", result.stderr)
            
        if result.returncode != 0:
            raise RuntimeError(f"dbt test a échoué (code {result.returncode}). Chouf les logs l-foq bash t-3ref l-mochkil.")

    e = extract_task()
    l = load_task()
    r = dbt_run_task()
    t = dbt_test_task()

    e >> l >> r >> t

pipeline_academique()