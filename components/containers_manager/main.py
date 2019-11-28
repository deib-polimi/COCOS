import argparse

from flask import Flask, jsonify
from flask import request
import logging
import yaml
import requests
from flask_cors import CORS
from models.model import Model
from models.device import Device
from models.container import Container

app = Flask(__name__)
CORS(app)

CONFIG_FILE = "config/remote.yml"
ACTUATOR_PORT = "5000"
CONTAINERS_LIST_ENDPOINT = "/containers"


@app.route('/', methods=['GET'])
def get_status():
    return {"status": status}


@app.route('/containers', methods=['GET', 'PATCH'])
def containers():
    if request.method == 'GET':
        return jsonify([container.to_json() for container in containers])
    elif request.method == 'PATCH':
        data = request.get_json()
        app.logger.info("Request: " + str(data))

        app.logger.info("Updating container %s with quota %d", data["container_id"], data["cpu_quota"])

        # search and update the container quota
        for container in containers:
            if container.container_id == data["container_id"] or container.container_id[:12] == data["container_id"]:
                container.quota = data["cpu_quota"]
                app.logger.info("Container %s updated")
                break
        return {"response": "ok"}
    """ elif request.method == 'POST':
    # TODO: add a new container
    data = request.get_json()
    app.logger.info("Adding new container %s", data["model"])
    container = Container(data["model"], data["version"])
    containers.append(container)
    return container.to_json()"""


@app.route('/node/containers', methods=['GET'])
def containers_grouped_by_nodes():
    nodes = set(map(lambda c: c.node, containers))
    containers_in_node = {}
    for node in nodes:
        containers_in_node[node] = [container.to_json() for container in
                                    list(filter(lambda c: c.node == node, containers))]
    return jsonify(containers_in_node)


@app.route('/containers/<node>', methods=['GET'])
def containers_by_node(node):
    return jsonify([container.to_json() for container in list(filter(lambda c: c.node == node, containers))])


@app.route('/models', methods=['GET', 'PATCH'])
def models():
    if request.method == 'GET':
        return jsonify([model.to_json() for model in models])
    elif request.method == 'PATCH':
        data = request.get_json()
        app.logger.info("Request: " + str(data))
        app.logger.info("Updating model %s", data["model"])

        # search and update the model
        for model in models:
            if model.name == data["model"]:
                if data["sla"] is not None:
                    model.sla = float(data["sla"])
                    app.logger.info("Model %s updated", model.name)
                    break
        return {"response": "ok"}


@app.route('/models/<model_name>', methods=['GET'])
def get_model(model_name):
    for model in models:
        if model.name == model_name:
            return model.to_json()


@app.route('/models/<model_name>/containers', methods=['GET'])
def get_container_for_model(model_name):
    return jsonify(list(map(lambda c: c.to_json(), filter(lambda c: c.model == model_name, containers))))


@app.route('/models/<node>', methods=['GET'])
def models_by_node(node):
    models_node = []
    for model in models:
        if model.name in list(map(lambda c: c.model, list((filter(lambda c: c.node == node, containers))))):
            models_node.append(model)
    return jsonify([model.to_json() for model in models_node])


def read_config_file(config_file):
    """
    Read the configuration file and init the containers variable
    """
    with open(config_file, 'r') as file:
        data = file.read()
        config = yaml.load(data, Loader=yaml.FullLoader)

        # models
        if config["models"]:
            logging.info("Found %d models", len(config["models"]))

            for model in config["models"]:
                if "profiled_rt" in model:
                    models.append(
                        Model(model["name"], model["version"], model["sla"], model["alpha"], model["profiled_rt"]))
                else:
                    models.append(Model(model["name"], model["version"], model["sla"], model["alpha"]))

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


def containers_linking(actuator_port):
    """
    Link containers with ids
    """
    # get the set of nodes
    nodes = set(map(lambda c: c.node, containers))
    logging.info("Nodes: %s", nodes)

    # get the list of running containers for every node
    for node in nodes:
        containers_on_node = list(filter(lambda c: c.node == node, containers))

        try:
            response = requests.get("http://" + node + ":" + actuator_port + CONTAINERS_LIST_ENDPOINT)
            logging.info("Response: %d %s", response.status_code, response.text)

            if response.ok:
                # get the containers from the response
                running_containers = response.json()
                logging.info("Found %d containers on node %s", len(running_containers), node)

                # set the containers id
                linked_containers = 0
                for container in containers_on_node:
                    for running_container in running_containers:
                        if container.container == running_container["container_name"]:
                            container.container_id = running_container["id"]
                            logging.info("+ link: %s <-> %s", container.model, container.container_id)
                            linked_containers = linked_containers + 1
                            break
                logging.info("Linked %d containers on node %s", linked_containers, node)
            else:
                # disable model if actuator_controller response status is not 200
                logging.info("No containers found on node %s, (response not ok)", node)
                for container in containers_on_node:
                    container.active = False

        except Exception as e:
            logging.warning("Disabling containers for node: %s because %s", node, e)

            # disable containers if actuator_controller not reachable
            for container in containers_on_node:
                container.active = False

            break


def quota_reset(actuator_port, quota):
    """
    Set a default number of cores for all the containers
    """
    logging.info("Setting default cores for all containers to: %d", quota)
    for container in containers:
        if container.device == Device.CPU:
            response = requests.post(
                "http://" + container.node + ":" + str(
                    actuator_port) + CONTAINERS_LIST_ENDPOINT + "/" + container.container_id,
                json={"cpu_quota": int(quota * 100000)})
            logging.info("Actuator response: %s", response.text)
            container.quota = int(quota * 100000)


if __name__ == "__main__":
    models = []
    containers = []
    nodes = []

    # init log
    log_format = "%(asctime)s:%(levelname)s:%(name)s:" \
                 "%(filename)s:%(lineno)d:%(message)s"
    logging.basicConfig(level='DEBUG', format=log_format)

    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file', type=str, default=CONFIG_FILE)
    parser.add_argument('--actuator_port', type=str, default=ACTUATOR_PORT)
    parser.add_argument('--quota', type=float, required=True)
    args = parser.parse_args()

    # init models and containers
    status = "reading config file"
    logging.info(status)
    read_config_file(args.config_file)

    status = "linking containers with id"
    logging.info(status)
    containers_linking(args.actuator_port)

    status = "reset quota"
    logging.info(status)
    quota_reset(args.actuator_port, float(args.quota))

    # start
    status = "running"
    logging.info(status)
    app.run(host='0.0.0.0', port=5001)
