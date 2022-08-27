#!/usr/bin/env python3

import os
import json
from typing import List
from datetime import datetime
import subprocess

import requests

import config
import proxy
import utils


def get_sub(proto=1):
    url = config.SUBSCRIPTION_URL
    url = url + "?sub={}".format(proto)

    logger = config.get_logger()
    logger.info("get url: {}".format(url))
    resp = utils.db64(requests.get(url).text)
    resp = resp.splitlines()
    return resp


class ProxyScheduler:
    def __init__(self, save_path=config.SAVE_PATH):
        self.config_dict = {}  # `name` -> `config`
        self.remaining_traffic_bytes = None
        self.expiration_date = None
        self.running_name = None

        self._config_json_path = None
        self._logfile_path = None
        self._logfile = None
        self._server_process = None
        self._server_started_time = None

        self.logger = config.get_logger()

        self.save_path = save_path
        self._uri_list = None
        if os.path.isfile(save_path):
            with open(save_path, "r") as f:
                self._uri_list = [i.strip() for i in f.readlines()]
                self.load_uri_list(self._uri_list)

    def __repr__(self):
        s = "ProxyScheduler["
        s += "config={}".format(len(list(self.config_dict.keys())))
        if self.remaining_traffic_bytes is not None:
            s += ",remaining_traffic={}".format(self.remaining_traffic_bytes)
        if self.expiration_date is not None:
            s += ",expiration_date={}".format(self.expiration_date)
        s+= "]"
        return s

    def load_config_list(self, config_list:List[proxy.ProxyConfig]):
        for proxy_config in config_list:
            name = proxy_config.name
            self.logger.info("load config: " + name)

            if "剩余流量" in name:
                self.remaining_traffic_bytes = name.split("：")[-1]
            elif "过期时间" in name:
                self.expiration_date = name.split("：")[-1]
            else:
                self.config_dict[name] = proxy_config
    
    # load or update uri list
    def load_uri_list(self, uri_list:List[str]):
        if len(uri_list) <= 0:
            return
        self._uri_list = uri_list
        config_list = proxy.parse_list(uri_list)
        self.load_config_list(config_list)
        self.logger.info("load uri list: length={}".format(len(config_list)))

    def save_uri_list(self, save_path=None):
        if self._uri_list is None:
            return
        if save_path is None:
            save_path = self.save_path
        with open(save_path, "w") as f:
            for uri in self._uri_list:
                print(uri, file=f)
        self.logger.info("save uri_list to {} length={}".format(save_path, len(self._uri_list)))
    
    def update_subscription(self):
        # only could be done when server is not running
        if self._server_process is not None:
            return
        new_uri_list = get_sub()
        if len(new_uri_list) > 0:
            self.load_uri_list(new_uri_list)
            self.save_uri_list()

    def serve(self, name):
        self.logger.info("starting server: {}".format(name))
        assert name in self.config_dict
        proxy_config = self.config_dict[name]

        temp_basename = utils.get_temp_filename() + "_{}".format(name)
        self._config_json_path = os.path.join(config.TEMP_DIR, temp_basename + ".json")
        with open(self._config_json_path, "w") as f:
            json.dump(proxy_config.dump_config_json(), f)
        self._logfile_path = os.path.join(config.TEMP_DIR, temp_basename + ".log")
        self._logfile = open(self._logfile_path, "w", buffering=1)

        self.logger.info("server config json path: {}".format(self._config_json_path))
        self.logger.info("server logfile path: {}".format(self._logfile_path))

        self._server_process = proxy_config.get_proxy_process(self._config_json_path, self._logfile)
        self.logger.info("server started: PID={}".format(self._server_process.pid))
        self._server_started_time = datetime.now()
        self.running_name = name

    def stop(self):
        self.logger.info("stopping server: {}".format(self._config_json_path))
        if self._server_process is None:
            return

        self._server_process.terminate()
        
        if self._logfile is not None:
            self._logfile.close()

        self.running_name = None

        self._config_json_path = None
        self._logfile_path = None
        self._logfile = None
        self._server_process = None
        self._server_started_time = None
        self.logger.info("server stopped")

    def get_log(self, tail_lines=128) -> List[str]:
        if self._server_process is not None:
            lines = utils.get_log_tail(self._logfile_path, tail_lines).splitlines()
            lines = [i.replace("\x1b", "_") for i in lines]
            return "\n".join(lines)

    def __del__(self):
        self.logger.info("exiting...")
        if self._server_process is not None:
            self.stop()
        self.save_uri_list()
