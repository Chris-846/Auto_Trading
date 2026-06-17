# logger.py
import logging

def get_logger(name: str = __name__) -> logging.Logger:
    """
    프로젝트 공용 로거 생성 함수
    
    Args:
        name (str): 로거 이름, 기본은 호출 모듈 이름
    
    Returns:
        logging.Logger: 설정된 로거 객체
    """
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        # 로거 레벨 설정
        logger.setLevel(logging.INFO)

        # 콘솔 핸들러 생성
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 로그 메시지 포맷 설정
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)

        # 핸들러 로거에 추가
        logger.addHandler(console_handler)
        logger.propagate = False  # 상위로 로그 전파 방지

    return logger
