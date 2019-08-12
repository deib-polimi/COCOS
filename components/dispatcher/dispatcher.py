from req import Req
import random
import time


class Dispatcher:
    PolicyRoundRobin = 0
    PolicyRandom = 1

    def __init__(self, logger, models, policy: int = PolicyRoundRobin) -> None:
        self.logger = logger
        self.models = models
        self.policy = policy

        if self.policy == self.PolicyRoundRobin:
            # initialize an dev_index for every model
            self.dev_indexes = {model.model: 0 for model in models}

    def compute(self, req: Req):

        # filter the available instances for the model
        available_models = list(filter(lambda m: m.model == req.model, self.models))

        if len(available_models) == 0:
            # no available devs
            return 0

        if self.policy == self.PolicyRoundRobin:
            # select the next available dev for the model
            self.dev_indexes[req.model] = (self.dev_indexes[req.model] + 1) % len(available_models)
            dev_index = self.dev_indexes[req.model]

            self.logger.info("Using: " + str(dev_index + 1) + "/" + str(len(available_models)) + " | " + str(
                available_models[dev_index]) + " | for: " + str(req.id))

            # set the req model_id
            req.model_id = available_models[dev_index].id

            # call the predict on the selected device
            time.sleep(random.random()*3)

        # return the response
        response = len(available_models)

        return response