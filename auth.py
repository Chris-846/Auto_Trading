# auth.py
import json
import logging
import os
import time
from typing import Optional, Dict

import requests

from config import Config
from logger import get_logger

logger = get_logger()

TOKEN_CACHE_FILE = "token_cache.json"
TOKEN_VALIDITY_SECONDS = 3600  # 토큰 유효기간 (필요시 조절)

API_URL_PATH = "/oauth2/tokenP"  # OAuth 토큰 발급 엔드포인트

class Auth:
    def __init__(self, config: Config, env_dv: str = "real"):
        """
        OAuth 인증 관리 클래스
        
        Args:
            config (Config): 환경변수로 불러온 설정 객체
            env_dv (str): "real" (실전) 또는 "demo" (모의) 환경 구분
        """
        self.config = config
        if env_dv not in ("real", "demo"):
            raise ValueError("env_dv must be 'real' or 'demo'")
        self.env_dv = env_dv
        self.token_info = self._load_token_cache()

    def _get_base_url(self) -> str:
        """환경에 따라 API 기본 URL 반환"""
        # config.api_domain에 모의투자 주소 담겨 있다고 가정
        if self.env_dv == "real":
            # 실전 도메인 필요 시 변경
            return self.config.api_domain.replace("vts", "v1")
        return self.config.api_domain

    def _load_token_cache(self) -> Optional[Dict]:
        if not os.path.exists(TOKEN_CACHE_FILE):
            return None
        try:
            with open(TOKEN_CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception as e:
            logger.error(f"토큰 캐시 읽기 실패: {e}")
            return None

    def _save_token_cache(self, token: str, timestamp: float):
        try:
            with open(TOKEN_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump({"token": token, "timestamp": timestamp}, f)
            logger.info("토큰 캐시 저장 완료")
        except Exception as e:
            logger.error(f"토큰 캐시 저장 실패: {e}")

    def _is_token_valid(self) -> bool:
        if not self.token_info:
            return False
        now = time.time()
        expired_at = self.token_info.get("timestamp", 0) + TOKEN_VALIDITY_SECONDS
        return now < expired_at

    def get_token(self) -> str:
        if self._is_token_valid():
            logger.info("기존 토큰 재사용")
            return self.token_info["token"]

        logger.info("OAuth 토큰 신규 발급 요청 시작")
        token = self._request_new_token()
        if not token:
            raise RuntimeError("OAuth 토큰 발급 실패")
        self._save_token_cache(token, time.time())
        self.token_info = {"token": token, "timestamp": time.time()}
        return token

    def _request_new_token(self) -> Optional[str]:
        url = f"{self._get_base_url()}{API_URL_PATH}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/plain",
            "charset": "UTF-8",
            "User-Agent": self.config.user_agent,
        }
        payload = {
            "grant_type": "client_credentials",
            "appkey": self.config.app_key,
            "appsecret": self.config.app_secret,
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    logger.info("OAuth 토큰 발급 성공")
                    return token
                else:
                    logger.error(f"토큰 응답에 access_token 누락: {data}")
            else:
                logger.error(f"토큰 요청 실패 - 상태코드: {response.status_code} 응답: {response.text}")
        except requests.RequestException as e:
            logger.error(f"토큰 요청 중 예외 발생: {e}")
        return None
