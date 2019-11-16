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

    """
    Models available: half_plus_two, resnet_NHWC, alexnet, googlenet, vgg16, skyline_extraction
    """

    # init profiler
    status = "init"
    logging.info(status)
    model = Resnet(PARAMS_FILE, "resnet_NHWC", 1, BenchmarkStrategies.VARIABLE_SLA, logging)
    # model.run_profiling()
    model.run_benchmark()
    # model.validate()
