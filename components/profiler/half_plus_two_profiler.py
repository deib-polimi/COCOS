import matplotlib.pyplot as plt
from profiler import Profiler


class HalfPlusTwoProfiler(Profiler):

    def before_profiling(self):
        self.load_request_from_file()
        self.warm_up_model(self.bench_data[0])

    def after_profiling(self):
        self.logger.info("avg response times %s", self.avg_times)

        # plot response time graph
        plt.hist(self.avg_times)
        plt.show()
