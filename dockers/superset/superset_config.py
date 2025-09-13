import os
SECRET_KEY = os.environ["SUPERSET_SECRET_KEY"]

from flask_appbuilder.security.manager import AUTH_DB
AUTH_TYPE = AUTH_DB
AUTH_ROLE_PUBLIC = "Public"
PUBLIC_ROLE_LIKE = None
# PUBLIC_ROLE_LIKE = "Gamma"  # ← 공개 사용자에게도 권한 부여 (예: 차트 보기)

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

# 🔽 서브패스 배포: /ss 로 통일
APPLICATION_ROOT = "/ss"
SESSION_COOKIE_PATH = "/ss"
WTF_CSRF_COOKIE_PATH = "/ss"

# 외부에서 보이는 절대 URL의 베이스
PUBLIC_HOST = os.environ.get("PUBLIC_HOST")  # 예: song-ps.site
WEBSERVER_BASEURL = os.environ.get(
    "SUPERSET_WEBSERVER_BASEURL",
    (f"https://{PUBLIC_HOST}/ss" if PUBLIC_HOST else None),
)

PREFERRED_URL_SCHEME = "https"

# 로그인 후 이동 (상대경로, /ss/에 맞춤)
LOGIN_REDIRECT_URL = "/ss/superset/welcome/"

