import datetime
import requests
import logging
from models.model import Model
from models.container import Container
from models.req import Req


class Controller:

    def __init__(self, models_endpoint: str, containers_endpoint: str, requests_endpoint: str):
        self.models_endpoint = models_endpoint
        self.containers_endpoint = containers_endpoint
        self.requests_endpoint = requests_endpoint

        self.models = []
        self.containers = []

        self.logs = []

    def init(self):
        # get the models
        self.models = [Model(json_data=json_model)
                       for json_model in self.get_data(self.models_endpoint)]
        self.logs.append("Loaded " + str(len(self.models)) + " models: " + str(
            [model.to_json() for model in self.models]))

        # get the containers
        self.containers = [Container(json_data=json_container)
                           for json_container in self.get_data(self.containers_endpoint)]
        self.logs.append("Loaded " + str(len(self.containers)) + " containers: " + str(
            [container.to_json() for container in self.containers]))

    def update(self):
        # get the requests data
        self.logs.append(str(datetime.datetime.now()) + " / Getting the request")
        reqs = [Req(json_data=json_req) for json_req in self.get_data(self.requests_endpoint)]

        # apply control given models and containers
        self.logs.append(str(datetime.datetime.now()) + " / Applying control")

        # update containers
        self.logs.append(str(datetime.datetime.now()) + " / Update containers")

    def get_logs(self):
        return self.logs

    def get_data(self, url):
        try:
            response = requests.get(url)
        except Exception as e:
            logging.warning(e)
            response = []
        return response.json()

    def to_json(self):
        pass
