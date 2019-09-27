import statistics as stat
import uuid
import time
from enum import IntEnum


class Req:

    def __init__(self, model: str = None, version: int = None, instances: list = None, json_data=None) -> None:
        if json_data:
            self.__dict__ = json_data
        else:
            self.id = uuid.uuid4()
            self.model = model
            self.version = version
            self.instances = instances
            self.ts_in = time.time()
            self.ts_out = None
            self.node = None
            self.container = None
            self.response = None
            self.state = ReqState.CREATED

    def set_completed(self, response):
        self.ts_out = time.time()
        self.response = response
        self.state = ReqState.COMPLETED

    def to_json(self):
        if self.ts_out is not None:
            resp_time = self.ts_out - self.ts_in
        else:
            resp_time = None

        return {
            "id": str(self.id),
            "model": self.model,
            "version": self.version,
            "instances": self.instances,
            "node": self.node,
            "container": self.container,
            "ts_in": self.ts_in,
            "ts_out": self.ts_out,
            "resp_time": resp_time,
            "response": self.response,
            "state": self.state
        }

    @staticmethod
    def metrics(reqs):
        completed = list(filter(lambda r: r.state == ReqState.COMPLETED, reqs))
        resp_times = list(map(lambda r: r.ts_out - r.ts_in, completed))

        mean_t = min_t = max_t = dev_t = None
        if len(completed) > 0:
            mean_t = stat.mean(resp_times)
            min_t = min(resp_times)
            max_t = max(resp_times)

            if len(completed) > 1:
                dev_t = stat.variance(resp_times)

        return {
            "completed": len(completed),
            "waiting": len(reqs) - len(completed),
            "avg": mean_t,
            "dev": dev_t,
            "min": min_t,
            "max": max_t
        }


class ReqState(IntEnum):
    CREATED = 0
    WAITING = 1
    COMPLETED = 2
    ERROR = 3