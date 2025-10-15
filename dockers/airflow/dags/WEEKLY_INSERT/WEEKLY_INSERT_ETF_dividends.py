import os
import datetime
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
# from airflow.hooks.base import BaseHook
import pandas as pd
import sqlalchemy as sa

import pandas as pd
import yfinance as yf
import time



# from sqlalchemy import create_engine, text
# from sqlalchemy.types import VARCHAR, INTEGER, FLOAT, DateTime, TimeStamptz
import requests


def insert_values(**context):


    '''
    ETF 배당금 정보 주기적 업데이트
    '''


    url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
    df = pd.read_csv(url, sep="|")
    # df = df.query("`Financial Status`=='N' and ETF=='N' and NextShares=='N' and `Test Issue`=='N'")
    df = df[~df["Symbol"].str.contains('File Creation Time', case=False, na=False)]
    df = df[df['ETF'] == 'Y']
    nasdaq_tickers = df['Symbol'][~pd.isna(df['Symbol'])].tolist()

    u = "https://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt"
    df = pd.read_csv(u, sep="|")
    df = df[df["ACT Symbol"]!="File Creation Time"]
    # nyse = df.query("Exchange=='N' and ETF=='N' and `Test Issue`=='N'")
    df = df.query("ETF=='Y'")
    # pat = r"(preferred|depositary|warrant|right|unit|fund|trust|note|bond|etn|when issued|when distributed|spac)"; nyse_commonish = nyse[~nyse["Security Name"].str.contains(pat, case=False, na=False)]
    # nyse_commonish.loc[:, "ACT Symbol"] = nyse_commonish["ACT Symbol"].str.replace(r'(\.[A-Za-z0-9]+|\$[A-Za-z0-9]+)$', '', regex=True)
    nyse_tickers = sorted(df["ACT Symbol"].unique())


    '''
    ETF 배당금 정보 수집
    '''

    # temp = list(set([*nyse_tickers, *nasdaq_tickers]) - set(df_dividends['symbol']))
    temp = [*nyse_tickers, *nasdaq_tickers]
    temp = ['ULTY', 'NVDY']
    ls_series = []

    while temp:

        time.sleep(0.3)

        ticker = temp.pop()
        t = yf.Ticker(ticker)
        prev_close = t.fast_info["previous_close"]   # float

        # 배당/액션
        actions = t.actions

        if actions is None or actions.empty:
            continue

        try:
            longname = t.info['longName']

        except Exception as e:
            
            try:
                longname = t.info['shortName']
            
            except:
                print(f"{ticker} - {e}")
                continue

        actions = t.actions
        actions = actions.sort_index(ascending=False).reset_index()

        actions["symbol"] = ticker
        actions["longname"] = longname
        actions["close"] = prev_close
        actions["date_diff"] = ((actions["Date"] - actions["Date"].shift(-1)).astype(int)/86400000000000).astype(int)
        actions["rate"] = actions["Dividends"] / (actions["close"]) * 100

        actions = actions[actions['Date'] > '2025-01-01']
        ls_series.append(actions)

    df_dividends = pd.concat(ls_series, ignore_index=True)
    df_dividends = df_dividends.rename(columns={'Date': 'registdate', 'Dividends': 'dividends', 'Stock Splits': 'stocksplits', 'Capital Gains': 'capitalgain', 'date_diff': 'datediff'}, inplace=False)
    # df_dividends




    # conn = BaseHook.get_connection(CONN_ID)
    # uri = conn.get_uri()  # e.g. postgresql+psycopg://app:secret@postgres-meta:5432/appdb
    uri = f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@postgres-data/superset"
    engine = sa.create_engine(uri, future=True)

    # with engine.begin() as conn:
    #     conn.execute(text('TRUNCATE TABLE public."users" RESTART IDENTITY CASCADE;'))
    #     # conn.execute(text('drop table public.fear_greed_index;'))

    # 최초 생성 시 dtype 명시 가능

    df.to_sql("dividend_etf", engine, schema="public", if_exists="append", index=False, method="multi", chunksize=10_000)

    return 0


with DAG(
    dag_id="WEEKLY_INSERT_ETF_dividends",
    start_date=datetime.datetime(2025, 10, 1),
    # schedule=None,
    schedule='@monthly',
    catchup=False,
    default_args={"owner": "airflow"},
    tags=["postgres", "pandas"],
) as dag:
    read_task = PythonOperator(
        task_id="read_postgres",
        python_callable=insert_values,
    )
