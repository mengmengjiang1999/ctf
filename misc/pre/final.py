import numpy as np
from PIL import Image
import io
import base64


path1="./origin.png"
path2="./mix.png"

image1=Image.open(path1)
image2=Image.open(path2)
image_array1=image1.load()
image_array2=image2.load()


def image2bytes(image):
    img_bytes=io.BytesIO()
    image.save(img_bytes,format="png")
    image_bytes=img_bytes.getvalue()
    return image_bytes
    
def byte2image(byte_data):
    image=Image.open(io.BytesIO(byte_data))
    return image


image_origin_bytes=bytearray(image2bytes(image1))

image_mix_bytes=bytearray(image2bytes(image2))
image_mix_bytes=bytearray(image2bytes(image2))
# print(image_mix_bytes)
image_mix_bytes.reverse()

# print(image_mix_bytes)
# print(image_origin_bytes+image_mix_bytes)

image_byte=image_origin_bytes+image_mix_bytes

finalimage=bytes(image_byte)

with open("final","wb") as file:
    file.write(finalimage)

# finalimage=byte2image(bytes(image_byte))

# finalimage.save("./final.png",quality=100)