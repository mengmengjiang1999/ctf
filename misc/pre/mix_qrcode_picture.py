import numpy as np
from PIL import Image


path1="./origin.png"
path2="./qr.png"
path3="./mix.png"

image1=Image.open(path1)
image2=Image.open(path2)
image_array1=image1.load()
image_array2=image2.load()

print(image1.size)
print(image2.size)

for i in range(image2.size[0]):
    for j in range(image2.size[1]):
        # print(image_array2[i,j])
        if image_array2[i,j]==0:
            print(i,j)
            origin=image_array1[i,j]
            print(image_array1[i,j])
            image_array1[i,j]=(origin[0]+1,origin[1],origin[2])
            print(image_array1[i,j])

image1.save(path3,quality=100,subsampling=0)