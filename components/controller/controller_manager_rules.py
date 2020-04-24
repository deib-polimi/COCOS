import datetime
import math
import time
import requests
import logging
from models.model import Model
from models.container import Container
from models.device import Device
from models.controller import Controller


class ControllerManagerRules:
    SCALE_OUT_THRESHOLD = 0.80
    SCALE_IN_THRESHOLD = 0.20

    def __init__(self,
                 models_endpoint: str,
                 containers_endpoint: str,
                 requests_endpoint: str,
                 actuator_port: int,
                 window_time: float,
                 min_c: float,
                 max_c: float,
                 cooldown: float = 60,
                 step: int = 1):

        self.models_endpoint = models_endpoint
        self.containers_endpoint = containers_endpoint
        self.requests_endpoint = requests_endpoint
        self.actuator_port = actuator_port
        self.window_time = window_time

        # min and max core allocation
        self.min_c = min_c
        self.max_c = max_c

        self.cooldown = cooldown
        self.step = step

        self.models = {}
        self.nodes = ()
        self.containers = []
        self.containers_on_node = {}

        self.logs = []

        self.controllers = {}

    def init(self):
        # get the models
        self.models = {json_model["name"]: Model(json_data=json_model)
                       for json_model in self.get_data(self.models_endpoint)}
        log_str = "Loaded " + str(len(self.models)) + " models: " + str(
            [model.name for model in self.models.values()])
        self.logs.append({"ts": time.time(), "date": str(
            datetime.datetime.now()), "msg": log_str})

        # get the containers
        self.containers = [Container(json_data=json_container)
                           for json_container in self.get_data(self.containers_endpoint)]

        # group containers by nodes
        self.nodes = set(map(lambda c: c.node, self.containers))
        self.containers_on_node = {}
        for node in self.nodes:
            self.containers_on_node[node] = list(
                filter(lambda c: c.node == node, self.containers))
        log_str = "Containers by node: " + str(
            [{node: [c.to_json() for c in self.containers_on_node[node]]} for node in self.containers_on_node])
        self.logs.append({"ts": time.time(), "date": str(
            datetime.datetime.now()), "msg": log_str})

        # init controllers
        self.controllers = []
        t = time.time()
        for container in list(filter(lambda c: c.device == Device.CPU and c.active, self.containers)):
            c = Controller(container)
            c.nextAction = t
            self.controllers.append(c)

    def mean(self, list):
        num_val = 0
        tot = 0
        for v in list:
            if v is not None:
                num_val += 1
                tot += v

        if tot == 0:
            return None
        else:
            return tot / num_val

    def float_round(self, num, places=0, direction=math.ceil):
        return direction(num * (10 ** places)) / float(10 ** places)

    def update(self):
        if self.nextAction > time.time():
            return

        # update the models data
        self.models = {json_model["name"]: Model(json_data=json_model)
                       for json_model in self.get_data(self.models_endpoint)}
        gpu_containers = list(
            filter(lambda c: c.device == Device.GPU, self.containers))

        # get the metrics data since from_ts
        from_ts = time.time() - self.window_time
        metrics = self.get_data(
            self.requests_endpoint + '/metrics/container/model', {'from_ts': from_ts})

        log_str = "Got {} metrics from {}".format(
            len(metrics), str(datetime.datetime.fromtimestamp(from_ts)))

        for node in self.nodes:
            controller_for_node = list(
                filter(lambda c: c.container.node == node, self.controllers))
            log_str += "<br/><strong>node: {}</strong>".format(node)

            for controller in controller_for_node:

                # compute the requests completed
                cpu_containers = list(
                    filter(lambda c: c.device == Device.CPU and c.model == controller.container.model,
                           self.containers_on_node[controller.container.node]))

                reqs_gpus = []
                reqs_cpus = []
                for gpu_container in gpu_containers:
                    reqs_gpus.append(
                        metrics[gpu_container.container_id][controller.container.model])
                for cpu_container in cpu_containers:
                    # there should be only one container for CPU for a model
                    reqs_cpus.append(
                        metrics[cpu_container.container_id][controller.container.model])

                reqs_created_gpus = sum(map(lambda m: m["created"], reqs_gpus))
                reqs_created_cpus = sum(map(lambda m: m["created"], reqs_cpus))
                reqs_completed_gpus = sum(
                    map(lambda m: m["completed"], reqs_gpus))
                reqs_completed_cpus = sum(
                    map(lambda m: m["completed"], reqs_cpus))
                reqs_rt_gpus = self.mean(map(lambda m: m["avg"], reqs_gpus))
                reqs_rt_cpus = self.mean(map(lambda m: m["avg"], reqs_cpus))

                # rule-based control
                tot_reqs = max(1, reqs_completed_gpus + reqs_completed_cpus)
                gpu_share = reqs_completed_gpus/tot_reqs
                cpu_share = reqs_completed_cpus/tot_reqs

                controller.rt_sla = self.models[controller.container.model].sla
                controller.rt_cpu = reqs_rt_cpus
                controller.rt_gpu = reqs_rt_gpus
                controller.rt_all = reqs_rt_gpus*gpu_share + reqs_rt_cpus*cpu_share

                t = time.time()
                oldNc = controller.nc

                if t > controller.nextAction:
                    if controller.rt_all > controller.rt_sla*SCALE_OUT_THRESHOLD:
                        controller.nc = min(
                            controller.nc + self.step, self.max_c)
                    elif controller.rt_all < controller.rt_sla*SCALE_IN_THRESHOLD:
                        controller.nc = max(
                            controller.nc - self.step, self.min_c)
                    else:
                        # safe assignment for wrong initial values
                        controller.nc = min(
                            max(controller.nc, self.min_c), self.max_c)

                if oldNc != controller.nc:
                    controller.nextAction = t + self.cooldown

                # log
                log_str += '<br/><strong>model: {}, {} GPU containers, {} CPU containers</strong>' \
                           '<br/>sla: {}' \
                           '<br/>reqs completed: GPU: {}, CPU {} | ' \
                           'created: GPU: {}, CPU {}' \
                           '<br/>reqs rt: GPU: {:.4f}, CPU: {:.4f}'.format(controller.container.model,
                                                                           len(gpu_containers),
                                                                           len(cpu_containers),
                                                                           self.models[controller.container.model].sla,
                                                                           reqs_completed_gpus,
                                                                           reqs_completed_cpus,
                                                                           reqs_created_gpus,
                                                                           reqs_created_cpus,
                                                                           reqs_rt_gpus if reqs_rt_gpus is not None else 0,
                                                                           reqs_rt_cpus if reqs_rt_cpus is not None else 0)

            tot_reqs_cores = sum(map(lambda c: c.nc, controller_for_node))
            log_str += "<br/>cores before norm: {:.2f} / {}<br/>".format(
                tot_reqs_cores, self.max_c)
            if tot_reqs_cores > self.max_c:
                # norm
                for controller in controller_for_node:
                    controller.nc = self.float_round(
                        (controller.nc * self.max_c / tot_reqs_cores), 1)

            # log controllers
            for controller in controller_for_node:
                log_str += "controller for {}:<ul>" \
                           "<li>cores: {:.2f}</li>" \
                           "<li>rt_sla: {:.2f}</li>" \
                           "<li>rt_gpu: {:.2f}</li>" \
                           "<li>rt_cpu: {:.2f}</li>" \
                           "</ul>".format(controller.container.model,
                                          controller.nc,
                                          controller.rt_sla,
                                          controller.rt_gpu,
                                          controller.rt_cpu)
            tot_reqs_cores = sum(map(lambda c: c.nc, controller_for_node))
            log_str += "<strong>total cores: {:.2f} / {}</strong>".format(
                tot_reqs_cores, self.max_c)

            # actuate
            for controller in controller_for_node:
                # update container by node
                log_str += "<br/><strong>Updating container {:.12} @ {} for {}</strong>, " \
                           "new allocation {:.2f} / {}".format(controller.container.container_id,
                                                               controller.container.node,
                                                               controller.container.model,
                                                               controller.nc,
                                                               self.max_c)
                # post to actuator
                response = requests.post("http://" + node + ":" + str(
                    self.actuator_port) + "/containers/" + controller.container.container_id,
                    json={"cpu_quota": int(controller.nc * 100000)})
                log_str += "<br/>actuator response: {}".format(response.text)
                # post con containers_manager
                response = requests.patch(self.containers_endpoint,
                                          json={"container_id": controller.container.container_id,
                                                "cpu_quota": int(controller.nc * 100000)})
                log_str += "<br/>cm response: {}".format(response.text)

        self.logs.append({"ts": time.time(), "date": str(
            datetime.datetime.now()), "msg": log_str})

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
