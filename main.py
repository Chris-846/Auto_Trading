# main.py
import sys
import logging
from datetime import datetime, time as dt_time
from time import sleep

from config import Config
from auth import Auth
from api_client import APIClient
from market_data import MarketData
from account import Account
from orders import Orders
from trader import is_trading_time, get_logger
from logger import get_logger

logger = get_logger(__name__)

def wait_until_trading_start(start_time: dt_time = dt_time(9, 10)):
    logger.info(f"거래 시작 시간 {start_time.strftime('%H:%M')}까지 대기 중입니다.")
    while True:
        now = datetime.now().time()
        if now >= start_time:
            logger.info("거래 시작 시간 도달! 자동매매 시작합니다.")
            break
        sleep(10)

def main():
    try:
        logger.info("자동매매 프로그램 시작")

        # 1. 환경 변수 및 설정 로드
        config = Config()

        # 2. 인증 및 토큰 관리
        auth = Auth(config, env_dv="demo")  # 모의투자 환경

        # 3. API 클라이언트 생성
        api_client = APIClient(config, auth)

        # 4. 각종 모듈 초기화
        market_data = MarketData(config, auth)
        account = Account(config, auth, api_client, config.paper_account)
        orders = Orders(config, auth, api_client, config.paper_account)

        # 5. 시작 전 거래 가능 시간까지 대기
        wait_until_trading_start(dt_time(9, 10))

        # 6. 실제 반복 거래 함수
        def trade_cycle():
            if not is_trading_time():
                logger.info("거래 시간이 종료되었습니다. 루프를 종료합니다.")
                sys.exit(0)

            logger.info("거래 사이클 시작")

            current_price = market_data.get_current_price("005930")
            if current_price is None:
                logger.error("현재가 조회 실패, 이번 사이클 주문 불가")
                return

            balance = account.get_balance()
            holdings = account.get_holdings()
            logger.info(f"현재 잔고: {balance}")
            logger.info(f"현재 보유종목: {holdings}")

            # 주문 수량 동적 계산 예: 잔고에 맞게 최소 1주 이상 주문
            order_qty = max(1, int(int(balance.get("주문가능금액", "0").replace(",", "")) // current_price))

            buy_price = current_price - 2000
            sell_price = current_price + 2000

            logger.info(f"매수 주문: 수량 {order_qty}, 가격 {buy_price}")
            buy_result = orders.place_order("005930", qty=order_qty, price=buy_price, order_type="buy")

            logger.info(f"매도 주문: 수량 {order_qty}, 가격 {sell_price}")
            sell_result = orders.place_order("005930", qty=order_qty, price=sell_price, order_type="sell")

            logger.info(f"매수 주문 결과: {buy_result}")
            logger.info(f"매도 주문 결과: {sell_result}")

        # 7. 트레이딩 루프 시작 (폴링 인터벌 60초)
        from trader import trading_loop
        trading_loop(trade_cycle, poll_interval=60)

        logger.info("자동매매 프로그램 정상 종료")

    except Exception as e:
        logger.exception(f"프로그램 실행 중 예기치 않은 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
