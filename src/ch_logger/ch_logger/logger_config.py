'''
church logging module
'''
import os
import logging
import datetime

def setup_logger(file_hnd=logging.DEBUG, console_hnd=logging.INFO):
    '''
    setup_logger method
    '''
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    today = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{log_dir}/ch_app_{today}.log"

    # File handler
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(file_hnd)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_hnd)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] (%(threadName)s) %(message)s")

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
