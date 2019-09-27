import logging
from profilers.half_plus_two_profiler import HalfPlusTwoProfiler
from profilers.resnet_profiler import ResnetProfile
from profilers.googlenet_profiler import GoogLeNetProfiler
from profilers.alexnet_profiler import AlexNetProfiler
from profilers.vgg16_profiler import VGG16Profiler
from profilers.skyline_extraction_profiler import SkylineExtractionProfiler

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

    """
    # init profiler
    status = "init profiler"
    logging.info(status)
    profiler = ResnetProfile(PARAMS_FILE, "resnet_NHWC", logging)
    profiler.run()
    profiler.validate()
    """

    """
    # init profiler
    status = "init profiler"
    logging.info(status)
    profiler = AlexNetProfiler(PARAMS_FILE, "alexnet", logging)
    # profiler.run()
    profiler.validate()
    """

    """
    # init profiler
    status = "init profiler"
    logging.info(status)
    profiler = GoogLeNetProfiler(PARAMS_FILE, "googlenet", logging)
    profiler.run()
    profiler.validate()
    """

    # init profiler
    status = "init profiler"
    logging.info(status)
    profiler = VGG16Profiler(PARAMS_FILE, "vgg16", logging)
    profiler.run()
    profiler.validate()

    """
    # init profiler
    status = "init profiler"
    logging.info(status)
    profiler = SkylineExtractionProfiler(PARAMS_FILE, "skyline_extraction", logging)
    profiler.run()
    profiler.validate()
    """