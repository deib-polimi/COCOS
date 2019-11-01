import matplotlib.pyplot as plt
from .benchmark import Benchmark


class HalfPlusTwo(Benchmark):
    """
    Profiling
    """

    def before_profiling(self):
        self.load_requests_from_file()
        self.warm_up_model(self.bench_data[0])

    def after_profiling(self):
        self.logger.info("avg response times %s", self.avg_times)
        # plot response time graph
        plt.hist(self.avg_times)
        plt.show()

    """
    Benchmark
    """

    def before_benchmark(self):
        self.load_requests_from_file()
        self.warm_up_model(self.bench_data[0])
