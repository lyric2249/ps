import os
import datetime
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
# from airflow.hooks.base import BaseHook
import pandas as pd
import sqlalchemy as sa

# from sqlalchemy import create_engine, text
from sqlalchemy.types import VARCHAR, INTEGER, FLOAT, DateTime
from sqlalchemy.dialects.postgresql import TIMESTAMP, DOUBLE_PRECISION

import requests


def insert_values(**context):

    url = f"https://production.dataviz.cnn.io/index/fearandgreed/graphdata/2022-01-01"

    session = requests.Session()

    # Optional: set headers (some APIs require a User-Agent)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/117.0 Safari/537.36"
    })

    response = session.get(url)
    response.raise_for_status()
    r = response.json()

    data = r["fear_and_greed_historical"]["data"]
    df = pd.DataFrame(data)
    df["x"] = pd.to_datetime(df["x"], unit="ms")  # convert timestamp
    df = df.rename(columns={"x":"date", "y":"fear_greed_index"})

    df['weekly_fear_greed_index_max'] = (
        df.groupby(pd.Grouper(key='date', freq='W-SUN'))['fear_greed_index']
        .transform('max')
    )

    df['weekly_fear_greed_index_min'] = (
        df.groupby(pd.Grouper(key='date', freq='W-SUN'))['fear_greed_index']
        .transform('min')
    )




    # conn = BaseHook.get_connection(CONN_ID)
    # uri = conn.get_uri()  # e.g. postgresql+psycopg://app:secret@postgres-meta:5432/appdb
    uri = f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@postgres-data/superset"
    engine = sa.create_engine(uri, future=True)

    # with engine.begin() as conn:
    #     conn.execute(text('TRUNCATE TABLE public."users" RESTART IDENTITY CASCADE;'))
    #     # conn.execute(text('drop table public.fear_greed_index;'))

    # 최초 생성 시 dtype 명시 가능
    # df.head(0).to_sql("fear_greed_index", engine, schema="public", if_exists="replace", index=False, dtype={"date": TIMESTAMP(timezone=False), "fear_greed_index": DOUBLE_PRECISION(), "rating": VARCHAR(50)})
    # df.to_sql("fear_greed_index", engine, schema="public", if_exists="append", index=False, method="multi", chunksize=10_000)

    with engine.begin() as conn:
        # df.head(0).to_sql(
        #     "fear_greed_index",
        #     con=conn,
        #     schema="public",
        #     if_exists="replace",
        #     index=False,
        #     dtype={"date": TIMESTAMP(timezone=False), "fear_greed_index": DOUBLE_PRECISION(), "rating": VARCHAR(50)},
        # )
        df.to_sql(
            "fear_greed_index",
            con=conn,
            schema="public",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=10_000,
        )

    return 0


with DAG(
    dag_id="DAILY_INSERT_FearGreedIndex",
    start_date=datetime.datetime(2025, 9, 24),
    # schedule=None,
    schedule='@daily',
    catchup=False,
    default_args={"owner": "airflow"},
    tags=["postgres", "pandas"],
) as dag:
    read_task = PythonOperator(
        task_id="read_postgres",
        python_callable=insert_values,
    )
