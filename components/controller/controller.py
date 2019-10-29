import datetime
import time

import requests
import logging
import math
from models.model import Model
from models.container import Container
from models.req import Req


class Controller:
    A1_NOM = 0.1963
    A2_NOM = 0.002
    A3_NOM = 0.5658
    P_NOM = 0.4

    def __init__(self,
                 models_endpoint: str,
                 containers_endpoint: str,
                 requests_endpoint: str,
                 window_time: float,
                 min_c: int,
                 max_c: int):
        self.models_endpoint = models_endpoint
        self.containers_endpoint = containers_endpoint
        self.requests_endpoint = requests_endpoint
        self.window_time = window_time

        # min and max core allocation
        self.min_c = min_c
        self.max_c = max_c

        self.models = {}
        self.ui_old = {}
        self.containers = []

        self.logs = []

    def init(self):
        # get the models
        self.models = {json_model["name"]: Model(json_data=json_model)
                       for json_model in self.get_data(self.models_endpoint)}
        self.ui_old = {model: 0.0 for model in list(self.models.keys())}
        log_str = "Loaded " + str(len(self.models)) + " models: " + str(
            [model for model in self.models])
        self.logs.append({"ts": time.time(), "date": str(datetime.datetime.now()), "msg": log_str})

        # get the containers
        self.containers = [Container(json_data=json_container)
                           for json_container in self.get_data(self.containers_endpoint)]
        log_str = "Loaded " + str(len(self.containers)) + " containers: " + str(
            [container.to_json() for container in self.containers])
        self.logs.append({"ts": time.time(), "date": str(datetime.datetime.now()), "msg": log_str})

    def update(self):
        # get the metrics data since from_ts
        from_ts = time.time() - self.window_time
        metrics = self.get_data(self.requests_endpoint + '/metrics/model', {'from_ts': from_ts})
        log_str = "Got {} metrics from {}".format(len(metrics), str(datetime.datetime.fromtimestamp(from_ts)))
        self.logs.append({"ts": time.time(), "date": str(datetime.datetime.now()), "msg": log_str})

        for metric in metrics:
            # get response time for the model
            rt = metric["metrics"]["avg"]
            reqs_number = metric["metrics"]["created"]

            # apply control given models and containers
            log_str = 'Applying control for model: {}<br/>' \
                      'current_avg_rt: {}<br/>current_created_num_reqs: {}'.format(metric["model"],
                                                                   rt,
                                                                   reqs_number)

            # check that some metrics exists
            if rt is None or reqs_number is None:
                log_str = log_str + "<br>Skip {}: model metrics not found".format(metric["model"])
                self.logs.append({"ts": time.time(), "date": str(datetime.datetime.now()), "msg": log_str})
                continue

            # get model data
            model = self.models[metric["model"]]
            if not model:
                log_str = log_str + "<br>Skip {}: model data not found".format(metric["model"])
                self.logs.append({"ts": time.time(), "date": str(datetime.datetime.now()), "msg": log_str})
                continue

            sla = model.sla
            alpha = model.alpha
            ui_old = self.ui_old[model.name]

            e = sla - rt
            ke = (alpha - 1) / (self.P_NOM - 1) * e
            ui = ui_old + (1 - self.P_NOM) * ke
            ut = ui + ke

            core = reqs_number * (ut - self.A1_NOM - 1000.0 * self.A2_NOM) / (
                    1000.0 * self.A3_NOM * (self.A1_NOM - ut))

            approx_core = math.ceil(min(self.max_c, max(core, self.min_c)))

            approx_ut = ((1000.0 * self.A2_NOM + self.A1_NOM) * reqs_number +
                         1000.0 * self.A1_NOM * self.A3_NOM * approx_core) / (
                                reqs_number + 1000.0 * self.A3_NOM * approx_core)

            log_str = log_str + "<br>sla: {2:.4f}<br/>" \
                                "error: {3:.4f}<br/>" \
                                "ke: {4:.4f}<br/>" \
                                "ui, ui_old, ut, approx_ut: {5:.4f} {6:.4f} {7:.4f} {8:.4f}<br/>" \
                                "core, approx_core: {9:.4f} {10:.4f}".format(
                rt, reqs_number, sla, e, ke, ui, ui_old, ut, approx_ut, core, approx_core)

            self.ui_old[model.name] = approx_ut - ke

            allocation = approx_core

            # update containers
            log_str = log_str + "<br>Model {}: allocation: {}, updating containers...".format(model.name, allocation)
            self.logs.append({"ts": time.time(), "date": str(datetime.datetime.now()), "msg": log_str})

    def get_logs(self):
        return self.logs

    def get_data(self, url, data=None):
        try:
            response = requests.get(url, params=data)
        except Exception as e:
            logging.warning(e)
            response = []
        return response.json()

    def to_json(self):
        pass
