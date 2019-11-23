from .imagenet import ImageNet
import matplotlib.pyplot as plt


class GoogLeNet(ImageNet):
    model_spec = {"input_width": 224,
                  "input_height": 224}

    """
    URLS_FILE = "img_urls_5.txt"
    Validate using images from URLs
    def before_validate(self):
        self.logger.info("loading validation data")
        self.load_images_from_urls(self.validation_folder + self.URLS_FILE, self.validation_data)
    """

    def before_profiling(self):
        self.load_images_from_folder(self.bench_folder, self.bench_data)
        self.warm_up_model(self.bench_data[0])

    def after_profiling(self):
        self.logger.info("received %d responses", len(self.responses))
        self.logger.info("avg response times %s", self.profiling_rt_avg)
        # plot response time graph
        plt.hist(self.profiling_rt_avg)
        plt.show()

    """
    Benchmark
    """

    def before_benchmark(self):
        self.load_images_from_folder(self.bench_folder, self.bench_data)
