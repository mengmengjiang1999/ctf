# 2018 海南省大学生网络安全攻防竞赛部分 WriteUp

阅读量 **303312**

|评论 **7**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-12-26 14:30:53

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t011b01a7b66b5c571f.gif)

## 0x00 Welcome

签到题。查看源码，拿到 flag

![](https://i.imgur.com/xBIATHk.png)

## 0x01 code php

无提示，御剑扫描拿到index.php2（确实挺坑的）

![](https://i.imgur.com/7HXlSaF.png)

弱类型比较，payload如下（ **数组绕过** ）

    
    
    http://211.149.128.46:20001/b8379a669f5cbf18/7/?key[]=1
    

![](https://i.imgur.com/RoRjp0m.png)

## 0x02 Dearm II

提示的很清楚， **put 方法提交一个 message** （方法体中提交 message）

![](https://i.imgur.com/yyUEroY.png)

抓包。repeater，看到了一个 base64 加密的 flag，解码即可

![](https://i.imgur.com/UgtnjpK.png)

![](https://i.imgur.com/igNNOdF.png)

## 0x03 include

抓包找到关键数据包， **看样子应该是文件包含。**

![](https://i.imgur.com/eKSdeLl.png)

尝试包含 include1.php 的源码，这里有一个 flag.php，但是被过滤了。提示了一个 include2.php 文件。

![](https://i.imgur.com/NJDYp6g.png)

拿到 include2.php 的源码， **发现 include2.php 的可以利用**

![](https://i.imgur.com/uyz8gHZ.png)

但是过滤了 base 关键字，没办法使用 base64 编码读出来 flag.php。但是可以使用 **rot13（string.rot13）**

![](https://i.imgur.com/LcdP64m.png)

可以参考这里：

<http://www.php.net/manual/zh/wrappers.php.php>

payload:

    
    
     /e9f5af7deaa28563/11/include2.php?file=php://filter/read=string.rot13/resource=flag
    

最后 rot13 解码还原即可

flag{79ac2d3112c633687a2447dbb1dc11b2}

## 0x04 数据包分析

2018 红帽杯原题

<https://www.freebuf.com/column/171641.html>

wireshark打开，发现是个压缩包的十六进制流的拼接

![](https://i.imgur.com/jO2OTrk.png)

使用 tshark 提取出来数据

    
    
    tshark -r x.pcapng -e http.request.uri -T fields -Y 'http.request.uri' | grep -P 'name=[A-F0-9]{3}' | awk -F '=' '{printf $2}'
    

![](https://i.imgur.com/37Z9urC.png)

仔细观察是一个 zip 压缩包。改一下前面的十六进制：

    
    
    504B03040A0001080000739C8C4B7B36E495200000001400000004000000666C616781CD460EB62015168D9E64B06FC1712365FDE5F987916DD8A52416E83FDE98FB504B01023F000A0001080000739C8C4B7B36E4952000000014000000040024000000000000002000000000000000666C61670A00200000000000010018000DB39B543D73D301A1ED91543D73D301F99066543D73D301504B0506000000000100010056000000420000000000
    

发现出来的压缩包有密码，在源数据包中找到

![](https://i.imgur.com/EQrTJsg.png)

    
    
    key=1128%23
    

输入密码得到 flag

    
    
    flag{tsh4rk_1s_C00l}
    

## 0x05 MIX

下载下来解压出来是一个 .git 的文件夹

![](https://i.imgur.com/6aCWeax.png)

在自己的服务器上部署， **使用 githack 把源码 dump 下来** （貌似可以直接搞出来？）

![](https://i.imgur.com/ri0NmdD.png)

一个加密的 key.zip 加上一个 没用卵用的 tishi

![](https://i.imgur.com/ZAPSXKR.png)

拿到zip文件，测试伪加密，拿到flag

![](https://i.imgur.com/V68nEJd.png)

## 0x06 Wireshark

过滤出 http 流， **发现了一个 8950 的十六进制开头的 png 图片** ，提取出来

![](https://i.imgur.com/KvTibbu.png)

在协议分级中找到 Line based 的流，作为过滤器过滤出来。

![](https://i.imgur.com/QScr6KW.png)

发现是个 rar 压缩文件。 **这里右键显示明文分组，使用原始数据提取**

使用脚本将十六进制数据写到一个 Rar 文件中。

    
    
    # -*- coding: utf-8 -*-    
    s = '2d3e7c526172211a0700cf907300000d00000000000000be0f7420902e0031510000326f000002560a16400ba77c471d3309002000000068656c6......fbac943fe86dff0bfc3ec9dfebfd20f276b72fb6425246cd7ecceb3ed9df1d1e73246a768725760750e76c8fcb00a929a97fe0413fc2fbff10c43d7b004007007c3c2d'
    f = open('shu.rar', 'wb')
    hex_s = s.decode('hex')
    f.write(hex_s)
    f.close()
    

解压出来拿到一张图片，总共两张 png 图片，flag 的各一半，拼接拿到 flag

![](https://i.imgur.com/5rxvjqE.png)

flag{c7265f898a52fcc4}

## 0x07 caesar N

题目只给了一个凯撒加密的变种字符串。

![](https://i.imgur.com/mHHJduV.png)

仔细观察结构，发现前面是 66 6c 61 67 对应着 flag 的 ascii 码

e 对应 7 ，往回推 f 对应 6 ，b 对应 3。对应好之后解码即可。

<https://wishingstarmoye.com/tools/ascii>

![](https://i.imgur.com/XB7rcVS.png)

## 0x08 美丽

Foremost 分解出文件：

![](https://i.imgur.com/PeDZNmQ.png)

**原来猜想是盲水印攻击** ，但是两张是格式不同的图片，所以搞不了。

后来经过学长提示 **可以使用 compare 命令试试**

compare 命令的解释：

<http://blog.chinaunix.net/uid-24109725-id-2629869.html>

**Compare 对比：生成的图片就是出现差异的数据**

![](https://i.imgur.com/9d1H1Sv.png)

出现二维码

![](https://i.imgur.com/W1FNnCW.png)

扫描得到 flag

## 0x9 迷失的flag

十六进制工具 winhex 打开发现最后面有一个压缩文件

![](https://i.imgur.com/tFD6BwY.png)

**foremost 命令将其中的文件提取出来** ，出来一个 flag.txt

打开，&#x 后面是十六进制，编码出来是 Unicode 编码

![](https://i.imgur.com/G0jDd4a.png)

**发现是unicode码** ，继续解码

![](https://i.imgur.com/qfMXvW5.png)

或者也可以直接提取出 ascii 码，直接在这里继续解码

<https://wishingstarmoye.com/tools/ascii>

![](https://i.imgur.com/Gx2FSjb.png)

flag{b5e750114efb68791330f3af70cd8fc0}

## 0x10 rot

rot13解码，使用工具解码

![](https://i.imgur.com/AmVTPXc.png)

## 0x11 解密

**栅栏密码解密**

![](https://i.imgur.com/E5FBJVe.png)

## 0x12 Easy

IDA 打开，算法逆向

![](https://i.imgur.com/o2OmlnM.png)

直接写逆向脚本，解 flag

![](https://i.imgur.com/f1MnQm8.png)

![](https://i.imgur.com/WBj1CKB.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **H4lo** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/168480](/post/id/168480)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __8赞

 __收藏

![](https://p2.ssl.qhimg.com/t0129eee7c67478558f.jpg) H4lo

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

