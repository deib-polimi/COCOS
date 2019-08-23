from flask import Flask, jsonify
from flask import request
from model import Model
from container import Container
from device import Device
import logging
import yaml
import requests

app = Flask(__name__)
app.config['SERVER_NAME'] = "localhost:5001"

CONFIG_FILE = "config.yml"
ACTUATOR_PORT = "30000"
CONTAINERS_LIST_ENDPOINT = "/containers"


@app.route('/', methods=['GET'])
def get_status():
    return {"status": status}


@app.route('/containers', methods=['GET', 'POST'])
def containers():
    if request.method == 'GET':
        return jsonify([container.to_json() for container in containers])
    """ elif request.method == 'POST':
    # TODO: add a new container
    data = request.get_json()
    app.logger.info("Adding new container %s", data["model"])
    container = Container(data["model"], data["version"])
    containers.append(container)
    return container.to_json()"""


@app.route('/models', methods=['GET', 'POST'])
def models():
    if request.method == 'GET':
        return jsonify([model.to_json() for model in models])
    """elif request.method == 'POST':
    # TODO: add a new model """


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
    nodes = set(map(lambda c: c.node, containers))
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


if __name__ == "__main__":
    models = []
    containers = []

    # init log
    log_format = "%(asctime)s:%(levelname)s:%(name)s:" \
                 "%(filename)s:%(lineno)d:%(message)s"
    logging.basicConfig(level='DEBUG', format=log_format)

    # init models and containers
    status = "reading config"
    logging.info(status)
    read_config_file()

    status = "linking containers with id"
    logging.info(status)
    link_containers_ids()

    # start
    status = "running"
    logging.info(status)
    app.run()