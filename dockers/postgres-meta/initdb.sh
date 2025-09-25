#!/usr/bin/env bash
set -Eeuo pipefail

# 필수 변수 점검 (없으면 즉시 실패)
: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${POSTGRES_DB:?POSTGRES_DB is required}"
: "${SUPERSET_DB:=superset}"
: "${SUPERSET_DB_USER:=superset}"
: "${SUPERSET_DB_PASSWORD:?SUPERSET_DB_PASSWORD is required}"
: "${AIRFLOW_DB:=airflow}"
: "${AIRFLOW_DB_USER:=airflow}"
: "${AIRFLOW_DB_PASSWORD:?AIRFLOW_DB_PASSWORD is required}"


# psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<SQL
# DO \$\$
# BEGIN
#   IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '${SUPERSET_DB_USER}') THEN
#     EXECUTE format('CREATE ROLE %I LOGIN PASSWORD %L', '${SUPERSET_DB_USER}', '${SUPERSET_DB_PASSWORD}');
#   END IF;

#   IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = '${SUPERSET_DB}') THEN
#     EXECUTE format('CREATE DATABASE %I OWNER %I ENCODING ''UTF8'' TEMPLATE template0', '${SUPERSET_DB}', '${SUPERSET_DB_USER}');
#   END IF;

#   IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '${AIRFLOW_DB_USER}') THEN
#     EXECUTE format('CREATE ROLE %I LOGIN PASSWORD %L', '${AIRFLOW_DB_USER}', '${AIRFLOW_DB_PASSWORD}');
#   END IF;

#   IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = '${AIRFLOW_DB}') THEN
#     EXECUTE format('CREATE DATABASE %I OWNER %I ENCODING ''UTF8'' TEMPLATE template0', '${AIRFLOW_DB}', '${AIRFLOW_DB_USER}');
#   END IF;
# END
# \$\$;
# SQL


# 전제
export PGPASSWORD="$POSTGRES_PASSWORD"

psql -v ON_ERROR_STOP=1 \
  -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  -v su_user="$SUPERSET_DB_USER" -v su_pw="$SUPERSET_DB_PASSWORD" -v su_db="$SUPERSET_DB" \
  -v af_user="$AIRFLOW_DB_USER"  -v af_pw="$AIRFLOW_DB_PASSWORD"  -v af_db="$AIRFLOW_DB" <<'PSQL'
SELECT 'CREATE ROLE ' || quote_ident(:'su_user')
       || ' LOGIN PASSWORD ' || quote_literal(:'su_pw')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'su_user');
\gexec

SELECT 'CREATE ROLE ' || quote_ident(:'af_user')
       || ' LOGIN PASSWORD ' || quote_literal(:'af_pw')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'af_user');
\gexec

SELECT 'CREATE DATABASE ' || quote_ident(:'su_db')
       || ' OWNER ' || quote_ident(:'su_user')
       || ' ENCODING ''UTF8'' TEMPLATE template0'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = :'su_db');
\gexec

SELECT 'CREATE DATABASE ' || quote_ident(:'af_db')
       || ' OWNER ' || quote_ident(:'af_user')
       || ' ENCODING ''UTF8'' TEMPLATE template0'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = :'af_db');
\gexec
PSQL



# 2) 각 DB 후처리(스키마 소유권/확장)
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$SUPERSET_DB" <<SQL
ALTER SCHEMA public OWNER TO "$SUPERSET_DB_USER";
GRANT ALL PRIVILEGES ON DATABASE "$SUPERSET_DB" TO "$SUPERSET_DB_USER";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
SQL

psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$AIRFLOW_DB" <<SQL
ALTER SCHEMA public OWNER TO "$AIRFLOW_DB_USER";
GRANT ALL PRIVILEGES ON DATABASE "$AIRFLOW_DB" TO "$AIRFLOW_DB_USER";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
SQL
