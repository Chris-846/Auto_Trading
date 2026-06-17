# market_data.py
import logging
import pandas as pd
from typing import Optional

from api_client import APIClient
from config import Config
from auth import Auth
from logger import get_logger

logger = get_logger()

class MarketData:
    """
    국내 주식 시세 조회 모듈
    삼성전자 현재가 조회와 시간외잔량 순위 API 포함
    """

    def __init__(self, config: Config, auth: Auth):
        self.api_client = APIClient(config, auth)

    def get_current_price(self, stock_code: str = "005930") -> Optional[int]:
        """
        기본시세 조회 - 삼성전자 현재가

        Args:
            stock_code (str): 종목코드 (기본값 005930)

        Returns:
            Optional[int]: 현재가(원), 실패하면 None
        """
        path = "/uapi/domestic-stock/v1/quotations/inquire-price"
        params = {
            "fid_cond_mrkt_div_code": "J",  # 코스피 시장코드
            "fid_input_iscd": stock_code,
        }

        logger.info(f"{stock_code} 현재가 조회 시작")
        response = self.api_client.get(path, params=params)
        if not response:
            logger.error("현재가 API 호출 실패 또는 무응답")
            return None

        try:
            current_price_str = response.get("output", {}).get("stck_prpr")
            if current_price_str is None:
                logger.error(f"현재가 데이터 없음: {response}")
                return None
            current_price = int(str(current_price_str).replace(",", ""))
            logger.info(f"{stock_code} 현재가: {current_price} 원")
            return current_price
        except Exception as e:
            logger.error(f"현재가 파싱 중 오류 발생: {e}")
            return None

    def after_hour_balance(
            self,
            fid_input_price_1: str = "",
            fid_cond_mrkt_div_code: str = "J",
            fid_cond_scr_div_code: str = "20176",
            fid_rank_sort_cls_code: str = "1",
            fid_div_cls_code: str = "0",
            fid_input_iscd: str = "0000",
            fid_trgt_exls_cls_code: str = "0",
            fid_trgt_cls_code: str = "0",
            fid_vol_cnt: str = "",
            fid_input_price_2: str = "",
            tr_cont: str = "",
            dataframe: Optional[pd.DataFrame] = None,
            depth: int = 0,
            max_depth: int = 10
    ) -> Optional[pd.DataFrame]:
        """
        국내주식 시간외잔량 순위 조회 (재귀 호출 가능)

        Args:
            위 각 파라미터 참조 (기본값 설정 포함)
            dataframe: 이전까지 누적된 데이터
            depth: 현재 재귀 깊이
            max_depth: 최대 재귀 깊이 제한

        Returns:
            Optional[pd.DataFrame]: 누적된 전체 시간외잔량 순위 데이터
        """
        if depth >= max_depth:
            logger.warning(f"최대 재귀 깊이 {max_depth}에 도달했습니다. 추가 호출 중지.")
            return dataframe if dataframe is not None else pd.DataFrame()

        api_url = "/uapi/domestic-stock/v1/ranking/after-hour-balance"
        tr_id = "FHPST01760000"

        params = {
            "fid_input_price_1": fid_input_price_1,
            "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
            "fid_cond_scr_div_code": fid_cond_scr_div_code,
            "fid_rank_sort_cls_code": fid_rank_sort_cls_code,
            "fid_div_cls_code": fid_div_cls_code,
            "fid_input_iscd": fid_input_iscd,
            "fid_trgt_exls_cls_code": fid_trgt_exls_cls_code,
            "fid_trgt_cls_code": fid_trgt_cls_code,
            "fid_vol_cnt": fid_vol_cnt,
            "fid_input_price_2": fid_input_price_2,
        }

        logger.info(f"시간외잔량 순위 API 호출, 재귀 깊이: {depth}")
        response = self.api_client.post(api_url, data={"tr_id": tr_id, **params})

        if not response:
            logger.error("시간외잔량 순위 API 호출 실패")
            return dataframe if dataframe is not None else pd.DataFrame()

        try:
            output = response.get("output")
            if output is None:
                logger.warning(f"출력 데이터 없음: {response}")
                return dataframe if dataframe is not None else pd.DataFrame()

            current_data = pd.DataFrame(output)
            # 기존 누적 데이터와 합친다
            if dataframe is not None and not dataframe.empty:
                dataframe = pd.concat([dataframe, current_data], ignore_index=True)
            else:
                dataframe = current_data

            # 다음 페이지가 있으면 재귀 호출 (tr_cont가 "M"인지 체크)
            tr_cont = response.get("header", {}).get("tr_cont", "")
            if tr_cont == "M":
                logger.info("다음 페이지 존재하여 재귀 호출 수행 중...")
                # 트래픽 부담 낮추기 위해 잠시 쉬기
                import time
                time.sleep(0.5)
                return self.after_hour_balance(
                    fid_input_price_1=fid_input_price_1,
                    fid_cond_mrkt_div_code=fid_cond_mrkt_div_code,
                    fid_cond_scr_div_code=fid_cond_scr_div_code,
                    fid_rank_sort_cls_code=fid_rank_sort_cls_code,
                    fid_div_cls_code=fid_div_cls_code,
                    fid_input_iscd=fid_input_iscd,
                    fid_trgt_exls_cls_code=fid_trgt_exls_cls_code,
                    fid_trgt_cls_code=fid_trgt_cls_code,
                    fid_vol_cnt=fid_vol_cnt,
                    fid_input_price_2=fid_input_price_2,
                    tr_cont=tr_cont,
                    dataframe=dataframe,
                    depth=depth + 1,
                    max_depth=max_depth
                )
            else:
                logger.info("모든 페이지 수집 완료")
                return dataframe

        except Exception as e:
            logger.error(f"시간외잔량 데이터 처리 오류: {e}")
            return dataframe if dataframe is not None else pd.DataFrame()
