# $AIRFLOW_HOME/webserver_config.py
from flask_appbuilder.security.manager import AUTH_DB

# 기본 로그인 수단은 DB 비번(변경 안 해도 됨)
AUTH_TYPE = AUTH_DB

# ★ 익명 사용자를 Viewer 권한으로 취급
AUTH_ROLE_PUBLIC = "ViewerMinor"
