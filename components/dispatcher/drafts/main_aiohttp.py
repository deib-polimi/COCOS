"""
AIOHTTP version (draft)

"""
import argparse
import time

from models.req import Req
from models.model import Model
from models.container import Container
from dispatcher import Dispatcher
from dispatcher import QueuePolicy
import requests
from aiohttp import web
import asyncio
import logging
import random
from concurrent.futures import ProcessPoolExecutor


# GET /
def get_status(_):
    return web.json_response({"status": status})


# POST /predict
async def predict(request):
    data = await request.json()

    # check if incoming data are valid
    if not data:
        return web.json_response({'error': 'input not specified'})
    elif 'model' not in data.keys():
        return web.json_response({'error': 'key model not specified'})
    elif 'version' not in data.keys():
        return web.json_response({'error': 'key version not specified'})
    elif 'instances' not in data.keys():
        return web.json_response({'error': 'key instances not specified'})

    logger.info("REQ %s/V%s %s", data["model"], data["version"], data["instances"])

    # Create an Event object
    request_event = asyncio.Event()

    # Queue and log incoming request
    req = Req(data["model"], data["version"], data["instances"], request_event)
    await reqsQueues[data["model"]].put(req)

    # Wait for response
    await request_event.wait()

    req.set_completed("RESPONSE")

    # Log outcoming response
    reqsDone[data["model"]].append(req)

    # Forward reply
    return web.json_response({"resp": req.to_json()})


async def requests_consumer(app, model_name):
    logger.info("Starting consumer for model %s", model_name)
    try:
        while True:
            req = await reqsQueues[model_name].get()
            logger.info("Waiting for turn")
            await turn[model_name].wait()
            logger.info("%s CONSUMING_R: %s", model_name, req.id)
            # Forward request (dispatcher)
            # status_code, response = dispatcher.compute(req)
            await asyncio.sleep(10)
            #time.sleep(10)
            req.event.set()
            logger.info("%s CONSUMED R: %s", model_name, req.to_json())

    except asyncio.CancelledError:
        pass


async def policy_task(app):
    try:
        while True:
            for model in models:
                turn[model.name].clear()
            selected_model = policy()
            turn[selected_model].set()
            await asyncio.sleep(1)

    except asyncio.CancelledError:
        pass


def policy_random() -> str:
    not_empty_queues = []
    for q in reqsQueues:
        if not reqsQueues[q].empty():
            not_empty_queues.append(q)
    logger.info("NOT EMPTY: %s", not_empty_queues)
    if len(not_empty_queues) > 0:
        return random.choice(not_empty_queues)
    else:
        return random.choice(list(reqsQueues.keys()))


def policy_longest_queue() -> str:
    return 0


def policy_heuristic_1() -> str:
    return 0


def get_data(url):
    try:
        response = requests.get(url)
    except Exception as e:
        logging.warning(e)
        response = []
    return response.json()


async def start_background_tasks(app):
    for model in models:
        app['requests_consumer_' + model.name] = asyncio.create_task(requests_consumer(app, model.name))
    app['policy_task'] = asyncio.create_task(policy_task(app))


async def cleanup_background_tasks(app):
    for model in models:
        app['requests_consumer_' + model.name].cancel()
        await app['requests_consumer_' + model.name]

    app['policy_task'].cancel()
    await app['policy_task']


reqsQueues = {}
reqsDone = {}
policies = {QueuePolicy.RANDOM: policy_random,
            QueuePolicy.LONGEST_QUEUE: policy_longest_queue,
            QueuePolicy.HEURISTIC_1: policy_heuristic_1}

if __name__ == '__main__':
    containers_manager = "http://localhost:5001"

    parser = argparse.ArgumentParser()
    parser.add_argument('--containers_manager', type=str, required=True)
    parser.add_argument('--verbose', type=int, default=1)
    parser.add_argument('--policy', type=int, default=QueuePolicy.RANDOM)
    args = parser.parse_args()

    """
    # init models and containers
    status = "init models and containers"
    logging.info(status)
    models_endpoint = containers_manager + "/models"
    containers_endpoint = containers_manager + "/containers"
    logging.info("Getting models from: %s", models_endpoint)
    logging.info("Getting containers from: %s", containers_endpoint)

    models = [Model(json_data=json_model) for json_model in get_data(models_endpoint)]
    logging.info("Models: %s", [model.to_json() for model in models])
    containers = [Container(json_data=json_container) for json_container in get_data(containers_endpoint)]
    logging.info("Containers: %s", [container.to_json() for container in containers])

    

    # init dispatcher
    status = "init dispatcher"
    logging.info(status)
    dispatcher = Dispatcher(app.logger, models, containers, Dispatcher.PolicyRoundRobin)

    """

    # init log
    log_format = "%(asctime)s:%(levelname)s:%(name)s:" \
                 "%(filename)s:%(lineno)d:%(message)s"
    logging.basicConfig(level='DEBUG', format=log_format)
    logger = logging

    # disable logging if verbose == 0
    logging.info("verbose: %d", args.verbose)
    if args.verbose == 0:
        logger.disabled = True
        logging.getLogger('werkzeug').setLevel(logging.WARNING)

    models = [Model("m1", 1, 100), Model("m2", 2, 200)]

    # init requests queues
    reqsQueues = {model.name: asyncio.Queue() for model in models}
    reqsDone = {model.name: [] for model in models}
    turn = {model.name: asyncio.Event() for model in models}

    # init queues policy
    policy = policies.get(args.policy)
    logging.info("policy: %d", args.policy)

    # start
    status = "running"
    logging.info(status)

    app = web.Application()
    app.add_routes([web.get('/', get_status),
                    web.post('/predict', predict)])
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    web.run_app(app)
