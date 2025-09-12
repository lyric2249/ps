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

# Subpath deployment (/ss)
APPLICATION_ROOT = "/ss"
SESSION_COOKIE_PATH = "/ss"

# External base URL for redirects and absolute links
PUBLIC_HOST = os.environ.get("PUBLIC_HOST")
WEBSERVER_BASEURL = os.environ.get(
    "SUPERSET_WEBSERVER_BASEURL",
    f"https://{PUBLIC_HOST}/ss" if PUBLIC_HOST else None,
)
PREFERRED_URL_SCHEME = "https"