#orders.py
from typing import Optional, Dict, Any
from config import Config
from auth import Auth
from api_client import APIClient
from logger import get_logger

logger = get_logger()

class Orders:
    def __init__(self, config: Config, auth: Auth, api_client: APIClient, account_no: str):
        self.config = config
        self.auth = auth
        self.api_client = api_client
        self.account_no = account_no

    def place_order(self, stock_code: str, qty: int, price: int, order_type: str  # "buy" or "sell") -> Optional[Dict[str, Any]]:
        """
        매수 또는 매도 주문 수행

        Args:
            stock_code (str): 종목 코드 (예: "005930")
            qty (int): 주문 수량
            price (int): 주문 가격 (시장가 주문이면 0이나 적절히 처리)
            order_type (str): "buy" 또는 "sell"

        Returns:
            Optional[dict]: 주문 결과, 실패 시 None 반환
        """
        path = "/uapi/domestic-stock/v1/trading/order-cash"  # 가상의 주문 API 엔드포인트

        trade_type = "1" if order_type == "buy" else "2"  # 매수=1, 매도=2 (API 문서 확인 필수)

        data = {"CANO": self.account_no, "PDNO": stock_code, "ORDR_DVSN": trade_type, "ORD_QTY": qty, "ORD_UNPR": price}
            # 추가 파라미터 필요하면 확장

        logger.info(f"{order_type} 주문 요청: 종목 {stock_code}, 수량 {qty}, 가격 {price}")

        response = self.api_client.post(path, data=data)

        if not response:
            logger.error("주문 API 호출 실패")
            return None

        try:
            result_code = response.get("rt_cd")
            result_msg = response.get("msg_cd") or response.get("msg")

            if result_code == "0":  # 0이 성공 코드일 확률 높음, API 문서 확인 필수
                logger.info(f"{order_type} 주문 성공: {response}")
                return response
            else:
                logger.error(f"{order_type} 주문 실패: 코드 {result_code}, 메시지 {result_msg}")
                return None
        except Exception as e:
            logger.error(f"주문 결과 파싱 실패: {e}")
            return None
