import time

from models.req import Req, ReqState
from models.device import Device
import random
import requests
import logging
from enum import IntEnum
from threading import Lock


# Define how requests are dispatched to containers
class DispatchingPolicy(IntEnum):
    ROUND_ROBIN = 0
    RANDOM = 1


class Dispatcher:
    def __init__(self,
                 logger,
                 models,
                 containers,
                 policy: int = DispatchingPolicy.ROUND_ROBIN,
                 device=None) -> None:
        self.logger = logger
        self.models = models
        self.containers = containers
        self.policy = policy
        self.device = device
        self.lock = {model.name: Lock() for model in models}

        # Group containers by model selecting the given type of device
        self.logger.info("Grouping containers for device type: %s", self.device)

        self.available_containers = {}
        if self.device is None:  # select all type of device
            for model in models:
                self.available_containers[model.name] = list(
                    filter(lambda c: (c.model == model.name or c.model == "all") and c.active, self.containers))
        elif self.device == Device.CPU:  # CPU containers serve only one model
            for model in models:
                self.available_containers[model.name] = list(
                    filter(lambda c: c.model == model.name and c.device == Device.CPU and c.active, self.containers))
        elif self.device == Device.GPU:  # GPU containers serve all models
            for model in models:
                self.available_containers[model.name] = list(
                    filter(lambda c: c.device == Device.GPU and c.active, self.containers))

        self.logger.info("Available containers are: %s",
                         {ac: [str(c.container_id) + ", Dev: " + str(c.device) for c in self.available_containers[ac]]
                          for ac in self.available_containers})

        self.dev_indexes = {model.name: 0 for model in models}

        # set urllib3 logging level
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    def compute(self, req: Req):
        if req.model not in self.dev_indexes:
            # the model is not available
            return 400, "Error: model not available"

        # get the available containers for the model
        available_containers = self.available_containers[req.model]

        if len(available_containers) == 0:
            # no available containers
            return 400, "Error: no available container"

        # select the container
        if self.policy == DispatchingPolicy.ROUND_ROBIN:
            # select the next available container for the model
            with self.lock[req.model]:
                self.dev_indexes[req.model] = (self.dev_indexes[req.model] + 1) % len(available_containers)
            dev_index = self.dev_indexes[req.model]
        elif self.policy == DispatchingPolicy.RANDOM:
            # select a random container
            dev_index = random.randint(0, len(available_containers) - 1)

        # self.logger.info("Using: " + str(dev_index + 1) + "/" + str(len(available_containers)) + " | " + str(
        #    available_containers[dev_index]) + " | for: " + str(req.id))

        # set the req container and node
        req.container = available_containers[dev_index].container
        req.container_id = available_containers[dev_index].container_id
        req.node = available_containers[dev_index].node
        req.device = self.device
        req.set_waiting()

        # call the predict on the selected device
        payload = {"instances": req.instances}
        try:
            response = requests.post(available_containers[dev_index].endpoint + "/v"
                                     + str(req.version) + "/models/" + req.model + ":predict",
                                     json=payload)
            # self.logger.info(response.text)
            req.set_completed(response)
            return
        except Exception as e:
            self.logger.warning("EXCEPTION %s", e)
            req.set_error(400 + "\n" + str(e))
            return
