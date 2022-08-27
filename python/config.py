#!/usr/bin/env python3

import os
from functools import lru_cache
import logging

from config_secret import SUBSCRIPTION_URL

API_SERVER_HOST = "127.0.0.1"
API_SERVER_PORT = 1280

# LOCAL_ADDR = "0.0.0.0"
# LOCAL_PORT = 8881
LOCAL_ADDR = "0.0.0.0"
LOCAL_PORT = 8881

OUTPUT_DIR = "./output"
TEMP_DIR = "./tmp"
SAVE_PATH = os.path.join(OUTPUT_DIR, "save.txt")
LOG_PATH = os.path.join(OUTPUT_DIR, "scheduler.log")

def check_dir():
    if not os.path.isdir(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    if not os.path.isdir(TEMP_DIR):
        os.makedirs(TEMP_DIR)

TEMPLATE = {
    "ssr": {
        "udp": False,
        "idle_timeout": 180,
        "connect_timeout": 6,
        "client_settings": {
            # "listen_address": LOCAL_ADDR,
            # "listen_port": LOCAL_PORT,
        },
    },

    "ss": {
        # TODO
    },

    "v2ray": {
        # TODO
    },
}

REPLACE_DICT = {
    '日本': 'jp',
    '俄罗斯': 'ru',
    '台湾': 'tw',
    '香港': 'hk',
    '新加坡': 'sg',
    '韩国': 'kr',
    '美国': 'us',
    '土耳其': 'tu',
    '巴基斯坦': 'pk',
    '英国': 'uk',
}

@lru_cache()
def get_logger():
    check_dir()
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(L%(lineno)d) %(message)s',
                                  datefmt='%d/%m/%Y %H:%M:%S')
    log_file = LOG_PATH
    # if not os.path.exists(EXP_DISK_BASE_PATH):
    #     os.makedirs(EXP_DISK_BASE_PATH, exist_ok=True)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    stream_handler.setLevel(logging.INFO)

    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger


if __name__ == "__main__":
    logger = get_logger()
    logger.info("config loaded")
