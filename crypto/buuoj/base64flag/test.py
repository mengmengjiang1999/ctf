import base64

str1 = "aWRiaq3QBTOkBxomQoF6QnVidTCwJJ==0"
# str1="aWRiaq3QBTOkBxomQoF6QnVidTCw0"


string1 = "JKLMNOxyUVzABCDEFGH789PQIabcdefghijklmWXYZ0123456RSTnopqrstuvw+/"#修改之后的base64表
string2 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

flag="flag{W31c0me_T0_Bas3}"

print(len(string1))
print(len(string2))

print (base64.b64decode(str1.translate(str.maketrans(string1,string2))))

# print(base64.b64encode(flag.translate(str.maketrans(string1,string2))))