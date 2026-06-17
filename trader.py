# trader.py
import time
import logging
from datetime import datetime, time as dt_time
from typing import Callable

from logger import get_logger

logger = get_logger(__name__)

def is_trading_time(start: dt_time = dt_time(9, 10), end: dt_time = dt_time(15, 30)) -> bool:
    """현재 시간이 거래 가능 시간 안에 있는지 체크"""
    now = datetime.now().time()
    return start <= now <= end

def trading_loop(trade_func: Callable, poll_interval: int = 60):
    """
    지정된 시간에만 거래 반복 실행하는 함수

    Args:
        trade_func (Callable): 실제 거래 처리 함수 (가격 조회, 주문 등)
        poll_interval (int): 반복 주기(초 단위)
    """
    logger.info("트레이딩 루프 시작 - 거래 가능 시간 동안만 동작합니다.")
    while True:
        if not is_trading_time():
            logger.info("거래 시간이 종료되었습니다. 프로그램을 종료합니다.")
            break

        try:
            logger.info("거래 함수 호출 중...")
            trade_func()
        except Exception as e:
            logger.error(f"거래 처리 중 오류 발생: {e}")

        logger.info(f"{poll_interval}초 대기 후 다시 실행합니다.")
        time.sleep(poll_interval)

if __name__ == "__main__":
    # 예시: trade_func 자리에는 실제 매매 로직 함수 넣기
    def dummy_trade():
        logger.info("여기에 매매 로직(가격 조회, 매수/매도 주문) 작성하세요.")

    trading_loop(dummy_trade, poll_interval=60)
