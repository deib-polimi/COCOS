from flask import Flask, jsonify
from flask import request
from req import Req
from dispatcher import Dispatcher
import logging
import json
import requests

app = Flask(__name__)


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

    app.logger.info("REQ %s: %s", data["model"], data["version"], data["instances"])

    # Log incoming request
    req = Req(data["model"], data["version"], data["instances"])
    reqs.append(req)

    # Forward request (dispatcher)
    response = dispatcher.compute(req)

    # Log outcoming response
    req.set_completed(response)

    # Forward reply
    return response


@app.route('/metrics', methods=['GET'])
def get_metrics():
    metrics = []
    for model in models:
        # filter the reqs associated with the model
        model_reqs = list(filter(lambda r: r.model == model.name and r.version == model.version, reqs))
        # compute the metrics
        metrics.append({"model": model.name, "version": model.version, "metrics": Req.metrics(model_reqs)})
    return jsonify(metrics)


@app.route('/requests', methods=['GET'])
def get_requests():
    return jsonify([req.to_json() for req in reqs])


def get_data(url):
    try:
        response = requests.get(url)
    except Exception as e:
        logging.warning(e)
        response = []
    return json.loads(response.content)


def create_app(containers_manager="http://localhost:5001", verbose=1):
    global reqs
    global dispatcher
    reqs = []

    # init log
    log_format = "%(asctime)s:%(levelname)s:%(name)s:" \
                 "%(filename)s:%(lineno)d:%(message)s"
    logging.basicConfig(level='DEBUG', format=log_format)

    # init models and containers
    models = get_data(containers_manager + "/models")
    logging.info("Models: %s", models)
    containers = get_data(containers_manager + "/containers")
    logging.info("Containers: %s", containers)

    # init dispatcher
    status = "Init dispatcher"
    logging.info(status)
    dispatcher = Dispatcher(app.logger, models, containers, Dispatcher.PolicyRoundRobin)

    # disable logging if verbose == 0
    logging.info("Verbose: %d", verbose)
    if verbose == 0:
        app.logger.disabled = True
        logging.getLogger('werkzeug').setLevel(logging.WARNING)

    # start
    status = "Running"
    logging.info(status)
    return app
