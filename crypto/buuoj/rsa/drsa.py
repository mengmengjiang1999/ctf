n=int('0x52d483c27cd806550fbe0e37a61af2e7cf5e0efb723dfc81174c918a27627779b21fa3c851e9e94188eaee3d5cd6f752406a43fbecb53e80836ff1e185d3ccd7782ea846c2e91a7b0808986666e0bdadbfb7bdd65670a589a4d2478e9adcafe97c6ee23614bcb2ecc23580f4d2e3cc1ecfec25c50da4bc754dde6c8bfd8d1fc16956c74d8e9196046a01dc9f3024e11461c294f29d7421140732fedacac97b8fe50999117d27943c953f18c4ff4f8c258d839764078d4b6ef6e8591e0ff5563b31a39e6374d0d41c8c46921c25e5904a817ef8e39e5c9b71225a83269693e0b7e3218fc5e5a1e8412ba16e588b3d6ac536dce39fcdfce81eec79979ea6872793',16)
e=3
c=int('0x10652cdfaa6b63f6d7bd1109da08181e500e5643f5b240a9024bfa84d5f2cac9310562978347bb232d63e7289283871efab83d84ff5a7b64a94a79d34cfbd4ef121723ba1f663e514f83f6f01492b4e13e1bb4296d96ea5a353d3bf2edd2f449c03c4a3e995237985a596908adc741f32365',16)


print(n)
print(e)
print(c)

from decimal import *

# https://docs.python.org/3/library/decimal.html
c = Decimal(c)
e = Decimal(e)

getcontext().prec = 500 # Set a big enough precision
root = pow(c, 1/e) # Calculate c^(1/e) = m^(e * 1/e) = m
print(root)

# Decode with no padding
m = hex(int(root))[2:-1] # Number to hex
m = ''.join(chr(int(m[i:i+2], 16)) for i in range(0, len(m), 2)) # Hex to Ascii
print(m)