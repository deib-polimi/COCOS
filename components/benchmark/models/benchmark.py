import json
import logging
import time
import requests
import yaml
import statistics as stat
from enum import IntEnum
from .models.req import Req, ReqState


class BenchmarkStrategies(IntEnum):
    SINGLE_STREAM = 0
    MULTIPLE_STREAM = 1
    SERVER = 2
    OFFLINE = 3


class Mode(IntEnum):
    BENCHMARK = 0
    PROFILING = 1


class Benchmark:

    def __init__(self, params_file, model, version, benchmark_strategy, logger):
        self.model = model
        self.version = version

        if logger:
            self.logger = logger
        else:
            self.logger = logging

        self.bench_data = []
        self.validation_data = []
        self.responses = []
        self.avg_times = []

        self.mode = None

        # load parameters
        self.params = None
        self.load_parameters(params_file)

        # endpoints
        if "endpoint_profiler" in self.params.keys():
            self.endpoint_profiler = self.params["endpoint_profiler"] + "/v1/models/" + self.model + ":predict"
        else:
            self.endpoint_profiler = None
        if "endpoints_benchmark" in self.params.keys():
            self.endpoints_benchmark = [endpoint_benchmark + "/predict"
                                        for endpoint_benchmark in self.params["endpoints_benchmark"]]
        else:
            self.endpoints_benchmark = None
        self.endpoint = None

        # folders
        if "bench_folder" in self.params.keys():
            self.bench_folder = self.params["bench_folder"] + "/" + self.model + "/"
        else:
            self.bench_folder = "bench_folder/" + self.model + "/"
        if "validation_folder" in self.params.keys():
            self.validation_folder = self.params["validation_folder"] + "/" + self.model + "/"
        else:
            self.validation_folder = "validation_data/" + self.model + "/"
        self.warm_up_reqs = self.params.get("warm_up_times", 5)
        self.repeat_measure = self.params.get("repeat_measure", 5)

        # set benchmark strategy
        self.benchmark_strategy = benchmark_strategy
        self.requests_ids = []

        if self.benchmark_strategy == BenchmarkStrategies.SINGLE_STREAM:
            strategy_key = "single_stream"
        elif self.benchmark_strategy == BenchmarkStrategies.MULTIPLE_STREAM:
            strategy_key = "multiple_stream"
        elif self.benchmark_strategy == BenchmarkStrategies.SERVER:
            strategy_key = "server"
        else:
            strategy_key = "offline"

        self.duration = self.params[strategy_key]["duration"]
        self.samples_per_query = self.params[strategy_key]["samples_per_query"]
        self.tail = self.params[strategy_key]["tail"]

        # requests store
        self.requests_store = self.params["requests_store"] + "/requests"

    def prepare_request(self, instances):
        if self.mode == Mode.PROFILING:
            request = {"instances": instances}
        else:  # self.mode == Mode.BENCHMARK:
            request = {"model": self.model, "version": self.version, "instances": instances}
        return request

    def load_parameters(self, params_file):
        """
        Load parameters from file
        """
        with open(params_file, 'r') as file:
            data = file.read()
            self.params = yaml.load(data, Loader=yaml.FullLoader)

    def load_requests_from_file(self):
        """
        Load the requests file from the bench folder
        """
        file_path = self.bench_folder + self.model + ".json"
        self.logger.info("loading requests from file %s", file_path)
        with open(file_path, 'r') as file:
            for data in json.load(file)["data"]:
                self.bench_data.append({"data": data["instances"], "request": self.prepare_request(data["instances"])})
            # self.logger.info("bench_data: %s", self.bench_data)

    def warm_up_model(self, data):
        """
        Send few request to warm up the model
        """
        self.logger.info("warming up the model %d times", self.warm_up_reqs)
        for _ in range(self.warm_up_reqs):
            response = self.post_request(data["request"])
        self.logger.info("warm up ended")

    def post_request(self, json_request):
        response = requests.post(self.endpoint, json=json_request)
        response.raise_for_status()
        return response

    def get_request(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return response

    """
    Benchmark
    """

    def before_benchmark(self):
        """
        Abstract
        Executed before benchmark is started
        """
        pass

    def after_benchmark(self):
        reqs = []
        self.logger.info("responses: %s", [response.text for response in self.responses])

        self.logger.info("waiting requests from requests_store for %s...", self.requests_ids)
        time.sleep(1)

        for i in range(10):
            response = self.get_request(self.requests_store)
            reqs = list(filter(lambda req: req["id"] in self.requests_ids and req["state"] == ReqState.COMPLETED,
                               response.json()))
            self.logger.info("found %d reqs: %s", len(reqs), reqs)
            if len(reqs) < len(self.requests_ids):
                self.logger.info("waiting requests from requests_store...")
                time.sleep(1)
            else:
                break

        reqs = list(map(lambda rs: Req(json_data=rs), reqs))
        self.logger.info("metrics: %s", Req.metrics(reqs))

    def benchmark(self):
        self.logger.info("using strategy %s", self.benchmark_strategy)
        self.logger.info("profiling the model with %d bench data", len(self.bench_data))
        if self.benchmark_strategy == BenchmarkStrategies.SINGLE_STREAM:
            for data in self.bench_data:
                response = self.post_request(data["request"])
                self.responses.append(response)
                self.requests_ids.append(response.json()["id"])
        elif self.benchmark_strategy == BenchmarkStrategies.MULTIPLE_STREAM:
            pass
        elif self.benchmark_strategy == BenchmarkStrategies.SERVER:
            pass
        elif self.benchmark_strategy == BenchmarkStrategies.OFFLINE:
            pass

    def run_benchmark(self):
        self.bench_data.clear()
        self.responses.clear()
        self.requests_ids.clear()

        self.logger.info("+++ running benchmark with the following parameters: %s", self.params)
        self.mode = Mode.BENCHMARK
        self.endpoint = self.endpoints_benchmark[0]
        self.logger.info("endpoint: %s", self.endpoint)

        self.logger.info("+++ before benchmark")
        self.before_benchmark()

        self.logger.info("+++ starting benchmark")
        self.benchmark()

        self.logger.info("+++ after benchmark")
        self.after_benchmark()

    """
    Profiling
    """

    def before_profiling(self):
        """
        Abstract
        Executed before profiling is started, e.g.:
        - load the requests data,
        - perform some pre profile works
        - warm up the model, etc.
        """
        pass

    def after_profiling(self):
        """
        Abstract
        Executed after profiling is done, e.g.:
        - save profiling data.
        - elaborate response data,
        - save response, etc.
        """
        pass

    def before_validate(self):
        """
        Abstract
        - load the validation data
        - prepare the requests
        """
        pass

    def after_validate(self):
        """
        Abstract
        - load the validation data
        - prepare the requests
        """
        pass

    def show_data(self, data):
        """
        Abstract
        Print the given data
        """
        pass

    def show_response(self, response):
        """
        Abstract
        Print the given response
        """
        pass

    def profile(self):
        self.logger.info("profiling the model %d times per request", self.repeat_measure)
        self.logger.info("profiling the model with %d bench data", len(self.bench_data))
        for data in self.bench_data:
            times = []
            for _ in range(0, self.repeat_measure):
                response = self.post_request(data["request"])
                self.responses.append(response)
                times.append(response.elapsed.total_seconds())
            avg_time = stat.mean(times)
            self.avg_times.append(float(avg_time))

    def run_profiling(self):
        self.bench_data.clear()
        self.responses.clear()

        self.logger.info("+++ running profiling with the following parameters: %s", self.params)
        self.mode = Mode.PROFILING
        self.endpoint = self.endpoint_profiler
        self.logger.info("endpoint: %s", self.endpoint)

        self.logger.info("+++ before profiling")
        self.before_profiling()

        self.logger.info("+++ starting profiling")
        self.profile()

        self.logger.info("+++ after profiling")
        self.after_profiling()

    def validate(self):
        self.validation_data.clear()

        self.logger.info("+++ validating the model with %d validation requests", len(self.validation_data))
        self.mode = Mode.PROFILING
        self.endpoint = self.endpoint_profiler
        self.logger.info("endpoint: %s", self.endpoint)

        self.logger.info("+++ before validate")
        self.before_validate()

        for data in self.validation_data:
            self.show_data(data["data"])
            response = self.post_request(data["request"])
            self.show_response(response.json())

        self.logger.info("after validate")
        self.after_validate()
