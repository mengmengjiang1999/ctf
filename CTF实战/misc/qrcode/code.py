from pyzbar.pyzbar import decode
from PIL import Image
decocdeQR = decode(Image.open("./code.png"))
print(decocdeQR)
print(decocdeQR[0].data.decode())