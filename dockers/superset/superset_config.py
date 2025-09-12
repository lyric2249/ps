import os
SECRET_KEY = os.environ["SUPERSET_SECRET_KEY"]

from flask_appbuilder.security.manager import AUTH_DB
AUTH_TYPE = AUTH_DB
AUTH_ROLE_PUBLIC = "Public"
# PUBLIC_ROLE_LIKE = None
PUBLIC_ROLE_LIKE = "Gamma" 

WTF_CSRF_ENABLED = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
ENABLE_PROXY_FIX = True  # 프록시/로드밸런서 뒤에서 필수

PROXY_FIX_CONFIG = {
    "x_for": 1,
    "x_proto": 1,
    "x_host": 1,
    "x_port": 1,
    "x_prefix": 1,
}

# Subpath deployment (/superset)
APPLICATION_ROOT = "/superset"
SESSION_COOKIE_PATH = "/superset"
# CSRF cookie도 동일 경로로 제한 (서브패스 운용 시 권장)
WTF_CSRF_COOKIE_PATH = "/superset"

# External base URL for redirects and absolute links
PUBLIC_HOST = os.environ.get("PUBLIC_HOST")
WEBSERVER_BASEURL = os.environ.get(
    "SUPERSET_WEBSERVER_BASEURL",
    (f"https://{PUBLIC_HOST}/superset" if PUBLIC_HOST else None),
)
PREFERRED_URL_SCHEME = "https"