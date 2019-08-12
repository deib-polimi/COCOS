from flask import Flask, jsonify
from flask import request
from model import Model, Device
from req import Req
from dispatcher import Dispatcher


app = Flask(__name__)

status = "Running"

models = []
model1_1 = Model("model_1", 1, True, Device.CPU, "n1", "m1", 5000, 0.5)
model1_2 = Model("model_1", 1, True, Device.GPU, "n1", "m1", 5001, 0.5)
model2 = Model("model_2", 1, True, Device.CPU, "n2", "m2", 5000, 0.5)
models.append(model1_1)
models.append(model1_2)
models.append(model2)

reqs = []

dispatcher = Dispatcher(app.logger, models)


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
    # TODO: sync or async?
    response = dispatcher.compute(req)

    # Log outcoming response
    req.set_completed(response)

    # Forward reply
    return {"response": response}


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



