from models.queues_policies import QueuesPolicies, QueuesPolicy
from models.model import Model
import logging
import random
import threading
import time
import queue
import statistics
import matplotlib.pyplot as plt

GPUS = [1, 1, 1, 1, 1]  # speeds of GPUs
MODELS = [Model("m1", 1, 0.5, 1), Model("m2", 1, 0.5, 1)]  # models
AVG_RESPONSE_TIME = {"m1": 0.05, "m2": 0.01}  # avg response time for the app [s]
STDEV = [0.6, 1]  # standard deviation, min max
ARRIVAL_RATES = {"m1": 50, "m2": 100}  # arrival rate [req/s]
SIM_DURATION = 5  # simulation duration [s]
QUEUES_POLICY = QueuesPolicy.HEURISTIC_1


class Req:
    model = None
    ts_in = None
    ts_out = None

    def __init__(self, model):
        self.ts_in = time.time()
        self.model = model


# PRODUCER
def producer():
    # init and start the producers threads
    for model in MODELS:
        producer_threads.append(threading.Thread(target=produce, args=(model.name,)))

    for pt in producer_threads:
        pt.start()


def produce(model):
    producer_sleep = 1 / ARRIVAL_RATES[model]
    logger.info("PRODUCER %s, SLEEP %f", model, producer_sleep)

    while producers_running:
        logger.info("ADDING req to %s", model)
        req = Req(model)
        in_queues[model].put(req)

        time.sleep(producer_sleep)


# CONSUMER
def consumer():
    # init and start the consumers threads
    for gpu in range(len(GPUS)):
        gpus_threads.append(threading.Thread(target=consume, args=(gpu,)))

    for gt in gpus_threads:
        gt.start()


def consume(gpu):
    while simulation_running:
        # select the queue
        selected_model = policy()

        if not in_queues[selected_model].empty():
            req = in_queues[selected_model].get()

            response_time = random.uniform(AVG_RESPONSE_TIME[selected_model] * STDEV[0],
                                           AVG_RESPONSE_TIME[selected_model] * STDEV[1])
            logger.info("CONSUMING from %s, WORKING for %f", selected_model, response_time)
            time.sleep(response_time / GPUS[gpu])
            req.ts_out = time.time()

            out_queues[selected_model].append(req)

    logger.info("STOPPING consumer %d", gpu)


# MEASURE
def measure():
    # init and start the measure thread
    measure_thread = threading.Thread(target=measurement)
    measure_thread.start()


def measurement():
    while simulation_running:
        now = time.time()
        time_m.append(now)

        # measure the queues lengths
        for model in MODELS:
            queues_lenghts_m[model.name].append(in_queues[model.name].qsize())

        time.sleep(0.001)

    logger.info("STOPPING measurement")


if __name__ == "__main__":
    in_queues = {}
    out_queues = {}
    gpus_threads = []
    producer_threads = []
    time_m = []
    queues_lenghts_m = {}

    # init log
    log_format = "%(asctime)s:%(levelname)s:%(name)s: %(filename)s:%(lineno)d:%(message)s"
    logging.basicConfig(format=log_format)
    logger = logging.getLogger(__name__)
    # logger.setLevel(level=logging.DEBUG)

    # init policy
    queues_policies = QueuesPolicies(in_queues, out_queues, MODELS)
    policy = queues_policies.policies.get(QUEUES_POLICY)
    logger.info("Policy: %s", QUEUES_POLICY)

    for model in MODELS:
        in_queues[model.name] = queue.Queue()
        queues_lenghts_m[model.name] = []
        out_queues[model.name] = []

    producers_running = True
    simulation_running = True

    producer()
    consumer()
    measure()

    # run the simulation
    time.sleep(SIM_DURATION)

    # stop the simulation
    simulation_running = False
    time.sleep(1)
    producers_running = False

    for gt in gpus_threads:
        gt.join()

    for pt in producer_threads:
        pt.join()

    # show results
    logger.setLevel(level=logging.DEBUG)

    logger.info("Max throughput: %d req / s", sum(GPUS))
    logger.info("Load < Max throughput: %.2f < %d",
                sum([AVG_RESPONSE_TIME[model.name] * STDEV[1] * ARRIVAL_RATES[model.name] for model in MODELS]),
                sum(GPUS))

    # Response Time
    for model in MODELS:
        response_times = [req.ts_out - req.ts_in for req in out_queues[model.name]]
        avg_responses_time = statistics.mean(response_times)
        logger.info("MODEL: %s"
                    "\nCONSUMED: %d "
                    "\nAVG RT: %f"
                    "\nMAX RT: %f"
                    "\nMIN RT: %f"
                    "\nSLA: %f"
                    "\nSLA respected: %r",
                    model.name,
                    len(out_queues[model.name]),
                    avg_responses_time,
                    max(response_times),
                    min(response_times),
                    model.sla,
                    (avg_responses_time < model.sla))
        plt.plot(range(len(response_times)), response_times, 'o', label="RT " + model.name)
        plt.plot(range(len(response_times)), response_times, label="RT " + model.name)
        plt.plot(range(len(response_times)), [avg_responses_time] * len(response_times), '--', label="AVG RT " + model.name)
        plt.plot(range(len(response_times)), [model.sla] * len(response_times), label="SLA " + model.name)
    plt.xlabel("Req")
    plt.ylabel("Time [s]")
    plt.legend()
    plt.show()

    # Queues length
    for model in MODELS:
        plt.plot(time_m, queues_lenghts_m[model.name], label="QL " + model.name)
    plt.xlabel("Time [s]")
    plt.ylabel("Queue Length [# req]")
    plt.legend()
    plt.show()
