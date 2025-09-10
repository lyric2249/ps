# ps/dockers/superset/Dockerfile
ARG BASE_IMAGE=apache/superset
ARG BASE_TAG=3.1.0
FROM ${BASE_IMAGE}:${BASE_TAG}

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev default-libmysqlclient-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY superset_config.py /app/pythonpath/superset_config.py
COPY boot.sh /docker-entrypoint-initdb.d/10_boot.sh
RUN chmod +x /docker-entrypoint-initdb.d/10_boot.sh

RUN mkdir -p /app/superset_home && chown -R 1000:1000 /app/superset_home
USER 1000:1000
