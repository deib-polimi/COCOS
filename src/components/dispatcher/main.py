import argparse

from flask import Flask, jsonify
from flask import request
from model import Model
from container import Container, Device
from req import Req
from dispatcher import Dispatcher
import yaml
import logging
import requests

app = Flask(__name__)

CONFIG_FILE = "config.yml"
ACTUATOR_PORT = "30000"
CONTAINERS_LIST_ENDPOINT = "/containers"


@app.route('/', methods=['GET'])
def get_status():
    return {"status": status}


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    app.logger.info("REQ %s: %s", data["model"], data["instances"])

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


@app.route('/containers', methods=['GET', 'POST'])
def add_model():
    if request.method == 'GET':
        return jsonify([container.to_json() for container in containers])
    elif request.method == 'POST':
        data = request.get_json()
        app.logger.info("Adding new container %s", data["model"])
        container = Container(data["model"], data["version"])
        containers.append(container)
        return container.to_json()


def init_containers_models():
    global status
    status = "Init containers and models: reading config"
    logging.info(status)
    read_config_file()

    status = "Init containers and models: link containers with id"
    logging.info(status)
    link_containers_ids()


def read_config_file():
    """
    Read the configuration file and init the containers variable
    """
    with open(CONFIG_FILE, 'r') as file:
        data = file.read()
        config = yaml.load(data, Loader=yaml.FullLoader)

        # models
        if config["models"]:
            logging.info("Found %d models", len(config["models"]))

            for model in config["models"]:
                models.append(Model(model["name"], model["version"], model["sla"]))

        logging.info("+ %d models", len(models))

        # containers
        if config["containers"]:
            logging.info("Found %d containers", len(config["containers"]))

            for container in config["containers"]:
                containers.append(
                    Container(container["model"],
                              container["version"],
                              container["active"],
                              container["container"],
                              container["node"],
                              container["port"],
                              container["device"],
                              container["quota"]))
        logging.info("+ %d CPU containers", len(list(filter(lambda m: m.device == Device.CPU, containers))))
        logging.info("+ %d GPU containers", len(list(filter(lambda m: m.device == Device.GPU, containers))))
        logging.info([container.to_json() for container in containers])


def link_containers_ids():
    """
    Link containers with ids
    """
    # get the set of nodes
    nodes = set(map(lambda container: container.node, containers))
    logging.info("Nodes: %s", nodes)

    # get the list of running containers for every node
    for node in nodes:
        containers_on_node = list(filter(lambda c: c.node == node, containers))

        try:
            response = requests.get("http://" + node + ":" + ACTUATOR_PORT + CONTAINERS_LIST_ENDPOINT)
            # logging.info("Response: %d %s", response.status_code, response.text)

            if response.ok:
                # get the containers from the response
                running_containers = response.json()

                # set the containers id
                for container in containers_on_node:
                    for running_container in running_containers:
                        if container.container == running_container["container_name"]:
                            container.container_id = running_container["id"]
                            logging.info("+ link: %s § %s", container.model, container.container_id)
                            break
            else:
                # disable model if actuator response status is not 200
                for container in containers_on_node:
                    container.active = False

        except Exception as e:
            logging.warning("Disabling containers for node: %s because %s", node, e)

            # disable containers if actuator not reachable
            for container in containers_on_node:
                container.active = False

            break


def create_app(verbose=1):
    # init vars
    global models
    global containers
    global reqs
    global status
    global dispatcher

    models = []
    containers = []
    reqs = []

    # init log
    log_format = "%(asctime)s:%(levelname)s:%(name)s:" \
                 "%(filename)s:%(lineno)d:%(message)s"
    logging.basicConfig(level='DEBUG', format=log_format)

    # init containers
    status = "Init containers and models"
    logging.info(status)
    init_containers_models()

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
