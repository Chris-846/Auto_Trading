# config.py
import os
from typing import Optional


class Config:
    """
    환경변수에서 인증 정보 및 기타 설정 불러오기
    - 모의투자 API 키 및 시크릿
    - HTS ID (계좌 주인 아이디)
    - 모의투자 계좌번호
    - API 도메인 주소
    - User-Agent 헤더 값
    """

    @staticmethod
    def get_env_var(key: str, required: bool = True) -> Optional[str]:
        value = os.getenv(key)
        if required and (value is None or value.strip() == ""):
            raise EnvironmentError(f"필수 환경변수 '{key}' 가 설정되어 있지 않습니다.")
        return value

    @property
    def app_key(self) -> str:
        # 예: paper_app, 나중에 환경변수 이름 바꾸면 여기만 변경
        return self.get_env_var("GH_APPKEY")

    @property
    def app_secret(self) -> str:
        # 예: paper_sec
        return self.get_env_var("GH_APPSECRET")

    @property
    def account(self) -> str:
        # HTS ID 또는 계정 ID
        return self.get_env_var("GH_ACCOUNT")

    @property
    def paper_account(self) -> str:
        # 모의 투자용 계좌번호
        return self.get_env_var("GH_PAPER_ACCOUNT")

    @property
    def api_domain(self) -> str:
        # 모의투자 API 서버 주소, 기본값도 지정 가능
        return self.get_env_var("GH_API_DOMAIN", required=False) or "https://openapivts.koreainvestment.com:29443"

    @property
    def user_agent(self) -> str:
        # User-Agent 헤더 값, 직접 환경변수로 받을 수 있게
        return self.get_env_var("GH_USER_AGENT", required=False) or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
