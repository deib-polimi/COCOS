"""
Example:
python3 client.py --target "localhost:5000" --requests 1000 --model "half_plus_two" --threads 4


It runs t thread and executes r reqs for the specified model on the target
"""

import argparse
import queue
import random
import threading
import time
import requests

TARGET = None


def run_thread(i, q):
    start = time.time()
    total_time = 0
    num_requests = 0
    response_times = []
    while not q.empty():
        predict_request = q.get()
        response = requests.post(TARGET, json=predict_request)
        response.raise_for_status()
        total_time += response.elapsed.total_seconds()
        response_times.append(response.elapsed.total_seconds())
        num_requests += 1
        print(predict_request, response.json())
    end = time.time()

    print("T{0}, WorkingTime: {1:.4f}, Reqs: {2}, AvgLat: {3:.4f}".format(i, (end - start), num_requests,
                                                                          (total_time) / num_requests))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', type=str)
    parser.add_argument('--model', type=str)
    parser.add_argument('--threads', type=int)
    parser.add_argument('--requests', type=int)
    args = parser.parse_args()

    global TARGET
    TARGET = "http://" + args.target + "/predict"

    # Compose JSON requests
    print("Composing JSON reqs...")
    predict_requests = []
    for _ in range(args.requests):
        req = {"model": args.model, "instances": [random.randint(0, 20) for _ in range(0, 10)]}
        predict_requests.append(req)

    print("Filling queue...")
    q = queue.Queue()
    for req in predict_requests:
        q.put(req)

    # TODO: Send few requests to warm-up the model.

    # Send requests and report average latency.
    print("Building threads...")
    threads = []
    for i in range(0, args.threads + 1):
        threads.append(threading.Thread(target=run_thread, args=(i, q)))

    # Start the threads, and block on their completion.
    print("Running threads...")
    start = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    end = time.time()
    print("Total Time: {0:.4f}".format((end - start)))


if __name__ == '__main__':
    main()
