import docker
import logging
from flask import Flask, jsonify
from flask import request
from actuator import Actuator
from pprint import pprint

app = Flask(__name__)

client = docker.from_env()


@app.route('/', methods=['GET'])
def get_status():
    return {"status": status}


@app.route('/containers', methods=['GET'])
def get_containers():
    return jsonify(actuator.get_containers())


@app.route('/containers/<string:container_id>', methods=['POST'])
def set_quota(container_id):
    app.logger.info("Container ID: " + container_id)
    data = request.get_json()
    app.logger.info("Request: " + str(data))

    (resp_code, resp) = actuator.set_quota(container_id, data["cpu_quota"])
    if resp_code == 0:
        return {"response": "ok"}
    else:
        return {"response": resp}


if __name__ == "__main__":
    # init log
    log_format = "%(asctime)s:%(levelname)s:%(name)s:" \
                 "%(filename)s:%(lineno)d:%(message)s"
    logging.basicConfig(level='DEBUG', format=log_format)

    status = "init actuator"
    logging.info(status)
    actuator = Actuator(app.logger, client)

    status = "running"
    logging.info(status)
    app.run(host="0.0.0.0", port=5000)
