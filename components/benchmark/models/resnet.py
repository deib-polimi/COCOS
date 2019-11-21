from .imagenet import ImageNet
from .benchmark import Mode
import base64
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join
import matplotlib.image as mplimg
import numpy as np
from PIL import Image
from io import BytesIO
import statistics as stat
import requests


class Resnet(ImageNet):
    URLS_FILE = "resnet_urls_50.txt"

    def prepare_image(self, image):
        jpeg_bytes = base64.b64encode(image).decode('utf-8')
        return [{"b64": str(jpeg_bytes)}]

    def load_images_from_folder(self, folder_path, store):
        """
        Load a set of images from a folder into the given variable
        """
        self.logger.info("loading images from folder %s", folder_path)
        imgs = [f for f in listdir(folder_path) if isfile(join(folder_path, f))
                and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        for img in imgs:
            with open(folder_path + img, "rb") as image_file:
                store.append(
                    {"data": mplimg.imread(folder_path + img),
                     "request": self.prepare_request(self.prepare_image(image_file.read()))})
            image_file.close()
        self.logger.info("loaded %d images", len(store))

    def load_images_from_urls(self, file, store, show_imgs=False):
        """
        Load a set of images from a file
        """
        file_urls = open(file, "r")
        for url in file_urls:
            self.logger.info("downloading %s", url.strip())
            try:
                dl_request = requests.get(url, stream=True)
                dl_request.raise_for_status()

                # open the image
                img = Image.open(BytesIO(dl_request.content))
                # convert image to array
                img_array = np.array(img)
                # resize the input shape
                img_array = self.resize_input_shape(img_array)

                if show_imgs:
                    plt.imshow(img)
                    plt.show()

                self.logger.info("composing the req for %s", url.strip())
                store.append(
                    {"data": img_array, "request": self.prepare_request(self.prepare_image(dl_request.content))})

            except Exception as e:
                self.logger.error("Exception %s", e)

        file_urls.close()

    """
    Profiling
    """

    def before_profiling(self):
        # self.load_images_from_urls(self.bench_folder + self.URLS_FILE, self.bench_data)
        self.load_images_from_folder(self.bench_folder, self.bench_data)
        # self.load_requests_from_file()
        self.warm_up_model(self.bench_data[0])

    def after_profiling(self):
        self.logger.info("received %d responses", len(self.responses))
        self.logger.info("avg response times %s, avg: %.4f", self.profiling_rt_avg, stat.mean(self.profiling_rt_avg))
        # plot response time graph
        plt.hist(self.profiling_rt_avg)
        plt.show()

    def before_validate(self):
        self.logger.info("loading validation data")
        self.load_images_from_urls(self.validation_folder + self.URLS_FILE, self.validation_data)

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

    """
    Benchmark
    """

    def before_benchmark(self):
        # self.load_images_from_urls(self.bench_folder + self.URLS_FILE, self.bench_data)
        self.load_images_from_folder(self.bench_folder, self.bench_data)
        self.warm_up_model(self.bench_data[0])
