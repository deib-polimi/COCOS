from flask import Flask, jsonify
from flask import request
from model import Model, Device
from req import Req
from rr_dispatcher import RRDispatcher


app = Flask(__name__)

status = "Running"

models = []
model = Model("model_1", 1, True, Device.CPU, "n1", "m1", 5000, 0.5)
models.append(model)

reqs = []

rr_dispatcher = RRDispatcher(models)


@app.route('/status', methods=['GET'])
def get_status():
    return {"status": status}


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    app.logger.info("IN req %s: %s", data["model"], data["instances"])

    # Log incoming request
    req = Req(data["model"], data["instances"])
    reqs.append(req)

    # Forward request (dispatcher)
    # TODO: sync or async?
    result = rr_dispatcher.compute(req)

    # Log outcoming response
    req.set_completed(result)

    # Forward reply
    return {"result": result}


@app.route('/requests/<model_id>', methods=['GET'])
def get_metrics_by_model(model_id):
    # get the reqs associated with the model
    model_reqs = list(filter(lambda r: r.model == model_id, reqs))
    # compute the metrics
    metrics = Req.metrics(model_reqs)
    return {"metrics": metrics}


@app.route('/requests', methods=['GET'])
def get_requests():
    return {"requests": ([req.to_json() for req in reqs])}


@app.route('/models', methods=['GET', 'POST'])
def add_model():
    if request.method == 'GET':
        return {"models": ([model.to_json() for model in models])}
    elif request.method == 'POST':
        data = request.get_json()
        app.logger.info("Adding new model %s", data["name"])
        model = Model(data["name"], data["version"])
        models.append(model)
        return model.to_json()
