import logging
from half_plus_two_profiler import HalfPlusTwoProfiler
from resnet_profiler import ResnetProfile

PARAMS_FILE = "parameters.yml"
BENCH_FOLDER = "bench_data"

if __name__ == "__main__":
    # init log
    log_format = "%(asctime)s:%(levelname)s:%(name)s:" \
                 "%(filename)s:%(lineno)d:%(message)s"
    logging.basicConfig(level='INFO', format=log_format)

    """
    # init profiler
    status = "init profiler"
    logging.info(status)
    profiler = HalfPlusTwoProfiler(PARAMS_FILE, "half_plus_two", logging)
    profiler.run()"""

    # init profiler
    status = "init profiler"
    logging.info(status)
    profiler = ResnetProfile(PARAMS_FILE, "resnet_NHWC", logging)
    profiler.run()
