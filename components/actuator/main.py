from flask import Flask, jsonify
from flask import request
import docker
from pprint import pprint

app = Flask(__name__)

client = docker.from_env()
status = "running"


@app.route('/containers', methods=['GET'])
def get_containers():
    for container in client.containers.list():
        app.logger.info(pprint(vars(container)))
    return jsonify([{"id": container.attrs["Id"],
                     "image": container.attrs["Config"]["Image"],
                     "name": container.attrs["Name"],
                     "status": container.attrs["State"]["Status"],
                     "container_name": container.attrs["Config"]["Labels"]["io.kubernetes.container.name"]}
                    for container in client.containers.list()])


@app.route('/containers/<string:container_id>', methods=['POST'])
def set_quota(container_id):
    app.logger.info("Container ID: " + container_id)
    data = request.get_json()
    app.logger.info("Request: " + str(data))

    container = client.containers.get(container_id)
    resp = container.update(cpu_quota=int(data["cpu_quota"]))

    return jsonify(resp)


@app.route('/', methods=['GET'])
def get_status():
    return {"status": status}


if __name__ == "__main__":
    app.run()
