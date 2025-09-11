# ps/dockers/superset/Dockerfile

ARG BASE_IMAGE=apache/superset
ARG BASE_TAG=3.1.0
FROM ${BASE_IMAGE}:${BASE_TAG}

# ➊ OS 빌드 툴/헤더 + MySQL 클라이언트 헤더(사용한다면) 설치
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config libpq-dev \
    libssl-dev libffi-dev \
    libmariadb-dev-compat libmariadb-dev \
 && rm -rf /var/lib/apt/lists/*

# ➋ pip 툴체인 최신화 (중요)
RUN python -m pip install --no-cache-dir -U pip setuptools wheel

# ➌ (선택) 휠 우선으로 받아서 소스 빌드 회피
ENV PIP_ONLY_BINARY=:all:

# ➍ 파이썬 의존성 설치
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# ➎ Superset 설정/부트 스크립트
COPY superset_config.py /app/pythonpath/superset_config.py
COPY boot.sh /docker-entrypoint-initdb.d/10_boot.sh
RUN chmod +x /docker-entrypoint-initdb.d/10_boot.sh

RUN mkdir -p /app/superset_home && chown -R 1000:1000 /app/superset_home
USER 1000:1000
