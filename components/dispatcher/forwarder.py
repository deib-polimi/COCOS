from dispatcher import Dispatcher
from dispatcher import DispatchingPolicy
from flask import Flask, jsonify, abort, request
from models.req import Req
from models.model import Model
from models.device import Device
from models.container import Container
from models.queues_policies import QueuesPolicies, QueuesPolicy
from concurrent.futures import ThreadPoolExecutor
import logging
import requests
import threading
import queue
import coloredlogs
import time

app = Flask(__name__)


@app.route('/', methods=['GET'])
def get_status():
    return {"status": status}


@app.route('/v1/models/<model_name>:predict', methods=['POST'])
def predict(model_name):
    data = request.get_json()
    if not data:
        return {'error': 'input not specified'}

    payload = {"instances": data["instances"]}
    response = requests.post(endpoint + "/v1/models/" + model_name + ":predict",
                             json=payload)
    logging.info(response.text)
    # Forward 200
    return {"status": "ok"}


def create_app(endpoint_tfs):
    global endpoint
    endpoint = endpoint_tfs

    log_format = "%(asctime)s:%(levelname)s:%(name)s: %(filename)s:%(lineno)d:%(message)s"
    logging.basicConfig(level='DEBUG', format=log_format)
    return app
