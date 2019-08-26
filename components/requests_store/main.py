from flask import Flask, jsonify
from flask import request
from req import Req
from flask_cors import CORS
from model import Model
import argparse
import logging
import requests

app = Flask(__name__)
CORS(app)

app.config['SERVER_NAME'] = "localhost:5002"


@app.route('/', methods=['GET'])
def get_status():
    return {"status": status}


@app.route('/requests', methods=['DELETE'])
def delete_requests():
    global reqs
    reqs = {}
    return jsonify(reqs)


@app.route('/requests', methods=['GET', 'POST'])
def get_requests():
    if request.method == 'GET':
        return jsonify([req.to_json() for req in reqs.values()])
    elif request.method == 'POST':
        rs = request.get_json()
        reqs[rs["id"]] = Req(json_data=rs)
        app.logger.info("+ %s", rs)
        return jsonify(rs)


@app.route('/metrics', methods=['GET'])
def get_metrics():
    metrics = []
    for model in models:
        # filter the reqs associated with the model
        model_reqs = list(filter(lambda r: r.model == model.name and r.version == model.version, reqs.values()))
        # compute the metrics
        metrics.append({"model": model.name, "version": model.version, "metrics": Req.metrics(model_reqs)})
    return jsonify(metrics)


def get_data(url):
    try:
        response = requests.get(url)
    except Exception as e:
        logging.warning(e)
        response = []
    print(response)
    return response.json()


if __name__ == "__main__":
    reqs = {}
    status = "running"

    parser = argparse.ArgumentParser()
    parser.add_argument('--containers_manager', type=str, required=True)
    args = parser.parse_args()

    # init log
    log_format = "%(asctime)s:%(levelname)s:%(name)s:" \
                 "%(filename)s:%(lineno)d:%(message)s"
    logging.basicConfig(level='DEBUG', format=log_format)

    # get models information
    models_endpoint = args.containers_manager + "/models"
    logging.info("Getting models from: %s", models_endpoint)

    models = [Model(json_data=json_model) for json_model in get_data(models_endpoint)]
    logging.info("Models: %s", [model.to_json() for model in models])

    app.run()
