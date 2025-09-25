import os
# SECRET_KEY = os.environ["SUPERSET_SECRET_KEY"]
SECRET_KEY = os.getenv("SUPERSET_SECRET_KEY")
SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

from flask_appbuilder.security.manager import AUTH_DB
AUTH_TYPE = AUTH_DB
AUTH_ROLE_PUBLIC = "Public"
# PUBLIC_ROLE_LIKE = None
PUBLIC_ROLE_LIKE = "Gamma"  # ← 공개 사용자에게도 권한 부여 (예: 차트 보기)

WTF_CSRF_ENABLED = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# 프록시 환경 필수
ENABLE_PROXY_FIX = True
PROXY_FIX_CONFIG = {
    "x_for": 1,
    "x_proto": 1,
    "x_host": 1,
    "x_port": 1,
    "x_prefix": 1,  # ← X-Forwarded-Prefix 신뢰
}


PREFERRED_URL_SCHEME = "https"



