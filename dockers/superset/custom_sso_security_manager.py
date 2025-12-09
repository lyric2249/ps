# custom_sso_security_manager.py
import logging
from superset.security import SupersetSecurityManager

logger = logging.getLogger(__name__)


class CustomSsoSecurityManager(SupersetSecurityManager):
    def oauth_user_info(self, provider, response=None):
        logger.debug("oauth_user_info for provider=%s", provider)

        if provider == "google":
            # 위에서 정의한 OAUTH_PROVIDERS['google']를 참조
            remote = self.appbuilder.sm.oauth_remotes[provider]

            # base_url + "userinfo" -> https://www.googleapis.com/oauth2/v2/userinfo
            me = remote.get("userinfo").json()
            email = me.get("email")
            logger.warning("Google userinfo=%s", me)
            logger.warning("Google email=%s", email)







            # userinfo 예시 필드: email, given_name, family_name 등
            # (Google OAuth / OIDC userinfo 엔드포인트 스펙 참고) :contentReference[oaicite:14]{index=14}
            return {
                "username": me.get("email"),          # Superset username
                "email": me.get("email"),
                "first_name": me.get("given_name", ""),
                "last_name": me.get("family_name", ""),
            }

        # 다른 provider는 기본 동작
        return super().oauth_user_info(provider, response)
