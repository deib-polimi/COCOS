from flask import Flask, jsonify
from flask import request
from model import Model, Device
from req import Req
from dispatcher import Dispatcher
import yaml
import logging

app = Flask(__name__)

CONFIG_FILE = "config.yml"


@app.route('/status', methods=['GET'])
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
        model_reqs = list(filter(lambda r: r.model_id == model.id, reqs))
        # compute the metrics
        metrics.append({"model": model.model, "model_id": model.id, "metrics": Req.metrics(model_reqs)})
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


def init_dispatcher():
    # Read config file
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
                          model["device"],
                          model["node"],
                          model["port"],
                          model["quota"]))
        logging.info("Loaded %d CPU models", len(list(filter(lambda m: m.device == Device.CPU, models))))
        logging.info("Loaded %d GPU models", len(list(filter(lambda m: m.device == Device.GPU, models))))
        logging.info([model.to_json() for model in models])


if __name__ == "__main__":
    models = []
    reqs = []

    log_format = "%(asctime)s:%(levelname)s:%(name)s:" \
                 "%(filename)s:%(lineno)d:%(message)s"
    logging.basicConfig(level='DEBUG', format=log_format)

    status = "Reading config"
    logging.info(status)
    init_dispatcher()

    status = "Init dispatcher"
    logging.info(status)
    dispatcher = Dispatcher(app.logger, models)

    status = "Running"
    logging.info(status)
    app.run()
