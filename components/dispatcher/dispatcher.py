from req import Req
import random
import requests


class Dispatcher:
    PolicyRoundRobin = 0
    PolicyRandom = 1

    def __init__(self, logger, models, policy: int = PolicyRoundRobin) -> None:
        self.logger = logger
        self.models = models
        self.policy = policy

        if self.policy == self.PolicyRoundRobin:
            # initialize an device index for every model
            self.dev_indexes = {model.model: 0 for model in models}

    def compute(self, req: Req):

        # filter the available instances for the model
        available_models = list(filter(lambda m: m.model == req.model and m.active, self.models))

        if len(available_models) == 0:
            # no available devs
            return "Error: no available devices"

        if self.policy == self.PolicyRoundRobin:
            # select the next available dev for the model
            self.dev_indexes[req.model] = (self.dev_indexes[req.model] + 1) % len(available_models)
            dev_index = self.dev_indexes[req.model]
        elif self.policy == self.PolicyRandom:
            dev_index = random.randint(0, len(available_models)-1)

        self.logger.info("Using: " + str(dev_index + 1) + "/" + str(len(available_models)) + " | " + str(
            available_models[dev_index]) + " | for: " + str(req.id))

        # set the req container and node
        req.container = available_models[dev_index].container
        req.node = available_models[dev_index].node

        # call the predict on the selected device
        payload = {"instances": req.instances}
        response = requests.post(available_models[dev_index].endpoint, json=payload)

        self.logger.info(response.text)

        # return the response
        return response.text
