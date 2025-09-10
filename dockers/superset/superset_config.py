import os
SECRET_KEY = os.environ["SUPERSET_SECRET_KEY"]

from flask_appbuilder.security.manager import AUTH_DB
AUTH_TYPE = AUTH_DB
AUTH_ROLE_PUBLIC = "Public"
PUBLIC_ROLE_LIKE = None

WTF_CSRF_ENABLED = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
ENABLE_PROXY_FIX = True  # 프록시/로드밸런서 뒤에서 필수
