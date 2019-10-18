from models.queues_policies import QueuesPolicies, QueuesPolicy
import logging
import random
import threading
import time
import queue
import statistics
import numpy
import matplotlib.pyplot as plt

GPUS = [1]  # speeds of GPUs
MODELS = ["m1", "m2"]  # models
SLA = {"m1": 0.1, "m2": 0.1}  # SLA [s]
AVG_RESPONSE_TIME = {"m1": 0.05, "m2": 0.05}  # avg response time for the app [s]
STDEV = [0.7, 0.9]  # standard deviation, min max
ALPHA = {"m1": 1, "m2": 1}  # alpha
ARRIVAL_RATES = {"m1": 10, "m2": 10}  # arrival rate [req/s]
SIM_DURATION = 5  # simulation duration [s]
QUEUES_POLICY = QueuesPolicy.LONGEST_QUEUE


class Req:
    model = None
    gen_time = None
    in_time = None
    out_time = None

    def __init__(self, model):
        self.gen_time = time.time()
        self.model = model


# PRODUCER
def producer():
    # init and start the producers threads
    for model in MODELS:
        producer_threads.append(threading.Thread(target=produce, args=(model,)))

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
        selected_model = policy(in_queues)

        if not in_queues[selected_model].empty():
            req = in_queues[selected_model].get()

            req.in_time = time.time()
            response_time = random.uniform(AVG_RESPONSE_TIME[selected_model] * STDEV[0],
                                           AVG_RESPONSE_TIME[selected_model] * STDEV[1])
            logger.info("CONSUMING from %s, WORKING for %f", selected_model, response_time)
            time.sleep(response_time / GPUS[gpu])
            req.out_time = time.time()

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
            queues_lenghts_m[model].append(in_queues[model].qsize())

        time.sleep(0.001)

    logger.info("STOPPING measurement")


def select_queue():
    needs = []
    avg_response_times = []
    queue_lengths = []
    for m, model in enumerate(MODELS):
        queue_list = list(in_queues[m].queue)
        queue_lengths.append(len(queue_list))

        # response_times = [time.time() - req.gen_time for req in queue_list]
        response_times = [req.out_time - req.gen_time for req in out_queues[m]]
        print("m%d: %s" % (m, response_times))

        if len(response_times) > 0:
            avg_response_time = statistics.mean(response_times)
        else:
            avg_response_time = 0

        avg_response_times.append(avg_response_time)

        if avg_response_time < SLA[m] * ALPHA[m]:
            needs.append(0)
        else:
            needs.append(avg_response_time - SLA[m] + (1 - ALPHA[m]) * SLA[m])

    print("\n")
    if max(needs) == 0:
        print("QUEUE lengths: %s" % queue_lengths)
        selected = numpy.argmax(queue_lengths)
    else:
        selected = numpy.argmax(needs)

    print("SELECTED: %d, AVG TIMES: %s, SLA_TIMES: %s, NEEDS: %s" % (int(selected), avg_response_times, SLA, needs))

    return int(selected)


def select_max_or_random(list):
    i_max = 0
    for i, v in enumerate(list):
        if v > list[i_max]:
            i_max = i

    max_i = []
    for i, v in enumerate(list):
        if v == list[i_max]:
            max_i.append(i)

    if len(max_i) == 1:
        return max_i
    else:
        return random.choice(max_i)


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
    queues_policies = QueuesPolicies()
    policy = queues_policies.policies.get(QUEUES_POLICY)
    logger.info("Policy: %s", QUEUES_POLICY)

    for model in MODELS:
        in_queues[model] = queue.Queue()
        queues_lenghts_m[model] = []

    for model in MODELS:
        out_queues[model] = []

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
                sum([AVG_RESPONSE_TIME[model] * STDEV[1] * ARRIVAL_RATES[model] for model in MODELS]),
                sum(GPUS))

    # Response Time
    for model in MODELS:
        response_times = [req.out_time - req.gen_time for req in out_queues[model]]
        avg_responses_time = statistics.mean(response_times)
        logger.info("MODEL: %s"
                    "\nCONSUMED: %d "
                    "\nAVG RT: %f"
                    "\nMAX RT: %f"
                    "\nMIN RT: %f"
                    "\nSLA: %f"
                    "\nSLA respected: %r",
                    model,
                    len(out_queues[model]),
                    avg_responses_time,
                    max(response_times),
                    min(response_times),
                    SLA[model],
                    (avg_responses_time < SLA[model]))
        plt.plot(range(len(response_times)), response_times, 'o', label="RT " + model)
        plt.plot(range(len(response_times)), response_times, label="RT " + model)
        plt.plot(range(len(response_times)), [avg_responses_time] * len(response_times), '--', label="AVG RT " + model)
        plt.plot(range(len(response_times)), [SLA[model]] * len(response_times), label="SLA " + model)
    plt.xlabel("Req")
    plt.ylabel("Time [s]")
    plt.legend()
    plt.show()

    # Queues length
    for model in MODELS:
        plt.plot(time_m, queues_lenghts_m[model], label="QL " + model)
    plt.xlabel("Time [s]")
    plt.ylabel("Queue Length [# req]")
    plt.legend()
    plt.show()
