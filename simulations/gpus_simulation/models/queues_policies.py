import random
from enum import IntEnum


# Define how applications queues are managed
class QueuesPolicy(IntEnum):
    RANDOM = 0
    LONGEST_QUEUE = 1
    HEURISTIC_1 = 2


class QueuesPolicies:
    def __init__(self) -> None:
        self.policies = {QueuesPolicy.RANDOM: self.policy_random,
                         QueuesPolicy.LONGEST_QUEUE: self.policy_longest_queue,
                         QueuesPolicy.HEURISTIC_1: self.policy_heuristic_1}

    @staticmethod
    def policy_random(reqs_queues) -> str:
        return random.choice(list(reqs_queues.keys()))

    @staticmethod
    def policy_longest_queue(reqs_queues) -> str:
        # compute the max
        max_length = max([reqs_queues[model].qsize() for model in reqs_queues])

        # return a random queue between the ones with the same size
        queues_same_length = []
        for model in reqs_queues:
            if reqs_queues[model].qsize() == max_length:
                queues_same_length.append(model)

        return random.choice(queues_same_length)

    @staticmethod
    def policy_heuristic_1(reqs_queues) -> str:
        return 0
