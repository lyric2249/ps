import os
import pandas as pd

import yfinance as yf
import time
import datetime
import requests


from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import or_

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
import requests

from sqlalchemy import Table, MetaData, inspect, or_
from sqlalchemy.dialects.postgresql import insert


import numpy as np
from pymongo import MongoClient, UpdateOne




# ==================================================================================================================================
# upsert
# ==================================================================================================================================


def upsert_method(table, conn, keys, data_iter):

    # 0) pandas SQLTable → 이름/스키마만 가져오고, 나머지는 무시
    sqltable = getattr(table, "table", table)
    t_schema = sqltable.schema            # 예: "public" (None이면 search_path 사용)
    t_name   = sqltable.name

    # 1) DB에서 '진짜' Table을 리플렉션 (PK/UNIQUE/컬럼 정의 포함)
    md = MetaData()
    real_table = Table(t_name, md, schema=t_schema, autoload_with=conn)

    # 2) 실제 테이블 컬럼만 사용
    table_cols = set(real_table.c.keys())
    keys = [k for k in keys if k in table_cols]
    rows = [{k: v for k, v in zip(keys, row) if k in table_cols} for row in data_iter]

    # 1) PK 우선
    pk_cols = [c.name for c in real_table.primary_key.columns]
    # print(sa_table.primary_key.keys())
    # print(full_name)
    # print(table_cols)
    # print(pk_cols)

    if not pk_cols:
        raise ValueError(f"PK/UNIQUE 제약을 찾지 못했습니다. 테이블에 PRIMARY KEY 또는 UNIQUE를 정의해 주세요.")


    stmt = insert(real_table).values(rows)

    # PK는 갱신 대상에서 제외
    update_cols = {k: stmt.excluded[k] for k in keys if k not in pk_cols}

    # (선택) 값이 실제로 바뀌는 경우에만 UPDATE (쓰기 최소화)
    where_cond = or_(*[
        stmt.excluded[k].is_distinct_from(real_table.c[k])
        for k in update_cols.keys()
    ]) if update_cols else None

    stmt = stmt.on_conflict_do_update(
        index_elements=pk_cols,
        set_=update_cols,
        where=where_cond
    )

    conn.execute(stmt)




