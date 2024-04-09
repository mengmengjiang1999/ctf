import math
v3=[""]*3
v3[0] = "Dufhbmf"
v3[1] = "pG`imos"
v3[2] = "ewUglpt"
string=""
for i in range(12):
    # print(v3[i % 3][2 * int(i / 3)])
    # print(math.ceil(2 * (i / 3)))
    
    string+=chr(ord(v3[i % 3][math.ceil(2 * (i / 3))])-1)
print(string)