from .profiler import Profiler
import base64
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import requests


class ResnetProfile(Profiler):
    URLS_FILE = "resnet_urls_50.txt"

    def before_profiling(self):
        self.load_images_from_urls()
        # self.load_request_from_file()
        self.warm_up_model(self.bench_data[0])

    def after_profiling(self):
        self.logger.info("avg response times %s", self.avg_times)

        # plot response time graph
        plt.hist(self.avg_times)
        plt.show()

    def load_images_from_urls(self, show_imgs=False):
        f = open(self.bench_folder + "/" + self.URLS_FILE, "r")
        for url in f:
            self.logger.info("downloading %s", url.strip())
            try:
                dl_request = requests.get(url, stream=True)
                dl_request.raise_for_status()

                if show_imgs:
                    im = Image.open(BytesIO(dl_request.content))
                    plt.imshow(im)
                    plt.show()

                # Compose a JSON Predict request (send JPEG image in base64).
                self.logger.info("composing the req for %s", url.strip())
                jpeg_bytes = base64.b64encode(dl_request.content).decode('utf-8')

                predict_request = {"instances": [{"b64": str(jpeg_bytes)}]}
                self.bench_data.append(predict_request)

            except Exception as e:
                self.logger.error("Exception %s", e)

        f.close()
