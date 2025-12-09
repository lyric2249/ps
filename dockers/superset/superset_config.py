import os
# SECRET_KEY = os.environ["SUPERSET_SECRET_KEY"]
SECRET_KEY = os.getenv("SUPERSET_SECRET_KEY")
SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
'''
from flask_appbuilder.security.manager import AUTH_DB
AUTH_TYPE = AUTH_DB
# AUTH_TYPE = AUTH_OAUTH
AUTH_ROLE_PUBLIC = "Public"
# PUBLIC_ROLE_LIKE = None
PUBLIC_ROLE_LIKE = "Gamma"  # ← 공개 사용자에게도 권한 부여 (예: 차트 보기)
'''

from custom_sso_security_manager import CustomSsoSecurityManager

CUSTOM_SECURITY_MANAGER = CustomSsoSecurityManager

# ====================================================================================
# OAuth 설정
# ====================================================================================



AUTH_ROLE_PUBLIC = "Public"
PUBLIC_ROLE_LIKE = "Gamma"  # ← 공개 사용자에게도 권한 부여 (예: 차트 보기)

from flask_appbuilder.security.manager import AUTH_OAUTH

print("DBG OAUTH client_id =", os.environ.get("GOOGLE_CLIENT_ID"))

# Set the authentication type to OAuth
AUTH_TYPE = AUTH_OAUTH

OAUTH_PROVIDERS = [
    {   'name':'google',            # Name of the provider
        'token_key':'access_token', # Name of the token in the response of access_token_url
        'icon':'fa-google',         # Icon for the provider
        'remote_app': {
            "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
            "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
            'api_base_url':'https://www.googleapis.com/oauth2/v2/',
            'client_kwargs':{
                # 'scope': 'read'               # Scope for the Authorization
                "scope": "openid email profile"
            },
            # 'access_token_method':'POST',    # HTTP Method to call access_token_url
            # 'access_token_params':{        # Additional parameters for calls to access_token_url
            #     'client_id':'myClientId'
            # },
            'jwks_uri':'https://www.googleapis.com/oauth2/v3/certs', # may be required to generate token
            # 'access_token_headers':{    # Additional headers for calls to access_token_url
            #     'Authorization': 'Basic Base64EncodedClientIdAndSecret'
            # },
            "request_token_url": None,
            'access_token_url':'https://oauth2.googleapis.com/token',
            'authorize_url':'https://accounts.google.com/o/oauth2/v2/auth'
        }
    }
]

# Will allow user self registration, allowing to create Flask users from Authorized User
AUTH_USER_REGISTRATION = False

# The default user self registration role
AUTH_USER_REGISTRATION_ROLE = "Public"
# AUTH_USER_REGISTRATION_ROLE = "Admin"





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



