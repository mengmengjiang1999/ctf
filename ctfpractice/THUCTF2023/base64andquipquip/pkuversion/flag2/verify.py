import base64


# JKLMNOxyUVzABCDEFGH789PQIabcdefghijklmWXYZ0123456RSTnopqrstuvw+/

# print(base64.b64decode("ZmxhZ3tXMzFjMG1lX1QwX0JhczN9AA==0"))


str1="AlvcA3hVLaFxLP1yV1KnV0XcqaI9WW==0"

string1 = "WEQJDFPCBXGYLIZTKUSHRMNVOAweqjdfpcbxgyliztkushrmnvoa0123456789+/"#修改之后的base64表
string2 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

print(len(string1))
print(len(string2))

print(base64.b64decode(str1.translate(str.maketrans(string1,string2))))

