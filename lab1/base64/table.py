table="18AtF9QM=ehJpNiZDRoIG/EwkT364yfs+PbaYvLg7uldrxBVC0njX2KWS5mUHqOcz"


import base64

str1 = "TL0PTWxbkwNvNaRsyMeP6gNrkwRvwWRPkL0vwKNP6vqbT/qa3Q9BTK/YsDzz"

string1 = "18AtF9QM=ehJpNiZDRoIG/EwkT364yfs+PbaYvLg7uldrxBVC0njX2KWS5mUHqOcz"#修改之后的base64表
string2 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="

print(len(string1))
print(len(string2))

# for item in string1:
#     print(item)

# dict1={}

# for item in string1:
#     if item not in dict1.keys():
#         dict1[item]=1
#     else:
#         dict1[item]=dict1[item]+1
# print(dict1)
print(base64.b64decode(str1.translate(str.maketrans(string1,string2))))