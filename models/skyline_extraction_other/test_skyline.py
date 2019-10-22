import matplotlib.image as img
import requests
import numpy as np


def convert_float_output_to_mat(buffer, height, width):
    # Mat result = new Mat(height, width, CvType.CV_8UC1);
    result = np.zeros((height, width))

    row = col = 0
    for row in range(0, height):
        for col in range(0, width):
            val = int(buffer[row * width + col][1] * 255)
            result[row][col] = val

    return result


file_name = "test_2.jpg"
image = img.imread(file_name)

print(image.shape)

js = {"instances": [image.tolist()]}
response = requests.post("http://localhost:8501" + "/v1/models/" + "skyline2" + ":predict", json=js)
response.raise_for_status()
print(response.json())

img_out = response.json()["predictions"]
output = convert_float_output_to_mat(img_out, 53, 73)

img.imsave("export.jpg", output)
