from .imagenet import ImageNet
import matplotlib.pyplot as plt
import numpy as np
import cv2


class SkylineExtraction(ImageNet):
    model_spec = {"input_width": 320,
                  "input_height": 240}
    EROSION_SIZE = 3
    EROSION_KERNEL = cv2.getStructuringElement(cv2.MORPH_ERODE,
                                               (2 * EROSION_SIZE + 1, 2 * EROSION_SIZE + 1),
                                               (EROSION_SIZE, EROSION_SIZE))
    OPTIMUM_THRESHOLD = 162
    pooling_scale_factor = 4

    def before_profiling(self):
        self.load_images_from_folder(self.bench_folder, self.bench_data)
        self.warm_up_model(self.bench_data[0])

    def after_profiling(self):
        self.logger.info("received %d responses", len(self.responses))
        self.logger.info("avg response times %s", self.profiling_rt_avg)
        # plot response time graph
        plt.hist(self.profiling_rt_avg)
        plt.show()

    def show_response(self, response):
        image_mat = self.convert_float_output_to_mat(response["predictions"], 53, 73)

        image_mat_height, image_mat_width = image_mat.shape
        expanded_skyline_mat_width = image_mat_width * self.pooling_scale_factor
        expanded_skyline_mat_height = image_mat_height * self.pooling_scale_factor
        expanded_skyline_mat = cv2.resize(image_mat, (expanded_skyline_mat_width, expanded_skyline_mat_height))
        picture_skyline_mat = cv2.erode(expanded_skyline_mat, self.EROSION_KERNEL)
        _, picture_skyline_mat = cv2.threshold(picture_skyline_mat, self.OPTIMUM_THRESHOLD, 255, cv2.THRESH_TOZERO)
        picture_skyline_skeleton_mat = self.skeleton(picture_skyline_mat)

        plt.imshow(picture_skyline_skeleton_mat)
        plt.show()

    def convert_float_output_to_mat(self, buffer, height, width):
        # Mat result = new Mat(height, width, CvType.CV_8UC1);
        result = np.zeros((height, width))

        row = col = 0
        for row in range(0, height):
            for col in range(0, width):
                val = int(buffer[row * width + col][1] * 255)
                result[row][col] = val

        return result

    def skeleton(self, img):
        """ OpenCV function to return a skeletonized version of img, a Mat object"""
        skeleton = np.zeros(img.shape, np.uint8)
        eroded = np.zeros(img.shape, np.uint8)
        temp = np.zeros(img.shape, np.uint8)

        _, thresh = cv2.threshold(img, 127, 255, 0)

        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

        iters = 0
        while (True):
            cv2.erode(thresh, kernel, eroded)
            cv2.dilate(eroded, kernel, temp)
            cv2.subtract(thresh, temp, temp, dtype=cv2.CV_8UC1)
            cv2.bitwise_or(skeleton, temp, skeleton)
            thresh, eroded = eroded, thresh  # Swap instead of copy

            iters += 1
            if cv2.countNonZero(thresh) == 0:
                return skeleton

    """
    Benchmark
    """
    def before_benchmark(self):
        self.load_images_from_folder(self.bench_folder, self.bench_data)