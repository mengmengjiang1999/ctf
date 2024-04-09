import base64

str1 = "FlZNfnF6Qol6e9w17WwQQoGYBQCgIkGTa9w3IQKw"

string1 = "JKLMNOxyUVzABCDEFGH789PQIabcdefghijklmWXYZ0123456RSTnopqrstuvw+/"#修改之后的base64表
string2 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

print(len(string1))
print(len(string2))

print (base64.b64decode(str1.translate(str.maketrans(string1,string2))))