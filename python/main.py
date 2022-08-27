#!/usr/bin/env python3

import os
import sys
import json
import time
from glob import glob

from flask import Flask, jsonify, request
from flask_cors import CORS

import config
import scheduler

logger = config.get_logger()


def main():
    config.check_dir()

    # load scheduler
    ps = scheduler.ProxyScheduler()

    app = Flask(__name__)

    # CORS for debug usage
    # DO NOT use it on a production environment
    # CORS(app)

    @app.route("/get/proxy_info")
    def get_ps_info():
        status = "running" if ps._server_process is not None else "stopped"
        if status == "running":
            server_started_time = ps._server_started_time.strftime("%Y%m%d-%H:%M:%S")
        else:
            server_started_time = "------"
        remaining_traffic = "UNKNOWN" if ps.remaining_traffic_bytes is None else ps.remaining_traffic_bytes
        expiration_date = "UNKNOWN" if ps.expiration_date is None else ps.expiration_date
        return jsonify({
            "status": status,
            "listen_on": "{}:{}".format(config.LOCAL_ADDR, config.LOCAL_PORT),
            "server_started_time": server_started_time,
            "running_config": "__none__" if ps.running_name is None else ps.running_name,
            "remaining_traffic": remaining_traffic,
            "expiration_date": expiration_date,
        })

    @app.route("/get/proxy_list")
    def get_name_list():
        name_list = sorted(list(ps.config_dict.keys()))
        return jsonify(name_list)

    @app.route("/get/proxy_log")
    def get_proxy_log():
        return jsonify({"log": ps.get_log()})

    @app.route("/start_proxy", methods=["GET"])
    def start_proxy():
        name = request.args.to_dict()['name']
        ps.serve(name)
        
        if ps._server_process is None:
            ret = False
        else:
            ret = True
        return jsonify({
            "success": ret,
        })

    @app.route("/stop_proxy", methods=["GET"])
    def stop_proxy():
        ps.stop()
        if ps._server_process is None:
            ret = True
        else:
            ret = False
        return jsonify({
            "success": ret,
        })

    app.run(config.API_SERVER_HOST, config.API_SERVER_PORT)


if __name__ == "__main__":
    main()
