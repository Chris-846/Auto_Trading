import logging

from config_module import Config 
from auth_module import Auth  
from api_client_module import APIClient  

logger = logging.getLogger(__name__)


class Account:
    def __init__(self, config: Config, auth: Auth, api_client: APIClient, account_no: str):
        self.config = config
        self.auth = auth
        self.api_client = api_client
        self.account_no = account_no

    def get_balance(self) -> dict:
        """
        계좌 잔고 및 예수금 조회
        """
        path = "/uapi/domestic-stock/v1/trading/inquire-psbl-order"
        params = {
            "CANO": self.account_no,
            # 필요시 비밀번호, 조회구분 등 포함
        }
        response = self.api_client.get(path, params=params)

        if response is None:
            logger.error("계좌 잔고 조회 실패")
            return {}

        # 데이터 파싱 예, 실제 필드명에 맞게 변경해야 함
        try:
            balance_info = {
                "예수금": response["output"]["dps_amt"],
                "총평가금액": response["output"]["tot_eval_amt"],
                "주문가능금액": response["output"]["ord_psbl_cash"],
            }
            return balance_info
        except KeyError as e:
            logger.error(f"잔고 정보 파싱 오류: {e}")
            return {}

    def get_holdings(self) -> list:
        """
        보유 종목 현황 조회
        """
        path = "/uapi/domestic-stock/v1/trading/inquire-balance"
        params = {
            "CANO": self.account_no,
            # 필요 파라미터 추가
        }
        response = self.api_client.get(path, params=params)

        if response is None:
            logger.error("보유 종목 조회 실패")
            return []

        try:
            holdings = response["output"]["balance_yna"]
            return holdings
        except KeyError as e:
            logger.error(f"보유 종목 파싱 오류: {e}")
            return []
