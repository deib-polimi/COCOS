import argparse
import logging
import threading

from flask import Flask, jsonify
from controller import Controller

app = Flask(__name__)


@app.route('/', methods=['GET'])
def get_status():
    return {"status": status}


@app.route('/logs', methods=['GET'])
def get_logs():
    return jsonify(controller.get_logs())


def control():
    app.logger.info("Control")
    controller.update()
    threading.Timer(args.time, control).start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--containers_manager', type=str, required=True)
    parser.add_argument('--requests_store', type=str, required=True)
    parser.add_argument('--time', type=float, required=True)
    args = parser.parse_args()

    models_endpoint = args.containers_manager + "/models"
    logging.info("Setting models manager to: %s", models_endpoint)
    containers_endpoint = args.containers_manager + "/containers"
    logging.info("Setting containers_manager to: %s", containers_endpoint)
    requests_endpoint = args.requests_store + "/requests"
    logging.info("Setting requests_store to: %s", requests_endpoint)

    status = "init controller"
    logging.info(status)
    controller = Controller(models_endpoint, containers_endpoint, requests_endpoint)
    controller.init()

    threading.Timer(args.time, control).start()

    status = "running"
    logging.info(status)
    app.run(port=5003, debug=True)
