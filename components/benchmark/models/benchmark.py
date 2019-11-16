import json
import logging
import threading
import time
import requests
import yaml
import statistics as stat
import numpy as np
from enum import IntEnum
import matplotlib.pyplot as plt
from .models.req import Req, ReqState
from .models.model import Model


class BenchmarkStrategies(IntEnum):
    SINGLE_STREAM = 0
    SERVER = 1
    VARIABLE_SLA = 2
    VARIABLE_LOAD = 3


class Mode(IntEnum):
    BENCHMARK = 0
    PROFILING = 1


class Benchmark:

    def __init__(self, params_file, model, version, benchmark_strategy, logger):
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

        # set benchmark strategy
        self.benchmark_strategy = benchmark_strategy
        self.requests_ids = []

        self.benchmark_running = False
        self.benchmark_rt = []
        self.benchmark_req = []
        self.sample_frequency = self.params["sample_frequency"]

        # endpoints
        self.requests_store = self.params["requests_store"]
        self.containers_manager = self.params["containers_manager"]

        # get model data
        self.model = Model(json_data=self.get_data(self.containers_manager + "/models/" + model).json())
        self.logger.info(self.model.to_json())
        self.version = version

        # endpoints
        if "endpoint_profiler" in self.params.keys():
            self.endpoint_profiler = self.params["endpoint_profiler"] + "/v1/models/" + self.model.name + ":predict"
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
            self.bench_folder = self.params["bench_folder"] + "/" + self.model.name + "/"
        else:
            self.bench_folder = "bench_folder/" + self.model.name + "/"
        if "validation_folder" in self.params.keys():
            self.validation_folder = self.params["validation_folder"] + "/" + self.model.name + "/"
        else:
            self.validation_folder = "validation_data/" + self.model.name + "/"
        self.warm_up_reqs = self.params.get("warm_up_times", 5)
        self.repeat_measure = self.params.get("repeat_measure", 5)

    def prepare_request(self, instances):
        if self.mode == Mode.PROFILING:
            request = {"instances": instances}
        else:  # self.mode == Mode.BENCHMARK:
            request = {"model": self.model.name, "version": self.version, "instances": instances}
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
        file_path = self.bench_folder + self.model.name + ".json"
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
        self.logger.info(self.endpoint, json_request)
        response = requests.post(self.endpoint, json=json_request)
        response.raise_for_status()
        return response

    def get_data(self, url, data=None):
        try:
            response = requests.get(url, params=data)
            response.raise_for_status()
        except Exception as e:
            logging.warning(e)
            response = []
        return response

    def patch_data(self, url, data=None):
        try:
            response = requests.patch(url, json=data)
            response.raise_for_status()
        except Exception as e:
            logging.warning(e)
            response = []
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
        x_val = np.arange(len(self.benchmark_rt))
        self.logger.info("avg rt %s", self.benchmark_rt)
        self.logger.info("req %s", self.benchmark_req)
        plt.plot(x_val, self.benchmark_rt, '--', label="AVG RT")
        plt.show()
        plt.plot(x_val, self.benchmark_req, label="#REQ")
        plt.show()

    def sampler(self):
        while self.benchmark_running:
            time.sleep(self.sample_frequency)
            from_ts = time.time() - self.sample_frequency
            metrics = self.get_data(self.requests_store + '/metrics/model', {'from_ts': from_ts}).json()
            for metric in metrics:
                if metric["model"] == self.model.name:
                    self.benchmark_rt.append(metric["metrics_from_ts"]["avg"])
                    self.benchmark_req.append(
                        metric["metrics_from_ts"]["created"] + metric["metrics_from_ts"]["completed"])

    def benchmark(self):
        self.logger.info("using strategy %s", self.benchmark_strategy)
        self.logger.info("profiling the model %s with %d bench data", self.model.name, len(self.bench_data))
        if self.benchmark_strategy == BenchmarkStrategies.SINGLE_STREAM:
            i = 0
            for _ in range(0, self.repeat_measure):
                data = self.bench_data[i]
                response = self.post_request(data["request"])
                self.responses.append(response)
                self.requests_ids.append(response.json()["id"])
                i = (i + 1) % len(self.bench_data)
        elif self.benchmark_strategy == BenchmarkStrategies.SERVER:
            i = 0
            mu = self.params["server"]["mu"]
            sigma = self.params["server"]["sigma"]
            reqs_per_s = self.params["server"]["reqs_per_s"]
            duration = self.params["server"]["duration"]

            # start the sample thread: measure metrics every t time
            self.benchmark_running = True
            self.benchmark_rt.clear()
            self.benchmark_req.clear()
            sampler_thread = threading.Thread(target=self.sampler)
            sampler_thread.start()

            end_t = time.time() + duration
            while end_t - time.time() > 0:
                self.logger.info("\tremaining: %.2f s", end_t - time.time())

                # sleep for sleep_t seconds got from a Normal distribution
                sleep_t = 0
                while sleep_t <= 0:
                    sleep_t = np.random.normal(mu, sigma, 1)
                self.logger.info("waiting %.4f s", sleep_t)
                time.sleep(sleep_t)

                self.logger.info("sending %d reqs", reqs_per_s)
                # send the reqs
                for _ in range(0, reqs_per_s):
                    data = self.bench_data[i]
                    response = self.post_request(data["request"])
                    self.responses.append(response)
                    self.requests_ids.append(response.json()["id"])
                    i = (i + 1) % len(self.bench_data)

            self.benchmark_running = False
            time.sleep(self.sample_frequency)

        elif self.benchmark_strategy == BenchmarkStrategies.VARIABLE_SLA or self.benchmark_strategy == BenchmarkStrategies.VARIABLE_LOAD:
            self.logger.info("GPUs containers should be disabled")

            duration = reqs_per_s = sla_increment = 0
            # get benchmark parameters
            if self.benchmark_strategy == BenchmarkStrategies.VARIABLE_SLA:
                reqs_per_s = self.params["variable_sla"]["reqs_per_s"]
                duration = self.params["variable_sla"]["duration"]
                sla_increment = self.params["variable_sla"]["increment"]
            elif self.benchmark_strategy == BenchmarkStrategies.VARIABLE_LOAD:
                reqs_per_s = self.params["variable_sla"]["reqs_per_s"]
                duration = self.params["variable_sla"]["duration"]

            # start the sample thread: measure metrics every t time
            self.benchmark_running = True
            self.benchmark_rt.clear()
            self.benchmark_req.clear()
            sampler_thread = threading.Thread(target=self.sampler)
            sampler_thread.start()

            data_i = 0
            sent_reqs = 0
            switched = False
            end_t = time.time() + duration
            tot_reqs = duration * reqs_per_s
            while end_t - time.time() > 0:
                self.logger.info("\tremaining: %.2f s", end_t - time.time())

                sleep_t = 1
                self.logger.info("waiting %.4f s", sleep_t)
                time.sleep(sleep_t)

                self.logger.info("sending %d reqs", reqs_per_s)
                # send the reqs
                for _ in range(0, reqs_per_s):
                    # use just one sample
                    data = self.bench_data[data_i]
                    response = self.post_request(data["request"])
                    self.responses.append(response)
                    self.requests_ids.append(response.json()["id"])
                    sent_reqs += 1

                if sent_reqs > tot_reqs / 2:
                    if self.benchmark_strategy == BenchmarkStrategies.VARIABLE_SLA and not switched:
                        switched = True
                        # update model sla
                        self.logger.info("Updating model SLA...")
                        response = self.patch_data(self.containers_manager + "/models", {"model": self.model.name,
                                                                                         "sla": self.model.sla +
                                                                                                sla_increment})
                        self.logger.info(response.text)
                    elif self.benchmark_strategy == BenchmarkStrategies.VARIABLE_LOAD and not switched:
                        switched = True
                        # update data
                        data_i += 1
                        self.logger.info("Load updated")

            self.benchmark_running = False
            time.sleep(self.sample_frequency)

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
