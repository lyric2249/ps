#!/usr/bin/env bash
set -e

superset fab create-admin \
  --username "${SUPERSET_USERNAME}" \
  --firstname Admin --lastname User \
  --email "${SUPERSET_EMAIL}" \
  --password "${SUPERSET_PASSWORD}" || true

superset db upgrade
superset init

exec /usr/bin/run-server.sh
