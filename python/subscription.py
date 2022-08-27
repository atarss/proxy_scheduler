#!/usr/bin/env python3

import requests

import config
from utils import db64


def get_sub(proto=1):
    url = config.SUBSCRIPTION_URL
    url = url + "?sub={}".format(proto)

    logger = config.get_logger()
    logger.info("get url: {}".format(url))
    resp = db64(requests.get(url).text)
    resp = resp.splitlines()
    return resp


if __name__ == "__main__":
    ret = get_sub()
    for i in ret:
        print(i)
