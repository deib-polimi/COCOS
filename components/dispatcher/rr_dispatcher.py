from req import Req
import random
import time


class RRDispatcher:

    def __init__(self, models) -> None:
        self.models = models

    def compute(self, req: Req):
        time.sleep(random.random())

        available_devs = list(filter(lambda m: m.model == req.model, self.models))
        if len(available_devs) == 0:
            # no available devs
            return 0
        else:
            return len(available_devs)
