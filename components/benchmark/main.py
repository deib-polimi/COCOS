import logging
from models.alexnet import AlexNet
from models.googlenet import GoogLeNet
from models.half_plus_two import HalfPlusTwo
from models.resnet import Resnet
from models.skyline_extraction import SkylineExtraction
from models.vgg16 import VGG16
from models.benchmark import BenchmarkStrategies

PARAMS_FILE = "parameters.yml"
BENCH_FOLDER = "bench_data"

if __name__ == "__main__":
    # init log
    log_format = "%(asctime)s:%(levelname)s:%(name)s:" \
                 "%(filename)s:%(lineno)d:%(message)s"
    logging.basicConfig(level='INFO', format=log_format)

    # init profiler
    status = "init profiler"
    logging.info(status)
    model = HalfPlusTwo(PARAMS_FILE, "half_plus_two", 1, BenchmarkStrategies.SERVER, logging)
    # model.run_profiling()
    model.run_benchmark()

    """
    # init profiler
    status = "init profiler"
    logging.info(status)
    model = Resnet(PARAMS_FILE, "resnet_NHWC", 1, BenchmarkStrategies.SINGLE_STREAM, logging)
    # model.run_profiling()
    # model.run_benchmark()
    model.validate()

    # init profiler
    status = "init profiler"
    logging.info(status)
    model = AlexNet(PARAMS_FILE, "alexnet", 1, BenchmarkStrategies.SINGLE_STREAM, logging)
    model.run_profiling()
    model.run_benchmark()
    
    # init profiler
    status = "init profiler"
    logging.info(status)
    model = GoogLeNet(PARAMS_FILE, "googlenet", 1, BenchmarkStrategies.SINGLE_STREAM, logging)
    model.run_profiling()
    model.run_benchmark()

    # init profiler
    status = "init profiler"
    logging.info(status)
    model = VGG16(PARAMS_FILE, "vgg16", 1, BenchmarkStrategies.SINGLE_STREAM, logging)
    model.run_profiling()
    model.run_benchmark()

    # init profiler
    status = "init profiler"
    logging.info(status)
    model = SkylineExtraction(PARAMS_FILE, "skyline_extraction", 1,
                                 BenchmarkStrategies.SINGLE_STREAM,
                                 logging)
    model.run()
    model.validate()
    """
