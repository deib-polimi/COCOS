import json
import logging
import statistics as stat
import requests
import yaml


class Profiler:

    def __init__(self, params_file, model, logger):
        self.model = model

        if logger:
            self.logger = logger
        else:
            self.logger = logging

        self.bench_data = []
        self.avg_times = []

        # load parameters
        self.params = None
        self.load_parameters(params_file)
        self.endpoint = self.params["serving_host"] + "/v1/models/" + self.model + ":predict"
        self.bench_folder = self.params["bench_folder"] if "bench_folder" in self.params.keys() else "bench_data"
        self.repeat_measure = self.params["repeat_measure"] if "repeat_measure" in self.params.keys() else 5
        self.warm_up_reqs = self.params["warm_up_reqs"] if "warm_up_reqs" in self.params.keys() else 5

    def before_profiling(self):
        """
        Abstract
        Executed before profiling is started.
        This is the place where:
        - load the requests data,
        - perform some pre profile works
        - warm up the model, etc.
        """
        pass

    def after_profiling(self):
        """
        Abstract
        Executed after profiling is done.
        This is the place where:
        - save profiling data.
        - elaborate response data,
        - save response, etc.
        """
        pass

    def load_parameters(self, params_file):
        """
        Load parameters from file
        """
        with open(params_file, 'r') as file:
            data = file.read()
            self.params = yaml.load(data, Loader=yaml.FullLoader)

    def load_request_from_file(self):
        """
        Load the requests file from the bench folder
        """
        file_path = self.bench_folder + "/" + self.model + ".json"
        self.logger.info("loading requests from file %s", file_path)
        with open(file_path, 'r') as file:
            self.bench_data = json.load(file)["data"]
            self.logger.info("bench_data: %s", self.bench_data)

    def warm_up_model(self, data):
        """
        Send few request to warm up the model
        """
        self.logger.info("warming up the model %d times", self.warm_up_reqs)
        for _ in range(self.warm_up_reqs):
            response = self.post_request(data)
            logging.info(response.json())

    def post_request(self, json_request):
        response = requests.post(self.endpoint, json=json_request)
        response.raise_for_status()
        return response

    def profile(self):
        self.logger.info("profiling the model %d times per request", self.repeat_measure)
        self.logger.info("profiling the model with %d bench data", len(self.bench_data))
        for data in self.bench_data:
            times = []
            for _ in range(0, self.repeat_measure):
                response = self.post_request(data)
                logging.info(response.json())
                times.append(response.elapsed.total_seconds())
            avg_time = stat.mean(times)
            self.avg_times.append(float(avg_time))

    def run(self):
        self.logger.info("Running profiling with the following parameters: %s", self.params)
        self.logger.info("pre-profiling")
        self.before_profiling()
        self.logger.info("profiling")
        self.profile()
        self.logger.info("post-profiling")
        self.after_profiling()
