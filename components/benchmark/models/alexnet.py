from .imagenet import ImageNet
import matplotlib.pyplot as plt


class AlexNet(ImageNet):
    model_spec = {"input_width": 227,
                  "input_height": 227}
    URLS_FILE = "img_urls_5.txt"

    """
    Profiling
    """

    def before_profiling(self):
        self.load_images_from_folder(self.bench_folder, self.bench_data)
        # self.load_images_from_urls(self.bench_folder + self.URLS_FILE, self.bench_data)
        self.warm_up_model(self.bench_data[0])

    def after_profiling(self):
        self.logger.info("received %d responses", len(self.responses))
        self.logger.info("avg response times %s", self.profiling_rt_avg)
        # plot response time graph
        plt.hist(self.profiling_rt_avg)
        plt.show()

    def before_validate(self):
        self.logger.info("loading validation data")
        self.load_images_from_urls(self.validation_folder + self.URLS_FILE, self.validation_data)

    """
    Benchmark
    """

    def before_benchmark(self):
        self.load_images_from_folder(self.bench_folder, self.bench_data)
