from flask import Flask, jsonify, abort, request
from req import Req
from dispatcher import Dispatcher
from model import Model
from container import Container
import logging
import requests
import threading
import queue

app = Flask(__name__)

reqs = queue.Queue()
reqs_batch_size = 2


@app.route('/', methods=['GET'])
def get_status():
    return {"status": status}


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data:
        return {'error': 'input not specified'}
    elif 'model' not in data.keys():
        return {'error': 'key model not specified'}
    elif 'version' not in data.keys():
        return {'error': 'key version not specified'}
    elif 'instances' not in data.keys():
        return {'error': 'key instances not specified'}

    app.logger.info("REQ %s/V%s %s", data["model"], data["version"], data["instances"])

    # Log incoming request
    req = Req(data["model"], data["version"], data["instances"])
    reqs.put(req)

    # Forward request (dispatcher)
    status_code, response = dispatcher.compute(req)

    # Log outcoming response
    if status_code == 200:
        req.set_completed(response)
    else:
        response = jsonify(response)
        response.status_code = 400
    reqs.put(req)

    # Forward reply
    return response


def send_requests():
    while True:
        payload = reqs.get().to_json()
        response = requests.post(requests_store_host, json=payload)
        app.logger.info("OUTGOING_R: %s", response.text)


def get_data(url):
    try:
        response = requests.get(url)
    except Exception as e:
        logging.warning(e)
        response = []
    return response.json()


def create_app(containers_manager="http://localhost:5001", requests_store="http://localhost:5002", verbose=1):
    global dispatcher
    global requests_store_host
    global status
    requests_store_host = requests_store + "/requests"

    # init log
    log_format = "%(asctime)s:%(levelname)s:%(name)s:" \
                 "%(filename)s:%(lineno)d:%(message)s"
    logging.basicConfig(level='DEBUG', format=log_format)

    # init models and containers
    status = "init models and containers"
    logging.info(status)
    models_endpoint = containers_manager + "/models"
    containers_endpoint = containers_manager + "/containers"
    logging.info("Getting models from: %s", models_endpoint)
    logging.info("Getting containers from: %s", containers_endpoint)

    models = [Model(json_data=json_model) for json_model in get_data(models_endpoint)]
    logging.info("Models: %s", [model.to_json() for model in models])
    containers = [Container(json_data=json_container) for json_container in get_data(containers_endpoint)]
    logging.info("Containers: %s", [container.to_json() for container in containers])

    # init dispatcher
    status = "init dispatcher"
    logging.info(status)
    dispatcher = Dispatcher(app.logger, models, containers, Dispatcher.PolicyRoundRobin)

    # disable logging if verbose == 0
    logging.info("verbose: %d", verbose)
    if verbose == 0:
        app.logger.disabled = True
        logging.getLogger('werkzeug').setLevel(logging.WARNING)

    # start the send requests thread
    send_reqs_thread = threading.Thread(target=send_requests)
    send_reqs_thread.start()

    # start
    status = "running"
    logging.info(status)
    return app
