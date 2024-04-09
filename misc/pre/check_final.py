import numpy as np
from PIL import Image

import io


path1="./final"

with open(path1,"rb") as file:
    png=file.readlines()
    print(png)

# image1=Image.open(path1)
# image_array1=image1.load()

# def image2bytes(image):
#     img_bytes=io.BytesIO()
#     image.save(img_bytes,format="png")
#     image_bytes=img_bytes.getvalue()
#     return image_bytes

# byte_final=image2bytes(image1)

# print(byte_final)