from flask import Flask, jsonify
from flask import request
from model import Model, Device
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
    req = Req(data["model"], data["instances"])
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
        model_reqs = list(filter(lambda r: r.container == model.container and r.node == model.node, reqs))
        # compute the metrics
        metrics.append({"model": model.model, "container": model.container, "metrics": Req.metrics(model_reqs)})
    return jsonify(metrics)


@app.route('/requests', methods=['GET'])
def get_requests():
    return jsonify([req.to_json() for req in reqs])


@app.route('/models', methods=['GET', 'POST'])
def add_model():
    if request.method == 'GET':
        return jsonify([model.to_json() for model in models])
    elif request.method == 'POST':
        data = request.get_json()
        app.logger.info("Adding new model %s", data["model"])
        model = Model(data["model"], data["version"])
        models.append(model)
        return model.to_json()

def init_models():
    status = "Init models: reading config"
    logging.info(status)
    read_config_file()

    status = "Init models: associating models with containers"
    logging.info(status)
    associate_models_containers()


def read_config_file():
    """
    Read the configuration file and init the
    models variable
    """
    with open(CONFIG_FILE, 'r') as file:
        data = file.read()
        config = yaml.load(data, Loader=yaml.FullLoader)

        if config["models"]:
            logging.info("Found %d models", len(config["models"]))

            for model in config["models"]:
                models.append(
                    Model(model["model"],
                          model["version"],
                          model["active"],
                          model["container"],
                          model["node"],
                          model["port"],
                          model["device"],
                          model["quota"]))
        logging.info("Loaded %d CPU models", len(list(filter(lambda m: m.device == Device.CPU, models))))
        logging.info("Loaded %d GPU models", len(list(filter(lambda m: m.device == Device.GPU, models))))
        logging.info([model.to_json() for model in models])


def associate_models_containers():
    """
    Associate models with running containers
    """
    # get the set of nodes
    nodes = set(map(lambda model: model.node, models))
    logging.info("Nodes: %s", nodes)

    # get the list of running containers for every node
    for node in nodes:
        response = requests.get("http://" + node + ":" + ACTUATOR_PORT + CONTAINERS_LIST_ENDPOINT)
        # TODO: check response status and disable model if actuator not reachable
        logging.info("Response: %s", response.text)
        containers = response.json()

        models_on_node = list(filter(lambda m: m.node == node, models))

        for model in models_on_node:
            for container in containers:
                logging.info("%s %s", model.container, container["container_name"])
                if model.container == container["container_name"]:
                    model.container_id = container["id"]
                    break


if __name__ == "__main__":
    # init vars
    models = []
    reqs = []

    # init log
    log_format = "%(asctime)s:%(levelname)s:%(name)s:" \
                 "%(filename)s:%(lineno)d:%(message)s"
    logging.basicConfig(level='DEBUG', format=log_format)

    # init models
    status = "Init models"
    logging.info(status)
    init_models()

    # init dispatcher
    status = "Init dispatcher"
    logging.info(status)
    dispatcher = Dispatcher(app.logger, models)

    # start
    status = "Running"
    logging.info(status)
    app.run()
