import requests
import logging
from actuator import Actuator
from models.model import Model
from models.container import Container
from models.req import Req


class Controller:

    def __init__(self, models_endpoint: str, containers_endpoint: str, requests_endpoint: str, actuator: Actuator,
                 node: str):
        self.models_endpoint = models_endpoint
        self.containers_endpoint = containers_endpoint
        self.requests_endpoint = requests_endpoint
        self.actuator = actuator
        self.node = node

        self.models = []
        self.containers = []

    def init(self):
        # get the models served by the node
        self.models = [Model(json_data=json_model) for json_model in
                       self.get_data(self.models_endpoint + "/" + self.node)]
        # get the containers served by the node
        self.containers = [Container(json_data=json_container) for json_container in
                           self.get_data(self.containers_endpoint + "/" + self.node)]

    def update(self):
        # get the requests data
        logging.info("Getting the request")
        reqs = [Req(json_data=json_req) for json_req in self.get_data(self.requests_endpoint + "/" + self.node)]
        logging.info("Requests: %s", [req.to_json() for req in reqs])

        # apply control given models and containers
        logging.info("Applying control")

        # update containers
        logging.info("Update containers")

    def get_data(self, url):
        try:
            response = requests.get(url)
        except Exception as e:
            logging.warning(e)
            response = []
        print(response)
        return response.json()

    def to_json(self):
        pass
