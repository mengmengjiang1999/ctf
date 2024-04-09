import base64

byte1=b'\xA8h\xADm\xFB+\xFC\x90;\xDD\xDC:\x93\xED\x37\x89'

string1 = "18AtF9QM=ehJpNiZDRoIG/EwkT364yfs+PbaYvLg7uldrxBVC0njX2KWS5mUHqOcz" #修改之后的base64表
string2 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="

# 现在存在一个字符串，换表解密后等于byte1

print(byte1)

# 直接base64加密
encoded=base64.b64encode(byte1)
print(encoded)
# 得到加密后的结果
assert(base64.b64decode(encoded)==byte1)
# 加密后再解密等于原来的字符串


# 加密后的结果变成string并换表
encoded_str=encoded.decode()
print(encoded_str)
trans=encoded_str.translate(str.maketrans(string2,string1))
print(trans)
# trans



# 用step1中的解密操作进行验证
print(trans.translate(str.maketrans(string1,string2)))
print(base64.b64decode(trans.translate(str.maketrans(string1,string2))))
