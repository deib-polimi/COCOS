from .profiler import Profiler
import numpy as np
import matplotlib.image as mplimg
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join
from PIL import Image
from io import BytesIO
import requests


class ImageNetProfiler(Profiler):

    def prepare_request(self, image):
        """
        Abstract
        transform raw data into a request ready to be sent
        """
        pass

    def load_images_from_folder(self, folder_path, store):
        """
        Load a set of images from a folder into the given variable
        """
        self.logger.info("loading images from folder %s", folder_path)
        imgs = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
        for img in imgs:
            img = mplimg.imread(folder_path + img)
            self.logger.info("loaded image with shape %s", img.shape)
            store.append({"data": img, "request": self.prepare_request(img)})
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

                if show_imgs:
                    im = Image.open(BytesIO(dl_request.content))
                    plt.imshow(im)
                    plt.show()

                self.logger.info("composing the req for %s", url.strip())
                store.append({"data": dl_request.content, "request": self.prepare_request(dl_request.content)})

            except Exception as e:
                self.logger.error("Exception %s", e)

        file_urls.close()

    def before_validate(self):
        self.logger.info("loading validation data")
        self.load_images_from_folder(self.validation_folder, self.validation_data)

    def show_data(self, data):
        plt.imshow(data)
        plt.show()

    def show_response(self, response):
        # self.logger.info("response %s", response)
        self.show_class(response["predictions"])

    def show_class(self, probs):
        """
        Displays the classification results given the class probability for each image
        """
        # Get a list of ImageNet class labels
        with open('./validation_data/imagenet-classes.txt', 'r') as infile:
            class_labels = [line.strip() for line in infile.readlines()]

        # Pick the class with the highest confidence for each image
        class_index = np.argmax(probs, axis=1)
        self.logger.info("Class: %d, %s, confidence: %f",
                         class_index[0], class_labels[class_index[0]], round(probs[0][class_index[0]] * 100, 2))
