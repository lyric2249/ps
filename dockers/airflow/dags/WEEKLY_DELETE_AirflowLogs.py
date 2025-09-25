# dags/cleanup_logs.py
import os
import stat
import time
import pendulum
from datetime import timedelta
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator

BASE_PATH        = "/opt/airflow/logs"
RETENTION_DAYS   = 14
DRY_RUN          = Variable.get("log_cleanup__dry_run", default_var="false").lower() in ("1","true","yes")
FOLLOW_SYMLINKS  = False  

def _safe_is_within(path, root):
    # 절대경로 고정 및 경로 이탈 방지
    path = os.path.realpath(path)
    root = os.path.realpath(root)
    return os.path.commonpath([path, root]) == root

def cleanup_logs(**_):
    base = os.path.realpath(BASE_PATH)
    if not os.path.isdir(base):
        print(f"[cleanup] base not exists: {base}")
        return

    now = time.time()
    cutoff = now - (RETENTION_DAYS * 24 * 3600)
    deleted_files = 0
    skipped_files = 0
    errors = 0

    # 파일 삭제
    for dirpath, dirnames, filenames in os.walk(base, topdown=True, followlinks=FOLLOW_SYMLINKS):
        # . / .. 예방 + base 밖 경로 이탈 예방
        if not _safe_is_within(dirpath, base):
            print(f"[cleanup] skip unexpected dir: {dirpath}")
            continue

        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            try:
                # 링크/권한 체크
                try:
                    st = os.lstat(fpath)
                except FileNotFoundError:
                    continue

                # 심볼릭 링크는 기본적으로 스킵(원하면 FOLLOW_SYMLINKS=True)
                if stat.S_ISLNK(st.st_mode) and not FOLLOW_SYMLINKS:
                    skipped_files += 1
                    continue

                mtime = st.st_mtime
                if mtime <= cutoff:
                    # 안전장치: base 밖은 절대 삭제하지 않음
                    if not _safe_is_within(fpath, base):
                        print(f"[cleanup] safety skip (outside base): {fpath}")
                        skipped_files += 1
                        continue
                    if DRY_RUN:
                        print(f"[dry-run] remove file: {fpath}")
                    else:
                        os.remove(fpath)
                        deleted_files += 1
                else:
                    skipped_files += 1
            except Exception as e:
                print(f"[cleanup] error removing {fpath}: {e}")
                errors += 1

    # 빈 디렉터리 정리(깊은 곳부터)
    for dirpath, dirnames, filenames in os.walk(base, topdown=False, followlinks=FOLLOW_SYMLINKS):
        try:
            # 파일도 없고 하위 디렉터리도 없으면 제거
            if not dirnames and not filenames and _safe_is_within(dirpath, base):
                if DRY_RUN:
                    print(f"[dry-run] rmdir: {dirpath}")
                else:
                    os.rmdir(dirpath)
        except Exception as e:
            print(f"[cleanup] error rmdir {dirpath}: {e}")

    print(f"[cleanup] deleted={deleted_files}, skipped={skipped_files}, errors={errors}, retention_days={RETENTION_DAYS}, base={base}, dry_run={DRY_RUN}")

with DAG(
    dag_id="WEEKLY_DELETE_AirflowLogs",
    start_date=pendulum.datetime(2025, 1, 1, tz="Asia/Seoul"),
    schedule="30 3 * * *",        # 매일 03:30 KST
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "airflow",
        "retries": 0,
    },
    tags=["maintenance", "logs"],
) as dag:

    PythonOperator(
        task_id="delete_old_log_files",
        python_callable=cleanup_logs,
    )