def insert_values(**context):

    # ==================================================================================================================================
    # fetch
    # ==================================================================================================================================

    url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
    df = pd.read_csv(url, sep="|")
    df = df[df['Test Issue'] == 'N']
    df = df[df['Financial Status'] == 'N']
    df = df[df['ETF'] == 'N']
    df = df[df['NextShares'] == 'N']
    nasdaq_tickers = df['Symbol'][~pd.isna(df['Symbol'])].tolist()
    nasdaq_tickers = [t for t in nasdaq_tickers if 'File Creation Time' not in t]

    u = "https://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt"
    df = pd.read_csv(u, sep="|")
    df = df[df["ACT Symbol"]!="File Creation Time"]
    nyse = df.query("Exchange=='N' and ETF=='N' and `Test Issue`=='N'")
    pat = r"(preferred|depositary|warrant|right|unit|fund|trust|note|bond|etn|when issued|when distributed|spac)"
    nyse_commonish = nyse[~nyse["Security Name"].str.contains(pat, case=False, na=False)]
    nyse_commonish.loc[:, "ACT Symbol"] = nyse_commonish["ACT Symbol"].str.replace(
        r'(\.[A-Za-z0-9]+|\$[A-Za-z0-9]+)$', '', regex=True
    )
    nyse_tickers = sorted(nyse_commonish["ACT Symbol"].unique())


    # ==================================================================================================================================
    # postgres
    # ==================================================================================================================================






    # for each in putss:
    #     if not (each.empty):

    #         each['registdate'] = registdate
    #         each = each.reset_index()
    #         each = each.rename(columns={'Date Reported':'DateReported'}).rename(columns=str.lower)

    #         each.to_sql("putss", engine, schema="public", if_exists="append", index=False, method=upsert_method, chunksize=10_000,)




    # ==================================================================================================================================
    # fetch
    # ==================================================================================================================================




    starttime = datetime.datetime.now()



    from sqlalchemy import create_engine, Table, MetaData
    from sqlalchemy.dialects.postgresql import insert
    import os

    client_mongo = MongoClient(f"mongodb://{os.getenv('MONGO_DB_USERNAME')}:{os.getenv('MONGO_DB_PASSWORD')}@mongo:27017/?authSource=admin")
    # engine_psql = create_engine(f"postgresql+psycopg2://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@localhost:5434/stock")  # postgresql+psycopg2://...
    engine_psql = create_engine(f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@postgres-data/stock")  # postgresql+psycopg2://...


    # for each_ticker in nasdaq_tickers:

    registdate = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    for idx, each_ticker in enumerate([*nasdaq_tickers, *nyse_tickers]):  # Limiting to first 100 for demo purposes
        try:
            time.sleep(0.5)  # To avoid hitting the API too hard

            yf_ticker = yf.Ticker(each_ticker)


            if True:
                # Mongo 연결

                ticker_info = yf_ticker.info
                ticker_info['registdate'] = registdate

                coll = client_mongo["stocks"]["tickers_info"]

                ops = []
                # for d in recs:
                filt = {"symbol": ticker_info["symbol"], "registdate": ticker_info["registdate"]}  # 자연키
                ops.append(UpdateOne(filt, {"$set": ticker_info}, upsert=True))
                coll.bulk_write(ops, ordered=False)


            if True:
                # postgres 연결

                institution_rate = yf_ticker.major_holders
                institution_rate = institution_rate.transpose()
                institution_rate['symbol'] = each_ticker;            institution_rate['registdate'] = registdate
                institution_rate = institution_rate.reset_index()
                institution_rate = institution_rate.rename(columns=str.lower)
                institution_rate.to_sql("institution_rates", engine_psql, schema="public", if_exists="append", index=False, method=upsert_method, chunksize=10_000,)


                ticker_holder = yf_ticker.institutional_holders
                ticker_holder['symbol'] = each_ticker;             ticker_holder['registdate'] = registdate
                ticker_holder = ticker_holder.reset_index()
                ticker_holder = ticker_holder.rename(columns={'Date Reported':'DateReported'}).rename(columns=str.lower)
                ticker_holder.to_sql("ticker_holders", engine_psql, schema="public", if_exists="append", index=False, method=upsert_method, chunksize=10_000,)


                
                if yf_ticker.options:
                    RecentExpireDate = yf_ticker.options[0]

                    calls = yf_ticker.option_chain(RecentExpireDate).calls
                    calls['symbol'] = each_ticker;                calls['registdate'] = registdate;                calls['RecentExpireDate'] = RecentExpireDate
                    calls = calls.reset_index()
                    calls = calls.rename(columns=str.lower)
                    calls.to_sql("callss", engine_psql, schema="public", if_exists="append", index=False, method=upsert_method, chunksize=10_000,)


                    puts = yf_ticker.option_chain(RecentExpireDate).puts
                    puts['symbol'] = each_ticker;                puts['registdate'] = registdate;                puts['RecentExpireDate'] = RecentExpireDate
                    puts = puts.reset_index()
                    puts = puts.rename(columns=str.lower)
                    puts.to_sql("putss", engine_psql, schema="public", if_exists="append", index=False, method=upsert_method, chunksize=10_000,)




        except Exception as e:
            error = e
            endtime =  datetime.datetime.now()
            print(f"Error processing {each_ticker}: {e}")
            print(endtime - starttime)



    # ==================================================================================================================================
    # mongo
    # ==================================================================================================================================

    return 0




with DAG(
    dag_id="DAILY_INSERT_tickers_info",
    start_date=datetime.datetime(2025, 9, 24),
    # schedule=None,
    schedule='@daily',
    catchup=False,
    default_args={"owner": "airflow"},
    tags=["postgres", "pandas"],
) as dag:
    read_task = PythonOperator(
        task_id="insert_tickers",
        python_callable=insert_values,
    )
