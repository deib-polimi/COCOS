import concurrent
from concurrent.futures import ThreadPoolExecutor
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
import pickle
from .models.req import Req, ReqState
from .models.model import Model
from apscheduler.schedulers.background import BackgroundScheduler
import multiprocessing


class BenchmarkStrategies(IntEnum):
    SERVER = 0
    VARIABLE_SLA = 1
    VARIABLE_LOAD = 2
    VARIABLE_REQS = 3


class Mode(IntEnum):
    BENCHMARK = 0
    PROFILING = 1


class Benchmark:

    def __init__(self, params_file, model, version, benchmark_strategy, logger, output_file=None):
        if logger:
            self.logger = logger
        else:
            self.logger = logging

        self.bench_data = []
        self.validation_data = []
        self.responses = []
        self.profiling_rt = []
        self.profiling_rt_avg = []

        self.mode = None

        # load parameters
        self.params = None
        self.load_parameters(params_file)

        # set benchmark strategy
        self.benchmark_strategy = benchmark_strategy
        self.requests_ids = []

        self.benchmark_running = False
        self.benchmark_rt = []
        self.benchmark_rt_process = []
        self.benchmark_req = []
        self.benchmark_reqs_s = 0
        self.benchmark_sent_reqs = []
        self.benchmark_sent = []
        self.benchmark_model_sla = []
        self.benchmark_data_i = 0
        self.benchmark_updates_count = 0
        self.benchmark_updates_count_max = 0
        self.benchmark_scheduler = None
        self.benchmark_result_file = self.params.get("benchmark_result_file", None)
        self.profiling_result_file = self.params.get("profiling_result_file", None)
        self.benchmark_containers = []
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
            self.bench_folder = self.params["bench_folder"] + "/"
        else:
            self.bench_folder = "bench_folder/" + self.model.name + "/"
        if "validation_folder" in self.params.keys():
            self.validation_folder = self.params["validation_folder"] + "/"
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
        self.logger.info("avg rt process %s", self.benchmark_rt_process)
        self.logger.info("req %s", self.benchmark_req)
        self.logger.info("reqs sent %s", self.benchmark_sent)
        self.logger.info("model sla %s", self.benchmark_model_sla)
        self.logger.info("containers %s", self.benchmark_containers)

        plt.plot(x_val, self.benchmark_rt, '--', label="avg RT")
        plt.title("avg RT")
        plt.show()
        plt.plot(x_val, self.benchmark_rt_process, '--', label="avg RT process")
        plt.title("avg RT process")
        plt.show()
        plt.plot(x_val, self.benchmark_req, label="# reqs")
        plt.title("# reqs")
        plt.show()
        plt.plot(x_val, self.benchmark_sent, label="# req sent")
        plt.title("# reqs sent")
        plt.show()
        plt.plot(x_val, self.benchmark_model_sla, label="Model SLA")
        plt.title("model SLA")
        plt.show()

    def save_results_benchmark(self):
        if self.benchmark_result_file is not None:
            self.logger.info("Saving to file...")
            benchmark_data = [self.benchmark_rt, self.benchmark_rt_process, self.benchmark_req, self.benchmark_sent,
                              self.benchmark_model_sla,
                              self.benchmark_containers]
            with open(self.benchmark_result_file + self.model.name + ".out", 'wb') as f:
                pickle.dump(benchmark_data, f)
            self.logger.info("Saved")

    def sampler(self):
        old_sent = []
        for i in range(len(self.bench_data)):
            old_sent.append(0)
        while self.benchmark_running:
            from_ts = time.time() - self.sample_frequency
            metrics = self.get_data(self.requests_store + '/metrics/model', {'from_ts': from_ts}).json()
            for metric in metrics:
                if metric["model"] == self.model.name:
                    self.benchmark_rt.append(metric["metrics_from_ts"]["avg"])
                    self.benchmark_rt_process.append(metric["metrics_from_ts"]["avg_process"])
                    self.benchmark_req.append(
                        metric["metrics_from_ts"]["created"] + metric["metrics_from_ts"]["completed"])
            sent_list = []
            for i in range(len(self.bench_data)):
                sent_list.append(self.benchmark_sent_reqs[i] - old_sent[i])
                old_sent[i] = self.benchmark_sent_reqs[i]
            self.benchmark_sent.append(sent_list)
            self.benchmark_model_sla.append(self.model.sla)
            self.benchmark_containers.append(self.get_data(self.containers_manager + '/models/' +
                                                           self.model.name + '/containers'))
            time.sleep(self.sample_frequency)

    def benchmark_update(self):
        self.logger.info("updating benchmark conditions...")

        if self.benchmark_strategy == BenchmarkStrategies.VARIABLE_SLA:
            sla_increment = self.params["variable_sla"]["increment"][self.benchmark_updates_count - 1]

            # update model sla
            self.logger.info("updating model SLA by %.4f, from %.4f, to %.4f...",
                             sla_increment, self.model.sla, float(self.model.sla + sla_increment))
            response = self.patch_data(self.containers_manager + "/models",
                                       {"model": self.model.name,
                                        "sla": float(self.model.sla + sla_increment)})
            self.logger.info(response.text)
            self.model.sla += sla_increment

        elif self.benchmark_strategy == BenchmarkStrategies.VARIABLE_LOAD:
            # update data
            self.benchmark_data_i += 1
            self.logger.info("load updated")

        elif self.benchmark_strategy == BenchmarkStrategies.VARIABLE_REQS:
            # update reqs/s
            reqs_s_increment = self.params["variable_reqs"]["increment"][self.benchmark_updates_count - 1]
            self.logger.info("updating reqs/s by %d, from %d, to %d...",
                             reqs_s_increment, self.benchmark_reqs_s, float(self.benchmark_reqs_s + reqs_s_increment))
            self.benchmark_reqs_s += reqs_s_increment

        self.benchmark_updates_count += 1
        if self.benchmark_updates_count > self.benchmark_updates_count_max:
            self.benchmark_scheduler.remove_job('benchmark_update')

    def benchmark_sender(self, reqs_queue):
        self.logger.info("benchmark sender started...")
        while self.benchmark_running:
            req = reqs_queue.get()
            if req is None:
                self.logger.info("benchmark sender finished...")
                break
            self.post_request(req)

    def benchmark(self):
        self.logger.info("using strategy %s", self.benchmark_strategy)
        self.logger.info("profiling the model %s with %d bench data", self.model.name, len(self.bench_data))
        if self.benchmark_strategy == BenchmarkStrategies.SERVER:
            self.benchmark_data_i = 0
            mu = self.params["server"]["mu"]
            sigma = self.params["server"]["sigma"]
            reqs_per_s = self.params["server"]["reqs_per_s"]
            duration = self.params["server"]["duration"]
            for i in range(len(self.bench_data)):
                self.benchmark_sent_reqs.append(0)

            # start the sample thread: measure metrics every t time
            self.benchmark_running = True
            self.benchmark_rt.clear()
            self.benchmark_req.clear()
            sampler_thread = threading.Thread(target=self.sampler)
            sampler_thread.start()

            end_t = time.time() + duration
            while end_t - time.time() > 0:
                self.logger.info("\tremaining: %.2f s", end_t - time.time())
                self.logger.info("sending %d reqs", reqs_per_s)

                # send the reqs
                time_start_send = time.time()
                for _ in range(0, reqs_per_s):
                    data = self.bench_data[self.benchmark_data_i]
                    response = self.post_request(data["request"])
                    self.responses.append(response)
                    self.requests_ids.append(response.json()["id"])
                    self.benchmark_data_i = (self.benchmark_data_i + 1) % len(self.bench_data)
                    self.benchmark_sent_reqs[self.benchmark_data_i] += 1

                # sleep for sleep_t seconds got from a Normal distribution
                sleep_t = 0
                while sleep_t <= 0:
                    sleep_t = float(np.random.normal(mu, sigma, 1))
                self.logger.info("waiting %.4f s", sleep_t)
                time_sending = time.time() - time_start_send
                time.sleep(sleep_t - time_sending)

            self.benchmark_running = False
            time.sleep(self.sample_frequency)

        elif self.benchmark_strategy == BenchmarkStrategies.VARIABLE_SLA or \
                self.benchmark_strategy == BenchmarkStrategies.VARIABLE_LOAD or \
                self.benchmark_strategy == BenchmarkStrategies.VARIABLE_REQS:
            self.logger.info("GPUs containers should be disabled")

            duration = 0
            updates = 1
            # get benchmark parameters
            if self.benchmark_strategy == BenchmarkStrategies.VARIABLE_SLA:
                self.benchmark_reqs_s = self.params["variable_sla"]["reqs_per_s"]
                duration = self.params["variable_sla"]["duration"]
                updates = len(self.params["variable_sla"]["increment"])
            elif self.benchmark_strategy == BenchmarkStrategies.VARIABLE_LOAD:
                self.benchmark_reqs_s = self.params["variable_load"]["reqs_per_s"]
                duration = self.params["variable_load"]["duration"]
                updates = len(self.params["variable_load"]["increment"])
            elif self.benchmark_strategy == BenchmarkStrategies.VARIABLE_REQS:
                self.benchmark_reqs_s = self.params["variable_reqs"]["reqs_per_s"]
                duration = self.params["variable_reqs"]["duration"]
                updates = len(self.params["variable_reqs"]["increment"])

            for i in range(len(self.bench_data)):
                self.benchmark_sent_reqs.append(0)

            # start the sample thread: measure metrics every t time
            self.benchmark_running = True
            self.benchmark_rt.clear()
            self.benchmark_req.clear()
            self.benchmark_updates_count = 1
            self.benchmark_updates_count_max = updates
            sampler_thread = threading.Thread(target=self.sampler)

            # creating processes
            reqs_queue = multiprocessing.Queue()
            num_proc = 30
            processes = []
            for w in range(num_proc):
                p = multiprocessing.Process(target=self.benchmark_sender, args=(reqs_queue,))
                processes.append(p)
                p.start()

            # start the updater
            self.benchmark_scheduler = BackgroundScheduler()
            self.benchmark_scheduler.add_job(self.benchmark_update, 'interval', seconds=duration / (updates + 1),
                                             id='benchmark_update')
            self.benchmark_scheduler.start()

            self.benchmark_data_i = 0
            model_sla_start = self.model.sla
            end_t = time.time() + duration
            sampler_thread.start()
            while end_t - time.time() > 0:
                self.logger.info("\tremaining: %.2f s", end_t - time.time())
                self.logger.info("sending %d reqs", self.benchmark_reqs_s)

                # send the reqs
                time_start_send = time.time()
                data = self.bench_data[self.benchmark_data_i]
                for _ in range(0, self.benchmark_reqs_s):
                    reqs_queue.put(data["request"])
                    self.benchmark_sent_reqs[self.benchmark_data_i] += 1
                time_sending = time.time() - time_start_send

                sleep_t = 1
                self.logger.info("waiting %.4f s, time sending %.4f s", sleep_t, time_sending)
                if sleep_t - time_sending > 0:
                    time.sleep(sleep_t - time_sending)

            self.benchmark_running = False
            # stop process
            for i in range(num_proc):
                reqs_queue.put(None)
            # completing process
            for p in processes:
                p.join()
            time.sleep(self.sample_frequency)


            # reset the system to the original state
            if self.benchmark_strategy == BenchmarkStrategies.VARIABLE_SLA:
                # reset model sla
                self.logger.info("Resetting model SLA to %.4f", model_sla_start)
                response = self.patch_data(self.containers_manager + "/models", {"model": self.model.name,
                                                                                 "sla": float(model_sla_start)})
                self.logger.info(response.text)

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

        self.logger.info("+++ saving results benchmark")
        self.save_results_benchmark()

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

    def send_data_profile(self):
        for data in self.bench_data:
            times = []
            for _ in range(0, self.repeat_measure):
                start_t = time.time()
                response = self.post_request(data["request"])
                end_t = time.time()
                self.responses.append(response)
                rt = end_t - start_t
                times.append(rt)
            self.profiling_rt.append(times)
            avg_time = stat.mean(times)
            self.profiling_rt_avg.append(float(avg_time))

    def profile(self):
        self.logger.info("profiling the model %d times per request", self.repeat_measure)
        self.logger.info("profiling the model with %d bench data", len(self.bench_data))
        self.logger.info("profiling with %d concurrent requests", self.params["concurrent_requests"])
        threads_pool = ThreadPoolExecutor(max_workers=self.params["concurrent_requests"])
        tp = []
        for i in range(self.params["concurrent_requests"]):
            tp.append(threads_pool.submit(self.send_data_profile))
        concurrent.futures.wait(tp)

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

        self.logger.info("+++ save results profiling")
        self.save_results_profiling()

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

    def save_results_profiling(self):
        if self.profiling_result_file is not None:
            self.logger.info("Saving to file...")
            profiling_data = [self.profiling_rt]
            with open(self.profiling_result_file + self.model.name + ".out", 'wb') as f:
                pickle.dump(profiling_data, f)
            self.logger.info("Saved")
