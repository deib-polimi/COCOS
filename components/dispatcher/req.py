import statistics as stat
import uuid
import time


class Req:

    def __init__(self, model: str, instances: list) -> None:
        self.id = uuid.uuid4()
        self.model = model
        self.instances = instances
        self.ts_in = time.time()
        self.ts_out = None
        self.response = None

    def set_completed(self, response):
        self.ts_out = time.time()
        self.response = response

    def to_json(self):
        return {
            "id": self.id,
            "model": self.model,
            "instances": self.instances,
            "ts_in": self.ts_in,
            "ts_out": self.ts_out,
            "response": self.response
        }

    @staticmethod
    def metrics(reqs):
        completed = list(filter(lambda r: r.ts_out is not None, reqs))
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
