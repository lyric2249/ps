#!/usr/bin/env bash
set -Eeuo pipefail

# : "${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN:?AIRFLOW DB URI missing}"



# DB 대기 (메타 Postgres)
until pg_isready -h postgres-meta -p 5432 -t 2; do
  echo "[airflow-init] waiting for postgres-meta:5432 ..."
  sleep 1
done

# Airflow DB 준비 (이미 초기화면 check가 0, 아니면 migrate 수행)
echo "[airflow-init] DB: $(airflow config get-value database sql_alchemy_conn)"
airflow db check || airflow db migrate

# (선택) 관리자 계정 등 초기화
# airflow users create --role Admin --admin ${AIRFLOW_ADMIN_USER} --password ${AIRFLOW_ADMIN_PASSWORD} --email a@b.c --firstname A --lastname B || true

airflow db migrate

echo "[airflow-init] done."


