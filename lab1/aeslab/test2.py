
byte_2080=bytes.fromhex('''
2F 55 D7 6A 4B FA 36 AC  7B 48 A0 AE 9B FB A8 E8
D4 8D 68 06 99 CA 92 E1  5F E6 F5 04 45 D0 C3 CB
89 69 17 DB C3 CF AA 5C  74 C5 8E 23 95 F9 56 6E
76 15 36 C5 1F 11 05 F1  2C 7D 11 35 E6 CA BA 17''')

unk_4010=bytes.fromhex('''A8 68 AD 6D FB 2B FC 90  3B DD DC 3A 93 ED 37 89''')

# 输入不知道什么东西
# 先进行base64解密得到v11
# 然后AES密钥是unk_4010，用密钥解密v11得到的结果是byte_2080


# b'qGitbfsr/JA73dw6k+03iQ=='
# qGitbfsr/JA73dw6k+03iQ==
# lQbx6srdce1UWyCmYOXWbDzz
# qGitbfsr/JA73dw6k+03iQ==
# lQbx6srdce1UWyCmYOXWbDzz