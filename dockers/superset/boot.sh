#!/usr/bin/env bash
set -e

superset fab create-admin \
  --username "${SUPERSET_ADMIN_USER}" \
  --firstname Admin --lastname User \
  --email "admin@example.com" \
  --password "${SUPERSET_ADMIN_PASSWORD}" || true

superset db upgrade
superset init

exec /usr/bin/run-server.sh

# from superset.app import create_app; app=create_app(); app.config.get("SQLALCHEMY_DATABASE_URI")
# superset@ec188ba55b11:/app$ echo "SQLALCHEMY_DATABASE_URI=$SQLALCHEMY_DATABASE_URI"
# superset@ec188ba55b11:/app$ echo "SUPERSET__SQLALCHEMY_DATABASE_URI=$SUPERSET__SQLALCHEMY_DATABASE_URI"