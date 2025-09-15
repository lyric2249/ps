#!/usr/bin/env bash
set -Eeuo pipefail

echo "[airflow-init] start"

# 필수 환경변수 확인(없으면 즉시 실패)
: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_DB:?POSTGRES_DB is required}"

pip install --no-cache-dir "apache-airflow-providers-fab==2.4.2"



# psql 비밀번호 전달
export PGPASSWORD="$POSTGRES_PASSWORD"

# Postgres 준비 대기
until pg_isready -h postgres-meta -p 5432 -U "$POSTGRES_USER"; do
  echo "[airflow-init] waiting for postgres-meta:5432 ..."
  sleep 1
done

PSQL="psql -h postgres-meta -U $POSTGRES_USER -d $POSTGRES_DB -v ON_ERROR_STOP=1"

# Airflow용 ROLE/DB 생성(존재하면 skip)
PSQL="psql -h postgres-meta -U $POSTGRES_USER -d $POSTGRES_DB -v ON_ERROR_STOP=1"

$PSQL <<'SQL'
-- 1) role은 DO 블록에서 생성 (OK)
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'airflow') THEN
    CREATE ROLE airflow LOGIN PASSWORD 'airflow_pw';
  END IF;
END$$;

-- 2) DB 생성은 블록 밖에서 조건부 + \gexec
SELECT 'CREATE DATABASE airflow OWNER airflow'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow') \gexec
SQL


# DB 마이그레이션 (필요 시 init 백업)
if ! airflow db migrate; then
  echo "[airflow-init] migrate failed, trying 'airflow db init'..."
  airflow db init
fi

echo "[airflow-init] done."


