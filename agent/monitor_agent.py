#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
This is the agent script for the Hpb-Monitor monitoring system.
"""
import yaml
import json
import os
import subprocess
import sys
import time
import platform
from datetime import datetime, timedelta
import psutil
import prometheus_client
from prometheus_client.core import CollectorRegistry, Gauge
from flask import Response, Flask
from web3 import Web3
from web3.eth import Eth


f = open('agent.yaml')
data = f.read()
agent_reader = yaml.load(data,Loader=yaml.FullLoader)
rpc_url = agent_reader['hpbnode']['rpc_url']
ghpb_path = agent_reader['hpbnode']['ghpb_path']
agent_port = agent_reader['hpbnode']['agent_port']
w3 = Web3(Web3.HTTPProvider(rpc_url))
eth = Eth(w3)

# exporter value variable
NODE_FLASK = Flask(__name__)
EXPORTER_PLATFORM = platform.platform()
AGENT_NAME = platform.node()

# exporter label variable
HPB_VERSION = "[ value is ghpb version ] ghpb version."
HPB_MINING = "[hpb mining]"
HPB_BLOCKNUMBER = "[hpb blocknumber]"
HPB_PEERCOUNT = "[hpb peers count]"

# class
class ExporterFunctions():
    """This class is to get HPB data"""

    def get_version(self):
        """request method"""
        req = ghpb_path + " version"
        try:
            req_result = os.popen(req).read()
        except OSError:
            log_time = time.asctime(time.localtime(time.time()))
            hpbversion = (log_time + " - Error - exec error[ " + req + " ]\n")
            boeversion = ""
        else:
            log_time = time.asctime(time.localtime(time.time()))
            if req_result == '':
                hpbversion = (log_time + " - Error - exec timeout[ " + req + " ]\n")
                boeversion = ""
            else:
                hpbversion = req_result.split('\n')[1]
                boeversion = req_result.split('\n')[3]
        return hpbversion,boeversion

    

# flask object
@NODE_FLASK.route("/metrics/ghpb")
def exporter():
    """Agent execution function"""
    print("query ghpb")
    # definition tag
    registry = CollectorRegistry(auto_describe=False)
    ghpb_version = Gauge("HPB_VERSION", HPB_VERSION, ["gversion","gboeversion"], registry=registry)
    
    is_mining = Gauge("HPB_Mining", HPB_MINING, ["gmining","gminer"], registry=registry)

    block_number = Gauge("HPB_BLOCKNUMBER", HPB_BLOCKNUMBER, ["number"], registry=registry)
    peers_count = Gauge("HPB_PEERCOUNT", HPB_PEERCOUNT, ["peercount"], registry=registry)

    # run exporter
    class_result = ExporterFunctions()

    version,boeversion = class_result.get_version()
    ghpb_version.labels(gversion=version,gboeversion=boeversion).set(1)

    mining = eth.mining
    miner = eth.coinbase
    is_mining.labels(gmining=mining,gminer=miner).set(1)


    number = eth.block_number
    block_number.labels(number=number).set(1)


    count = w3.net.peer_count
    peers_count.labels(peercount=count).set(2)
    
    return Response(prometheus_client.generate_latest(registry), mimetype="text/plain")


# flask object
@NODE_FLASK.route("/")
def index():
    """Page data view entry"""
    index_html = "<h2>访问 /metrics/cita 路径获取数据采集信息</h2>"
    return index_html


# main
if __name__ == "__main__":
    NODE_FLASK.run(host="0.0.0.0", port=int(agent_port))
