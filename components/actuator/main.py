from flask import Flask, jsonify
from flask import request
import docker
from pprint import pprint

app = Flask(__name__)

client = docker.from_env()


@app.route('/containers', methods=['GET'])
def get_containers():
    for container in client.containers.list():
        app.logger.info(pprint(vars(container)))
    return jsonify([{"id": container.attrs["Id"],
                     "image": container.attrs['Config']['Image'],
                     "name": container.attrs["Name"],
                     "status": container.attrs["State"]["Status"]} for container in client.containers.list()])
