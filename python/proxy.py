#!/usr/bin/env python3

from http import server
import os
import json
from copy import deepcopy
import subprocess
from typing import List
from urllib.parse import urlparse, parse_qs

import config
import utils


def convert_remark_to_config_name(remark_name:str):
    replace_dict = config.REPLACE_DICT
    name = remark_name.replace(" ", "")
    for source, target in replace_dict.items():
        if source in name:
            name = name.replace(source, target.upper())
            break
    return name


class ProxyConfig:
    def __init__(self):
        self.name = None
        self.server_process = None  # using Popen
        pass


class SSRProxyConfig(ProxyConfig):
    def __init__(self, uri=None):
        super().__init__()

        if uri is not None:
            self.parse_uri(uri)

    def __repr__(self):
        if self.name is None:
            return "SSRProxyConfig()"
        return "SSRProxyConfig({})".format(self.name)

    def parse_uri(self, uri:str):
        assert isinstance(uri, str)
        assert uri.startswith("ssr://")
        ssr_info = utils.db64(uri.split("ssr://", 1)[-1])

        ssr_main, ssr_query = ssr_info.split('/?', 1)
        ssr_main = ssr_main.split(":")
        assert len(ssr_main) == 6
        ssr_query = parse_qs(ssr_query)

        self.server_host = ssr_main[0]  # str
        self.server_port = int(ssr_main[1])  # int
        self.protocol = ssr_main[2]
        self.method = ssr_main[3]  # or `encrypto`
        self.obfuscator = ssr_main[4]
        self.password = utils.db64(ssr_main[5])

        self.obfuscator_param = ""
        if "obfsparam" in ssr_query:
            self.obfuscator_param = utils.db64(ssr_query["obfsparam"][0])
        self.protocol_param = ""
        if "protoparam" in ssr_query:
            self.protocol_param = utils.db64(ssr_query["protoparam"][0])

        remark_name = utils.db64(ssr_query["remarks"][0])
        config_name = convert_remark_to_config_name(remark_name)
        config_name = "SSR-" + config_name
        self.name = config_name

        return self

    def update_resolve(self):
        pass

    def dump_config_json(self, local_host=None, local_port=None) -> dict:
        config_json = deepcopy(config.TEMPLATE["ssr"])
        config_json.update({
            "password": self.password,
            "method": self.method,
            "protocol": self.protocol,
            "protocol_param": self.protocol_param,
            "obfs": self.obfuscator,
            "obfs_param": self.obfuscator_param,
        })

        if local_host is None:
            local_host = config.LOCAL_ADDR
        if local_port is None:
            local_port = config.LOCAL_PORT

        config_json["client_settings"].update({
            "server": self.server_host,
            "server_port": self.server_port,
            "listen_address": local_host,
            "listen_port": local_port,
        })
        
        return config_json

    def get_proxy_process(self, config_path, output=None) -> subprocess.Popen:
        # start using subprocess
        command_list = ["ssr-client", "-c", config_path]
        # logfile = open(logfile_path, "w")
        if output is None:
            p = subprocess.Popen(command_list)
        else:
            p = subprocess.Popen(command_list, stdout=output, stderr=output, 
                bufsize=1, universal_newlines=True)
        # terminate the process using 'p.terminate()'
        return p


def parse_list(uri_list: List[str]):
    result = []
    for uri in uri_list:
        if uri.startswith("ssr://"):
            result.append(SSRProxyConfig(uri))
        elif uri.startswith("ss://"):
            raise NotImplementedError
        elif uri.startswith("v2ray://"):
            raise NotImplementedError
        else:
            assert False
    return result
