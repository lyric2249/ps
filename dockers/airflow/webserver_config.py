# $AIRFLOW_HOME/webserver_config.py
import os
from flask_appbuilder.security.manager import AUTH_DB, AUTH_OAUTH



# 기본 로그인 수단은 DB 비번(변경 안 해도 됨)
AUTH_TYPE = AUTH_DB

# ★ 익명 사용자를 Viewer 권한으로 취급
AUTH_ROLE_PUBLIC = "ViewerMinor"


# === 기본 인증 타입을 OAuth로 전환 ===
AUTH_TYPE = AUTH_OAUTH

# 필요에 따라 조정
AUTH_USER_REGISTRATION = False
AUTH_USER_REGISTRATION_ROLE = "Viewer"  # 첫 유저를 Admin으로 하고 싶으면 "Admin"

# 첫 로그인 시 자동으로 Admin 부여 예시 (optional)
# AUTH_USER_REGISTRATION_ROLE_JMESPATH = (
#     "email == 'you@example.com' && 'Admin' || 'Viewer'"
# )

# 실제 OAuth provider 정의 (Google)
OAUTH_PROVIDERS = [
    {
        "name": "google",
        "icon": "fa-google",
        "token_key": "access_token",
        "remote_app": {
            # GCP OAuth client에서 받은 값은 보통 env로 주입
            "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
            "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),

            # Google OAuth 엔드포인트 (Airflow에서 많이 쓰는 패턴들)
            # userinfo용 base URL
            "api_base_url": "https://www.googleapis.com/oauth2/v2/",
            "client_kwargs": {
                "scope": "email profile",
            },
            'jwks_uri':'https://www.googleapis.com/oauth2/v3/certs', # may be required to generate token
            # 'access_token_headers':{    # Additional headers for calls to access_token_url
            #     'Authorization': 'Basic Base64EncodedClientIdAndSecret'
            # },
            "request_token_url": None,

            # 토큰/authorize URL (StackOverflow 및 예제 기준):contentReference[oaicite:2]{index=2}
            "access_token_url": "https://oauth2.googleapis.com/token",
            "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",

            # 필요하다면 콜백 URL 명시 (보통은 안 써도 자동)
            # Airflow 2.x 기준 기본 redirect: https://<AIRFLOW_URL>/oauth-authorized/google :contentReference[oaicite:3]{index=3}
            # "redirect_url": "/oauth-authorized/google",
        },
    }
]
