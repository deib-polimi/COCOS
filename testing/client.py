"""
Example:
python3 client.py --target "localhost:8000" --requests 1000 --req "./half_plus_two.json" --threads 4 --verbose 1


It runs t thread and executes r reqs for the specified model on the target
"""

import argparse
import queue
import json
import threading
import time
import requests

TARGET = None


def run_thread(i, q, verbose):
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
        if verbose: print(predict_request, response.json())
    end = time.time()

    print("T{0}, WorkingTime: {1:.4f}, Reqs: {2}, AvgLat: {3:.4f}".format(i, (end - start), num_requests,
                                                                          (total_time) / num_requests))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', type=str)
    parser.add_argument('--req', type=str)
    parser.add_argument('--threads', type=int)
    parser.add_argument('--requests', type=int)
    parser.add_argument('--verbose', default=0, type=int)
    args = parser.parse_args()

    global TARGET
    TARGET = "http://" + args.target + "/predict"

    print("Verbose: ", args.verbose)

    # Compose JSON requests
    print("Composing JSON reqs...")
    # Read req data from file
    with open(args.req, 'r') as file:
        reqs = json.load(file)
    print("Reqs: ", reqs)

    print("Filling queue...")
    q = queue.Queue()
    for i in range(args.requests):
        q.put(reqs["reqs"][i % len(reqs["reqs"])])

    # TODO: Send few requests to warm-up the model.

    # Send requests and report average latency.
    print("Building threads...")
    threads = []
    for i in range(0, args.threads + 1):
        threads.append(threading.Thread(target=run_thread, args=(i, q, args.verbose)))

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
