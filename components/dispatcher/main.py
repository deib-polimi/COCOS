from dispatcher import Dispatcher
from dispatcher import DispatchingPolicy
from flask import Flask, jsonify, abort, request
from models.req import Req
from models.model import Model
from models.device import Device
from models.container import Container
from models.queues_policies import QueuesPolicies, QueuesPolicy
from concurrent.futures import ThreadPoolExecutor
import logging
import requests
import threading
import queue
import coloredlogs
import time

app = Flask(__name__)


@app.route('/', methods=['GET'])
def get_status():
    return {"status": status}


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data:
        return {'error': 'input not specified'}
    elif 'model' not in data.keys():
        return {'error': 'key model not specified'}
    elif 'version' not in data.keys():
        return {'error': 'key version not specified'}
    elif 'instances' not in data.keys():
        return {'error': 'key instances not specified'}

    # app.logger.info("IN - REQ %s/V%s %s", data["model"], data["version"], data["instances"])

    # Queue and log incoming request
    req = Req(data["model"], data["version"], data["instances"])
    reqs_queues[data["model"]].put(req)
    log_queue.put(req)

    # Forward 200
    return {"status": "ok",
            "id": req.id}


def log_consumer():
    while True:
        payload = log_queue.get().to_json()
        requests.post(requests_store_host, json=payload)
        time.sleep(0.1)


def queues_pooling(dispatcher, policy):
    # Create the pool of consumers
    consumer_threads_poll = ThreadPoolExecutor(max_workers=MAX_CONSUMERS_THREADS)

    while True:
        selected_queue = policy()
        if not reqs_queues[selected_queue].empty():
            # Get next request
            req = reqs_queues[selected_queue].get()
            # Consume the request
            consumer_threads_poll.submit(queue_consumer(dispatcher, req))
        else:
            time.sleep(0.001)


def queue_consumer(dispatcher, req):
    # Forward request (dispatcher)
    # logging.info("Consumer for %s sending to dispatcher...", dispatcher.device)
    dispatcher.compute(req)
    log_queue.put(req)


def get_data(url):
    try:
        response = requests.get(url)
    except Exception as e:
        logging.warning(e)
        response = []
    return response.json()


reqs_queues = {}
log_queue = queue.Queue()
MAX_CONSUMERS_THREADS = 100


def create_app(containers_manager="http://localhost:5001",
               requests_store="http://localhost:5002",
               verbose=1,
               gpu_queues_policy=QueuesPolicy.HEURISTIC_1,
               cpu_queues_policy=QueuesPolicy.ROUND_ROBIN,
               max_log_consumers=1,
               max_polling=1,  # the number of threads waiting for requests
               max_consumers=100):  # the number of concurrent threads requests
    global reqs_queues, requests_store_host, status, gpu_policy, cpu_policy, responses_list, MAX_CONSUMERS_THREADS
    MAX_CONSUMERS_THREADS = max_consumers

    requests_store_host = requests_store + "/requests"

    # init log
    coloredlogs.install(level='DEBUG', milliseconds=True)
    # log_format = "%(asctime)s:%(levelname)s:%(name)s: %(filename)s:%(lineno)d:%(message)s"
    # logging.basicConfig(level='DEBUG', format=log_format)

    # init models and containers
    status = "Init models and containers"
    logging.info(status)
    models_endpoint = containers_manager + "/models"
    containers_endpoint = containers_manager + "/containers"
    logging.info("Getting models from: %s", models_endpoint)
    logging.info("Getting containers from: %s", containers_endpoint)

    models = [Model(json_data=json_model) for json_model in get_data(models_endpoint)]
    logging.info("Models: %s", [model.to_json() for model in models])
    containers = [Container(json_data=json_container) for json_container in get_data(containers_endpoint)]
    logging.info("Containers: %s", [container.to_json() for container in containers])
    logging.info("Found %d models and %d containers", len(models), len(containers))

    # init reqs queues
    reqs_queues = {model.name: queue.Queue() for model in models}
    responses_list = {model.name: [] for model in models}

    # init policy
    queues_policies = QueuesPolicies(reqs_queues, responses_list, models, logging)
    gpu_policy = queues_policies.policies.get(gpu_queues_policy)
    cpu_policy = queues_policies.policies.get(cpu_queues_policy)
    logging.info("Policy for GPUs: %s", gpu_queues_policy)
    logging.info("Policy for CPUs: %s", cpu_queues_policy)

    # disable logging if verbose == 0
    logging.info("Verbose: %d", verbose)
    if verbose == 0:
        app.logger.disabled = True
        logging.getLogger('werkzeug').setLevel(logging.WARNING)

    # init dispatchers
    status = "Init dispatchers"
    logging.info(status)
    dispatcher_gpu = Dispatcher(app.logger, models, containers, DispatchingPolicy.ROUND_ROBIN, Device.GPU)
    dispatcher_cpu = Dispatcher(app.logger, models, containers, DispatchingPolicy.ROUND_ROBIN, Device.CPU)

    # start the send requests thread
    status = "Start send reqs thread"
    logging.info(status)
    log_consumer_threads_pool = ThreadPoolExecutor(max_workers=max_log_consumers)
    for i in range(max_log_consumers):
        log_consumer_threads_pool.submit(log_consumer)

    # start the queues consumer threads
    status = "Start queues consumer threads"
    logging.info(status)

    if list(filter(lambda c: c.device == Device.GPU and c.active, containers)):
        # threads that pools from the apps queues and dispatch to gpus
        polling_gpu_threads_pool = ThreadPoolExecutor(max_workers=max_polling)
        for i in range(max_polling):
            polling_gpu_threads_pool.submit(queues_pooling, dispatcher_gpu, gpu_policy)

    if list(filter(lambda c: c.device == Device.CPU and c.active, containers)):
        # threads that pools from the apps queues and dispatch to cpus
        pooling_cpu_threads_pool = ThreadPoolExecutor(max_workers=max_polling)
        for i in range(max_polling):
            pooling_cpu_threads_pool.submit(queues_pooling, dispatcher_cpu, cpu_policy)

    # start
    status = "Running"
    logging.info(status)
    return app


if __name__ == '__main__':
    create_app()
