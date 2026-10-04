FROM apache/airflow:2.9.1-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /opt/airflow/dbt_target && chown -R airflow:root /opt/airflow/dbt_target

USER airflow

RUN pip install --no-cache-dir pandas Faker sqlalchemy psycopg2-binary dbt-core==1.8.0 dbt-postgres==1.8.0