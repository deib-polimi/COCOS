from .benchmark import Benchmark
import numpy as np
import matplotlib.image as mplimg
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join
from PIL import Image
from io import BytesIO
import requests


class ImageNet(Benchmark):
    model_spec = {"input_width": None,
                  "input_height": None}

    def load_images_from_folder(self, folder_path, store):
        """
        Load a set of images from a folder into the given variable
        """
        self.logger.info("loading images from folder %s", folder_path)
        imgs = [f for f in listdir(folder_path) if isfile(join(folder_path, f))
                and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        for img in imgs:
            img = mplimg.imread(folder_path + img)
            self.logger.info("loaded image with shape %s", img.shape)

            # resize the input shape
            img = self.resize_input_shape(img)

            store.append({"data": img, "request": self.prepare_request([img.tolist()])})
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
                store.append({"data": img_array, "request": self.prepare_request([img_array.tolist()])})

            except Exception as e:
                self.logger.error("Exception %s", e)

        file_urls.close()

    def resize_input_shape(self, img):
        # check if the model has a specified input width and height
        if self.model_spec["input_width"] is not None and self.model_spec["input_height"] is not None:
            # check if resize and crop is needed
            img_height, img_width, _ = img.shape
            if img_width != self.model_spec["input_width"] or img_height != self.model_spec["input_height"]:
                img = self.crop_and_resize_image(img, self.model_spec["input_width"], self.model_spec["input_height"])
                self.logger.info("cropped image with shape %s", img.shape)
        return img

    def crop_and_resize_image(self, image, width, height):
        # crop
        img_height, img_width, _ = image.shape

        min_side = min(img_width, img_height)
        new_width = min_side
        new_height = min_side

        left = int(np.ceil((img_width - new_width) / 2))
        right = img_width - int(np.floor((img_width - new_width) / 2))
        top = int(np.ceil((img_height - new_height) / 2))
        bottom = img_height - int(np.floor((img_height - new_height) / 2))

        if len(image.shape) == 2:
            center_cropped_img = image[top:bottom, left:right]
        else:
            center_cropped_img = image[top:bottom, left:right, ...]

        # convert array to image
        img = Image.fromarray(center_cropped_img)

        # resize
        img = img.resize((width, height), Image.ANTIALIAS)

        # convert image to array
        center_cropped_resized = np.array(img)
        return center_cropped_resized

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
