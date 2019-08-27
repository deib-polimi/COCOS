from req import Req, ReqState
from device import Device
import random
import requests
import logging


class Dispatcher:
    PolicyRoundRobin = 0
    PolicyRandom = 1

    def __init__(self, logger, models, containers, policy: int = PolicyRoundRobin) -> None:
        self.logger = logger
        self.models = models
        self.containers = containers
        self.policy = policy

        if self.policy == self.PolicyRoundRobin:
            # initialize an device index for every model
            # TODO: initialize also for every version
            self.dev_indexes = {model.name: 0 for model in models}

        # set urllib3 logging level
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    def compute(self, req: Req):
        if req.model not in self.dev_indexes:
            # the model is not available
            req.state = ReqState.ERROR
            return 400, "Error: model not available"

        # filter the available containers for the model
        available_containers = list(
            filter(lambda c: (c.model == req.model or c.device == Device.GPU) and c.active, self.containers))

        if len(available_containers) == 0:
            # no available containers
            req.state = ReqState.ERROR
            return 400, "Error: no available container"

        # select the container
        if self.policy == self.PolicyRoundRobin:
            # select the next available container for the model
            self.dev_indexes[req.model] = (self.dev_indexes[req.model] + 1) % len(available_containers)
            dev_index = self.dev_indexes[req.model]
        elif self.policy == self.PolicyRandom:
            # select a random container
            dev_index = random.randint(0, len(available_containers) - 1)

        self.logger.info("Using: " + str(dev_index + 1) + "/" + str(len(available_containers)) + " | " + str(
            available_containers[dev_index]) + " | for: " + str(req.id))

        # set the req container and node
        req.container = available_containers[dev_index].container
        req.node = available_containers[dev_index].node
        req.state = ReqState.WAITING

        # call the predict on the selected device
        payload = {"instances": req.instances}
        try:
            response = requests.post(available_containers[dev_index].endpoint + "/v"
                                     + str(req.version) + "/models/" + req.model + ":predict",
                                     json=payload)
            return 200, response.text
        except Exception as e:
            self.logger.warning("EXCEPTION %s", e)
            req.state = ReqState.ERROR
            return 400, str(e)
