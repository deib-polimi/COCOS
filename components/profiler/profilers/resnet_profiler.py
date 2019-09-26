from .imagenet_profiler import ImageNetProfiler
import base64
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join
import matplotlib.image as mplimg
import numpy as np


class ResnetProfile(ImageNetProfiler):
    URLS_FILE = "resnet_urls_5.txt"

    def before_profiling(self):
        self.load_images_from_urls(self.bench_folder + self.URLS_FILE, self.bench_data)
        self.warm_up_model(self.bench_data[0]["request"])

    def after_profiling(self):
        self.logger.info("received %d responses", len(self.responses))
        self.logger.info("avg response times %s", self.avg_times)
        # plot response time graph
        plt.hist(self.avg_times)
        plt.show()

    def prepare_request(self, image):
        jpeg_bytes = base64.b64encode(image).decode('utf-8')
        return {"instances": [{"b64": str(jpeg_bytes)}]}

    def load_images_from_folder(self, folder_path, store):
        """
        Load a set of images from a folder into the given variable
        """
        self.logger.info("loading images from folder %s", folder_path)
        imgs = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
        for img in imgs:
            with open(folder_path + img, "rb") as image_file:
                store.append(
                    {"data": mplimg.imread(folder_path + img), "request": self.prepare_request(image_file.read())})
            image_file.close()
        self.logger.info("loaded %d images", len(store))

    def show_class(self, probs):
        """
        Displays the classification results given the class probability for each image
        """
        # Get a list of ImageNet class labels
        with open('./validation_data/imagenet-classes.txt', 'r') as infile:
            class_labels = [line.strip() for line in infile.readlines()]

        # Pick the class with the highest confidence for each image
        class_index = np.argmax(probs[0]["probabilities"], axis=0)

        self.logger.info("Class: %d, %s, confidence: %f",
                         class_index, class_labels[class_index], round(probs[0]["probabilities"][class_index] * 100, 2))
