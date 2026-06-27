import os
import json
from typing import Optional


class Config:
    """
    SECRET_FILES 환경변수에 JSON 형태로 인증 정보 등을 담아서 읽어오는 방식

    - 모의투자 API 키 및 시크릿
    - HTS ID (계좌 주인 아이디)
    - 모의투자 계좌번호
    - API 도메인 주소
    - User-Agent 헤더 값
    """

    def __init__(self):
        secret_json = os.getenv("SECRET_FILES")
        if secret_json:
            try:
                self.secrets = json.loads(secret_json)
            except json.JSONDecodeError:
                raise EnvironmentError("SECRET_FILES 환경변수 JSON 파싱에 실패했습니다!")
        else:
            # SECRET_FILES가 없다면 빈 dict, 개별 환경변수로 fallback
            self.secrets = {}

    def get_env_var(self, key: str, required: bool = True) -> Optional[str]:
        # 먼저 SECRET_FILES 딕셔너리에서 찾고, 없으면 실제 환경변수에서 찾아요~
        if key in self.secrets and self.secrets[key].strip() != "":
            return self.secrets[key]
        value = os.getenv(key)
        if required and (value is None or value.strip() == ""):
            raise EnvironmentError(f"필수 환경변수 '{key}' 가 설정되어 있지 않습니다.")
        return value

    @property
    def app_key(self) -> str:
        # SECRET_FILES 안에 gh_appkey 키가 있으면 그것 쓰고, 아니면 환경변수 GH_APPKEY
        return self.get_env_var("gh_appkey") or self.get_env_var("GH_APPKEY")

    @property
    def app_secret(self) -> str:
        return self.get_env_var("gh_appsecret") or self.get_env_var("GH_APPSECRET")

    @property
    def account(self) -> str:
        return self.get_env_var("gh_account") or self.get_env_var("GH_ACCOUNT")

    @property
    def paper_account(self) -> str:
        return self.get_env_var("gh_paper_account") or self.get_env_var("GH_PAPER_ACCOUNT")

    @property
    def api_domain(self) -> str:
        return self.get_env_var("gh_api_domain", required=False) or self.get_env_var("GH_API_DOMAIN", required=False) or "https://openapivts.koreainvestment.com:29443"

    @property
    def user_agent(self) -> str:
        return self.get_env_var( "gh_user_agent", required=False) or self.get_env_var("GH_USER_AGENT", required=False) or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
