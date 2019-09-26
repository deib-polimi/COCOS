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
        self.validation_data = []
        self.responses = []
        self.avg_times = []

        # load parameters
        self.params = None
        self.load_parameters(params_file)
        self.endpoint = self.params["serving_host"] + "/v1/models/" + self.model + ":predict"
        if "bench_folder" in self.params.keys():
            self.bench_folder = self.params["bench_folder"] + "/" + self.model + "/"
        else:
            self.bench_folder = "bench_data/" + self.model + "/"
        if "validation_folder" in self.params.keys():
            self.validation_folder = self.params["validation_folder"] + "/" + self.model + "/"
        else:
            self.validation_folder = "validation_data/" + self.model + "/"
        self.repeat_measure = self.params["repeat_measure"] if "repeat_measure" in self.params.keys() else 5
        self.warm_up_reqs = self.params["warm_up_reqs"] if "warm_up_reqs" in self.params.keys() else 5

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
        self.logger.info("warm up ended")

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
                response = self.post_request(data["request"])
                self.responses.append(response)
                times.append(response.elapsed.total_seconds())
            avg_time = stat.mean(times)
            self.avg_times.append(float(avg_time))

    def run(self):
        self.logger.info("Running profiling with the following parameters: %s", self.params)
        self.logger.info("before profiling")
        self.before_profiling()
        self.logger.info("profiling")
        self.profile()
        self.logger.info("after profiling")
        self.after_profiling()

    def validate(self):
        self.logger.info("before validate")
        self.before_validate()

        self.logger.info("validating the model with %d validation requests", len(self.validation_data))
        for image in self.validation_data:
            self.show_data(image["data"])
            response = self.post_request(image["request"])
            self.show_response(response.json())

        self.logger.info("after validate")
        self.after_validate()
