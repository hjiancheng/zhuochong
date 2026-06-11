"""日志系统 - 强制刷新版（确保崩溃前日志不丢失）"""
import logging
import os
import sys
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)


class FlushFileHandler(logging.FileHandler):
    """每次写入后强制刷新的文件处理器"""
    def emit(self, record):
        super().emit(record)
        self.flush()


def setup_logger(name="yuexinmao", level=logging.DEBUG):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)

    log_path = os.path.join(LOG_DIR, "pet.log")
    fh = FlushFileHandler(log_path, mode='a', encoding='utf-8')
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


logger = setup_logger()
logger.info(f"日志系统初始化完成 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
