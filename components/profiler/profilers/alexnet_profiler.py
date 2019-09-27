from .imagenet_profiler import ImageNetProfiler
import matplotlib.pyplot as plt


class AlexNetProfiler(ImageNetProfiler):
    model_spec = {"input_width": 227,
                  "input_height": 227}

    def before_profiling(self):
        self.load_images_from_folder(self.bench_folder, self.bench_data)
        self.warm_up_model(self.bench_data[0]["request"])

    def after_profiling(self):
        self.logger.info("received %d responses", len(self.responses))
        self.logger.info("avg response times %s", self.avg_times)
        # plot response time graph
        plt.hist(self.avg_times)
        plt.show()

    def prepare_request(self, image_array):
        return {"instances": [image_array.tolist()]}
