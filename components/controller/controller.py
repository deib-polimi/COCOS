import datetime
import time
import requests
import logging
from models.model import Model
from models.container import Container
from models.device import Device


class Controller:
    A1_NOM = 0.1963
    A2_NOM = 0.002
    A3_NOM = 0.5658
    P_NOM = 0.4

    def __init__(self,
                 models_endpoint: str,
                 containers_endpoint: str,
                 requests_endpoint: str,
                 actuator_port: int,
                 window_time: float,
                 min_c: float,
                 max_c: float):
        self.models_endpoint = models_endpoint
        self.containers_endpoint = containers_endpoint
        self.requests_endpoint = requests_endpoint
        self.actuator_port = actuator_port
        self.window_time = window_time

        # min and max core allocation
        self.min_c = min_c
        self.max_c = max_c

        self.models = {}
        self.ui_old = {}
        self.containers = []
        self.containers_by_node = {}

        self.logs = []

    def init(self):
        # get the models
        self.models = {json_model["name"]: Model(json_data=json_model)
                       for json_model in self.get_data(self.models_endpoint)}
        self.ui_old = {model: 0.0 for model in list(self.models.keys())}
        log_str = "Loaded " + str(len(self.models)) + " models: " + str(
            [model for model in self.models])
        self.logs.append({"ts": time.time(), "date": str(datetime.datetime.now()), "msg": log_str})

        # get the containers by node
        self.containers = [Container(json_data=json_container)
                           for json_container in self.get_data(self.containers_endpoint)]

        # filter CPUs containers
        cpus_containers = list(filter(lambda c: c.device == Device.CPU, self.containers))
        # init ui_old
        self.ui_old = {container.container_id: 0 for container in cpus_containers}
        # group containers by nodes
        nodes = set(map(lambda c: c.node, cpus_containers))
        self.containers_by_node = {}
        for node in nodes:
            self.containers_by_node[node] = list(filter(lambda c: c.node == node, cpus_containers))
        log_str = "Containers by node: " + str(
            [{node: [c.to_json() for c in self.containers_by_node[node]]} for node in self.containers_by_node])
        self.logs.append({"ts": time.time(), "date": str(datetime.datetime.now()), "msg": log_str})

    def update(self):
        # get the metrics data since from_ts
        from_ts = time.time() - self.window_time
        metrics_data = self.get_data(self.requests_endpoint + '/metrics/container', {'from_ts': from_ts})
        metrics = {m["container"]["container_id"]: m["metrics_from_ts"] for m in metrics_data}
        log_str = "Got {} metrics from {}".format(len(metrics), str(datetime.datetime.fromtimestamp(from_ts)))
        # log_str = "Metrics: {}".format(metrics_data)

        for node in self.containers_by_node:
            allocation = {}
            total_allocation = 0
            log_str += "<br/>Working on node: {}<br/>".format(node)

            for container in self.containers_by_node[node]:
                # get response time for the model from ts
                rt = metrics[container.container_id]["avg"]
                # get requests number for the model
                reqs_number = metrics[container.container_id]["created"] + metrics[container.container_id]["completed"]

                # apply control given models and containers
                log_str += '<br/><strong>Applying control for model: {}</strong><br/>' \
                           'container: {:.12}<br/>' \
                           'current_avg_rt: {}<br/>' \
                           'current_created_num_reqs: {}'.format(container.model,
                                                                 container.container_id,
                                                                 rt,
                                                                 reqs_number)

                # check that some metrics exists
                if rt is None or reqs_number is None:
                    log_str = log_str + "<br/>Skip: container metrics not found"
                    continue

                # get model data
                model = self.models[container.model]
                if not model:
                    log_str += "<br/>Skip: model data not found"
                    continue

                # compute num cores
                rt = float(rt)
                reqs_number = float(reqs_number)
                sla = float(model.sla)
                alpha = 0.95  # model.alpha
                ui_old = float(self.ui_old[container.container_id])

                e = float(sla - rt)
                ke = float((alpha - 1) / (self.P_NOM - 1) * e)
                ui = float(ui_old + (1 - self.P_NOM) * ke)
                ut = float(ui + ke)

                core = float(
                    reqs_number * (ut - self.A1_NOM - 1000.0 * self.A2_NOM) / (
                            1000.0 * self.A3_NOM * (self.A1_NOM - ut)))

                approx_core = float((min(self.max_c, max(core, self.min_c))))

                approx_ut = float(((1000.0 * self.A2_NOM + self.A1_NOM) * reqs_number +
                                   1000.0 * self.A1_NOM * self.A3_NOM * approx_core) / (
                                          reqs_number + 1000.0 * self.A3_NOM * approx_core))

                log_str += "<br/>sla: {0:.4f}<br/>" \
                           "error: {1:.4f}<br/>" \
                           "ke: {2:.4f}<br/>" \
                           "ui, ui_old, ut, approx_ut: {3:.4f}, {4:.4f}, {5:.4f}, {6:.4f}<br/>" \
                           "core, approx_core: {7:.4f}, {8:.4f}".format(sla, e, ke, ui, ui_old, ut, approx_ut, core,
                                                                        approx_core)

                self.ui_old[container.container_id] = float(approx_ut - ke)

                allocation[container.container_id] = approx_core
                total_allocation += approx_core

            if total_allocation > 0:
                log_str += "<br/><br/>Total cores: {:.2f} / {}".format(total_allocation, self.max_c)

            if total_allocation > self.max_c:
                # normalize
                log_str += "<br/>Normalizing..."
                for container in allocation:
                    if allocation[container] != 0:
                        allocation[container] = self.max_c / allocation[container]

            for container in allocation:
                # update container by node
                log_str += "<br/><strong>Updating container: {:.12}</strong>, " \
                           "new allocation {:.2f} / {}".format(container,
                                                               allocation[container],
                                                               self.max_c)
                # post to actuator
                response = requests.post("http://" + node + ":" + str(self.actuator_port) + "/containers/" + container,
                                         json={"cpu_quota": int(allocation[container] * 100000)})
                log_str += "<br/>actuator response: {}".format(response.text)
                # post con containers_manager
                response = requests.patch(self.containers_endpoint,
                                          json={"container_id": container,
                                                "cpu_quota": int(allocation[container] * 100000)})
                log_str += "<br/>cm response: {}".format(response.text)

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
