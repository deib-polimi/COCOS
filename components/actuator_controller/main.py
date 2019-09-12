import argparse

from flask import Flask, jsonify
from flask import request
import docker
import logging
from actuator import Actuator
from controller import Controller
from pprint import pprint

app = Flask(__name__)

client = docker.from_env()


@app.route('/', methods=['GET'])
def get_status():
    return {"status": status}


@app.route('/containers', methods=['GET'])
def get_containers():
    """for container in client.containers.list():
        app.logger.info(pprint(vars(container)))"""
    return jsonify(actuator.containers)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--containers_manager', type=str, required=True)
    parser.add_argument('--requests_store', type=str, required=True)
    args = parser.parse_args()

    models_endpoint = args.containers_manager + "/models"
    logging.info("Setting models manager to: %s", models_endpoint)
    containers_endpoint = args.containers_manager + "/containers"
    logging.info("Setting containers_manager to: %s", containers_endpoint)
    requests_endpoint = args.requests_store + "/requests"
    logging.info("Setting requests_store to: %s", requests_endpoint)

    status = "init actuator_controller"
    logging.info(status)
    actuator = Actuator(client)
    actuator.init()

    status = "init controller"
    logging.info(status)
    controller = Controller(models_endpoint, containers_endpoint, requests_endpoint, actuator, "192.168.99.103")
    controller.init()

    status = "running"
    logging.info(status)
    app.run()
