import numpy as np
from PIL import Image


path1="./qr.jpg"
path2="./qr.png"


image1=Image.open(path1)

image1.save(path2,format='png',quality=100)