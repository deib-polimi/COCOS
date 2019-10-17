from dispatcher import Dispatcher
from dispatcher import QueuePolicy
from dispatcher import DispatchingPolicy
from flask import Flask, jsonify, abort, request
from models.req import Req
from models.model import Model
from models.device import Device
from models.container import Container
from concurrent.futures import ThreadPoolExecutor
import random
import time
import logging
import requests
import threading
import queue
import coloredlogs


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

    app.logger.info("IN - REQ %s/V%s %s", data["model"], data["version"], data["instances"])

    # Queue and log incoming request
    req = Req(data["model"], data["version"], data["instances"])
    log_queue.put(req)
    reqs_queues[data["model"]].put(req)

    # Forward 200
    return {"status": "ok"}


def send_requests():
    while True:
        payload = log_queue.get().to_json()
        response = requests.post(requests_store_host, json=payload)


def queues_consumer(dispatcher):
    while True:
        selected_queue = policy()
        if not reqs_queues[selected_queue].empty():
            # Get next request
            req = reqs_queues[selected_queue].get()

            # Forward request (dispatcher)
            logging.info("Consumer for %s sending to dispatcher...", dispatcher.device)
            status_code, response = dispatcher.compute(req)

            # Log outcoming response
            if status_code == 200:
                req.set_completed(response)
            else:
                req.set_error(status_code + "\n" + response)
            log_queue.put(req)


def get_data(url):
    try:
        response = requests.get(url)
    except Exception as e:
        logging.warning(e)
        response = []
    return response.json()


def policy_random() -> str:
    return random.choice(list(reqs_queues.keys()))


def policy_longest_queue() -> str:
    max = -1
    max_queue = None
    for model in reqs_queues:
        if reqs_queues[model].size() > max:
            max_queue = model
    return max_queue


def policy_heuristic_1() -> str:
    return 0


reqs_queues = {}
log_queue = queue.Queue()
policies = {QueuePolicy.RANDOM: policy_random,
            QueuePolicy.LONGEST_QUEUE: policy_longest_queue,
            QueuePolicy.HEURISTIC_1: policy_heuristic_1}


def create_app(containers_manager="http://localhost:5001",
               requests_store="http://localhost:5002",
               verbose=1,
               queue_policy=QueuePolicy.RANDOM,
               num_consumers=10):
    global dispatcher, reqs_queues, requests_store_host, status, policy

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

    # init policy
    policy = policies.get(queue_policy)
    logging.info("Policy: %s", queue_policy)

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
    send_reqs_thread = threading.Thread(target=send_requests)
    send_reqs_thread.start()

    # start the queues consumer threads
    status = "Start queues consumer threads"
    logging.info(status)
    # consumer_thread = threading.Thread(target=queues_consumer)
    # consumer_thread.start()

    consumer_gpu_threads_pool = ThreadPoolExecutor(num_consumers)
    for i in range(num_consumers):
        consumer_gpu_threads_pool.submit(queues_consumer, dispatcher_gpu)

    consumer_cpu_threads_pool = ThreadPoolExecutor(num_consumers)
    for i in range(num_consumers):
        consumer_cpu_threads_pool.submit(queues_consumer, dispatcher_cpu)

    # start
    status = "Running"
    logging.info(status)
    return app
