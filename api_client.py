# api_client.py
import time
import logging
import requests
from typing import Any, Dict, Optional

from config import Config
from auth import Auth
from logger import get_logger

logger = get_logger()

class APIClient:
    def __init__(self, config: Config, auth: Auth):
        self.config = config
        self.auth = auth
        self.base_url = config.api_domain
        self.session = requests.Session()

    def _get_headers(self) -> Dict[str, str]:
        token = self.auth.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "User-Agent": self.config.user_agent,
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, params: Optional[Dict] = None,
                 data: Optional[Dict] = None, retries: int = 3) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}{path}"
        headers = self._get_headers()

        for attempt in range(1, retries + 1):
            try:
                if method.upper() == "GET":
                    response = self.session.get(url, headers=headers, params=params, timeout=10)
                elif method.upper() == "POST":
                    response = self.session.post(url, headers=headers, json=data, timeout=10)
                else:
                    logger.error(f"지원하지 않는 HTTP 메서드: {method}")
                    return None

                if response.status_code == 200:
                    return response.json()

                # 5xx 에러는 재시도 대상
                if 500 <= response.status_code < 600:
                    logger.warning(f"{method} {url} - 서버 오류 {response.status_code} 발생, {attempt}번째 재시도")
                    time.sleep(1)
                    continue

                # 4xx 에러는 호출자에게 알려줌
                logger.error(f"{method} {url} 호출 실패 - 상태코드: {response.status_code}, 내용: {response.text}")
                return None

            except requests.RequestException as e:
                logger.warning(f"{method} {url} 요청 예외 발생: {e} - {attempt}번째 재시도")
                time.sleep(1)
        logger.error(f"{method} {url} 호출 실패, 최대 재시도 {retries}회 모두 실패")
        return None

    def get(self, path: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        return self._request("GET", path, params=params)

    def post(self, path: str, data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        return self._request("POST", path, data=data)
