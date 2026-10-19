# 七夕—一例APT28（Fancybear）样本详细分析

阅读量 **221848**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-08-26 14:30:37

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t013c20b81e4d35c6ff.jpg)

## 0x00 背景

APT28是一个疑似具有俄罗斯政治背景的APT组织。笔者根据公开的情报整理到的信息大概如下。

![](https://p4.ssl.qhimg.com/t0101deebdedf3d14e6.png)

本次的样本来源于沙箱app.any.run:<https://app.any.run/tasks/d6a8d1db-52c8-4371-b6d3-bf740408bb10/>

上传到app.any.run的时间为2020年7月27.

![](https://p3.ssl.qhimg.com/t01efdcb7815c3d7b0e.png)

可以看到样本已经标记为了APT28  
样本MD5为：36524c90ca1fac2102e7653dfadb31b2

## 0x01 样本基本信息

样本下载到本地之后通过exeinfo查看样本可以知道样本是标准VC编译的程序。

![](https://p2.ssl.qhimg.com/t01540651d5b3480316.png)

使用火绒剑和fakenet跑一下样本的行为：

![](https://p4.ssl.qhimg.com/t017b5b776e71bea91c.png)

样本运行后，最直接的行为就是在本地appdata路径释放了一个dll文件和一个bat文件，然后在左边的fakenet窗口中可以看到发送了超级长的一段base64编码数据，这次猜测可能是通过base64编码了本地收集到的信息然后传到C2.

![](https://p1.ssl.qhimg.com/t0105791d182d59306b.png)

转到bat和dll文件的目录下，可以看到bat的内容就是调用rundll32.exe去启用加载这个dll。

![](https://p5.ssl.qhimg.com/t015d620e4ef183a032.png)

所以看样子，我们拿到的这个exe有很大的概率是一个Dropper。

## 0x02 Dropper分析

使用IDA加载原始样本。

![](https://p5.ssl.qhimg.com/t0103d043927b51d736.png)

WinMain的入口点没什么特殊的，进来之后调用了三次sub_401DEF函数，这种情况下，sub_401DEF一般都是解密函数。

![](https://p1.ssl.qhimg.com/t016cec83fa4d968061.png)

解密的第一个字符串是SystemRoot\SysWow64

第二个串是SystemRoot\SysWow64

第三个串是：TEMP

![](https://p5.ssl.qhimg.com/t016e8ce397615558df.png)

所以我们将sub_401DEF函数重命名为：Rename_decodeStr

三个字符串解密之后，程序会再调用一个名为sub_4012D3的函数，这个函数如果调用失败，程序将通过jmp跳转到最后结束运行。所以sub_4012D3有可能是进行环境校验啥的。

![](https://p2.ssl.qhimg.com/t01b9fa9f7a136eb1ec.png)

###  WinMain->12d3

12D3函数进来之后，首先会通过GetProcessHeap获取当前进程的堆地址，然后通过HeapAlloc分配一个堆空间。

![](https://p1.ssl.qhimg.com/t016003e484ae8f539b.png)

成功分配之后，程序会调用sub_401063继续分配

![](https://p0.ssl.qhimg.com/t01e4453c1b5fd1e8f6.png)

然后在分配的堆空间中解密出这个dll名称

![](https://p1.ssl.qhimg.com/t01a11e210aa5d1f204.png)

第二次解密出appdata这个环境变量的名称

![](https://p3.ssl.qhimg.com/t017572077d492b8088.png)

12D3函数执行完成之后，程序会调用执行sub_4013F7

###  WinMain->13F7

该函数进来，程序首先是通过之前分析的解密函数，解密了两个解压相关的API:

RtlGetCompressionWorkSpaceSize  
RtlDecompressBuffer

这里应该是为等会释放文件做准备了。

![](https://p2.ssl.qhimg.com/t0104961dd91a5d77b9.png)

然后LoadLibrary之后通过GetProcAddress获取刚才解密出来的API函数的地址

![](https://p5.ssl.qhimg.com/t01666a345700fd2263.png)

然后直接调用该函数，参数为eax：

![](https://p2.ssl.qhimg.com/t0114a952f6e4857b2f.png)

然后调用了RtlDecompressBuffer，根据参数来看，这里应该是会将目标数据解压缩到esi所在的地址

![](https://p4.ssl.qhimg.com/t01167ccaa15595e810.png)

函数执行之后成功解压出一个PE

![](https://p4.ssl.qhimg.com/t0174753e3a7402057d.png)

![](https://p3.ssl.qhimg.com/t019f6bb8b27a8a3999.png)

至此，sub_4013F7函数功能分析完毕，经过分析，该函数用于解压缩数据为PE文件。

接下来是调用sub_40155B函数。

###  WinMain->155B

在115B函数中，程序首先执行了一个call ，然后就准备LoadLibrary

![](https://p3.ssl.qhimg.com/t014557963e33615f71.png)

**155B->sub_4010CD**

跟进到sub_4010CD中，程序首先是解密了两个字符串，分别是SystemRoot和\System32

然后就尝试通过GetEnvironmentVariableW获取LOCALAPPDATA环境变量的路径。

![](https://p1.ssl.qhimg.com/t0168e1a44a74dec91f.png)

成功获取，根据行为分析我们可以知道，这个路径是后续用于释放文件的。

![](https://p4.ssl.qhimg.com/t016a06a5f39a15c50f.png)

然后尝试通过lstrcatW拼接字符串，获取更完整的路径。

![](https://p2.ssl.qhimg.com/t01eeaf33f02dbe2cfe.png)

最后拼接出解密dll的完整路径：

至此，sub_4010CD函数分析完成，我们回到1565B函数中

程序是通过了拆分字符串的方式，组装出了Kernel32.dll

![](https://p5.ssl.qhimg.com/t01400afba467748aab.png)

然后准备调用CreateFileW

![](https://p5.ssl.qhimg.com/t01a7c354cf351d0dbf.png)

成功获取API地址之后，程序首先跳转到loc_4016E3去，然后通过jmp函数又跳转回来继续执行。

![](https://p0.ssl.qhimg.com/t016daced2833fe05eb.png)

跳回来之后，程序通过CreateFile创建这个dll的文件对象。

![](https://p0.ssl.qhimg.com/t01abbc26783a1ad1ba.png)

同样的方式，去获取WriteFile的API地址：

![](https://p3.ssl.qhimg.com/t015ca67bdce1daf51e.png)

然后调用WriteFile将dll文件写入过去：

![](https://p2.ssl.qhimg.com/t01a4534ebe8963c273.png)

这里是文件对象创建成功

![](https://p2.ssl.qhimg.com/t01ae8316d7636bb15b.png)

这里是closeHandle之后，dll文件写入成功。

![](https://p3.ssl.qhimg.com/t01d4fde17464cd61bc.png)

到这里，sub_40155B函数就分析完成。

通过分析我们可以知道，该函数的主要功能是解压缩资源，释放目标dll文件到指定的目录。

回到WinMain中，155B函数调用完成之后，程序会调用sub_40264C函数。

### **WinMain->264C**

264c函数进来之后就一直在解密字符串：

![](https://p4.ssl.qhimg.com/t01f438c1002cbfa63b.png)

解密的第一个字符串是rundll32.exe

![](https://p4.ssl.qhimg.com/t011163dcde6e257cbb.png)

解密出来的字符串分别如下：

![](https://p2.ssl.qhimg.com/t0168561bb717f4327a.png)

然后老套路解密出了操作注册表的API:RegOpenKeyExw

![](https://p2.ssl.qhimg.com/t01d919c5c5607cc5c7.png)

然后循环的去调用之前的解密函数，逐步解密出bat的完整内容

![](https://p1.ssl.qhimg.com/t01e147c543be003ca0.png)

尝试通过CreateFileA创建文件：

![](https://p2.ssl.qhimg.com/t01d149d6c7e4face30.png)

![](https://p1.ssl.qhimg.com/t012b41a6af9150f99d.png)

文件对象创建成功之后，将调用执行dll的命令写入进去：

![](https://p1.ssl.qhimg.com/t01e3f3b32ceb2bdcb1.png)

写入成功之后就是一系列的收尾工作：

![](https://p4.ssl.qhimg.com/t0122a72f224ab65193.png)

到这里，sub_402030函数分析完成，该函数的主要功能就是将启动dll的命令写入到bat文件中。

![](https://p1.ssl.qhimg.com/t015eb7fbe4cecf770a.png)

然后创建一个UserInitMprLogonScript的注册表，这是一种用于权限维持的操作。因为HKEY_CURRENT_USER\Environment\  
Logon Scripts 的执行顺序在杀软钱，所以Logon Scripts可以优先于杀软执行，绕过杀软对敏感操作的拦截。

![](https://p2.ssl.qhimg.com/t01c5d78a4dc05d79df.png)

到这里，264C函数也执行完毕。

该函数的主要功能就是释放bat文件，然后写入Logon Scripts注册表以绕过杀软。

接下来是在WinMain中调用sub_401707函数：

![](https://p3.ssl.qhimg.com/t018f78136224364e4a.png)

###  **WinMain- >1707**

1707进来之后首先是解密了三个字符串，分别是RunDll32.exe ,#1 和Open

![](https://p3.ssl.qhimg.com/t0147d6f5be8b719023.png)

接着call到了sub_401D09中。该函数用于获取进程的一个执行权限

![](https://p4.ssl.qhimg.com/t0139521d0a476e1f02.png)

获取之后，程序会带参数加载这个dll文件。

![](https://p3.ssl.qhimg.com/t01d370ee1103aad142.png)

这里加载执行之后，程序就会做一些收尾操作，然后退出当前的程序了。

这里程序其实配置了多种启动方式，感兴趣的可以看下。

最后，程序尝试通过DeleteFile删除自身

![](https://p0.ssl.qhimg.com/t017f9e3ef0f00d02ab.png)

到这里，Dropper这个程序就完全分析完成。

## 0x03 cdnver.dll分析

释放出来的这个dll就是APT28的特马。

该样本功能非常完善，包括信息收集、信息上传、下载、执行PE、截屏等。

网上关于该木马的分析报告还挺多的，这里就随便看一下，且因为篇幅的原因，也不能写太长啦~
这就是一个标准的远控木马，没有什么混淆，有一些自定义的解密函数，跟着调试很快就可以调试完。

使用IDA加载该dll，由bat文件中的执行指令可以知道，程序调用该dll的时候，是执行了序号为1的导出函数。  
start rundll32.exe “C:\Users\Administrator\AppData\Local\cdnver.dll”,#1

![](https://p2.ssl.qhimg.com/t01061d9c57bfc750c3.png)

该函数结构非常简单，进来直接就是CreateThread执行了sub_10002CA0，这里是该特马的入口点。

![](https://p5.ssl.qhimg.com/t01b98262cd8c11243b.png)

###  #1->2ca0

2CA0进来调用的第一个函数是sub_10002CFD

![](https://p5.ssl.qhimg.com/t011d255c9adfc32b4d.png)

###  sub_10002CFD

程序首先是通过10002F3F解密得到了一个互斥体名，然后通过CreateMuteA创建互斥体。

![](https://p4.ssl.qhimg.com/t0161d8137e460d8672.png)

![](https://p1.ssl.qhimg.com/t01e9321108387ea19c.png)

通过gethostbyname获取当前的主机名：

![](https://p4.ssl.qhimg.com/t01e93054279f84c260.png)

通过GetVolumeInformationW获取磁盘信息：

![](https://p3.ssl.qhimg.com/t0144f5f8a687c7d420.png)

调用obtainUserAgentString检索当前的User-Agenet HTTP请求标头字符串。

![](https://p3.ssl.qhimg.com/t011d279b3bf46817ef.png)

![](https://p3.ssl.qhimg.com/t013247eea27b18b67c.png)

打开：Software\Microsoft\Windows\CurrentVersion\Internet
Setting\Servers注册表键值，将C2信息加密后存储在这个键值的Domain项中。

![](https://p0.ssl.qhimg.com/t01668226f9cc89a3b1.png)

解密出域名：cdnverify.net

![](https://p3.ssl.qhimg.com/t011f6222de59bc6fa6.png)

该域名是apt28的经典域名

![](https://p0.ssl.qhimg.com/t01cb09cce047168226.png)

将接下来要请求的信息base64编码，方便之后传输。

![](https://p2.ssl.qhimg.com/t012c7660a0023418ad.png)

首先对google发起网络请求，确保网络畅通。

![](https://p0.ssl.qhimg.com/t0188ed4d653d107166.png)

样本会来回在googl和真实的c2之间来回切换通信，达到隐藏通信的目的。

该样本中使用的是标准的HttpSendRequestA系列API进行网络请求：

![](https://p4.ssl.qhimg.com/t01ed4b169c68384ec0.png)

发送数据之后，程序会通过InternetReadFile接收并解析返回值。

![](https://p2.ssl.qhimg.com/t01bba9aa82c37e9110.png)

关于cdnver.dll就分析到这里。感兴趣的小伙伴可以到app.any.run上下载该样本到本地继续分析。

## 0x04 总结

经过分析，可以看到这是一个apt28的老样本，Dropper释放出来的payload就是经典的APT28远控木马。现在他们更常用的payload是由Dephi编写的Zebrocy，后面有机会再分享给大家。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **jux1a** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/215184](/post/id/215184)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [APT28](/tag/APT28)

 **+1** __4赞

 __收藏

![](https://p0.ssl.qhimg.com/t01c900f6a705a10464.png) jux1a

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

