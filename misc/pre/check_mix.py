import numpy as np
from PIL import Image


path1="./origin.png"
path2="./qr.png"
path3="./mix.png"
path4="./qr_get.png"


image1=Image.open(path1)
image2=Image.open(path2)
image3=Image.open(path3)
image_array1=image1.load()
image_array2=image2.load()
image_array3=image3.load()

image4=Image.new(mode="RGBA",size=image1.size)
image_array4=image4.load()

assert(image1.size==image3.size)

for i in range(image1.size[0]):
    for j in range(image1.size[1]):
        if image_array1[i,j]==image_array3[i,j]:
            # pass
            image_array4[i,j]=(255,255,255)
            print(image_array1[i,j])
        else:
            print(i,j)
            image_array4[i,j]=(0,0,0)
            
image4.save(path4)