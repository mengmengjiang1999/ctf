## **一、前言**

自病毒木马诞生起，杀毒软件与病毒木马的斗争一直都没有停止过。从特征码查杀，到现在的人工智能查杀，杀毒软件的查杀技术也是越来越复杂。但是病毒木马却仍然层出不，这是因为大部分病毒木马使用了免杀技术。

免杀技术全称为反杀毒技术（Anti Anti-Virus），简称“免杀”，指的是一种能使病毒木马免于被杀毒软件查杀的技术。不管是钓鱼攻击，还是Web渗透，对使用的病毒木马进行免杀处理，都是必不可少的操作。

在某次网络攻防演练期间，我们捕获了一个免杀样本，主要使用了“LOLBins”免杀技术。 **这篇文章将对该样本进行分析，以此揭开此类免杀技术的神秘面纱。**

##  **二、LOLBins概述**

LOLBins，全称为“Living-Off-the-Land Binaries”，这个概念最初在2013年DerbyCon黑客大会由Christopher
Campbell和Matt Graeber创造，最终由Philip
Goh提出。指的是在目标操作系统上运行受信任的合法进程来执行恶意活动，例如横向移动、权限提升和远程控制等。

通俗来讲，就是大家所熟悉的“白名单”免杀技术。比如常见的Powershell.exe、Certutil.exe和Mshta.exe等程序，都属于LOLBins范畴。在一些APT攻击中，也可以看到使用LOLBins免杀技术进行攻击的活动。比如，海莲花APT组织曾使用微软操作系统自带的程序MSBuild.exe运行远程控制木马，达到免杀的效果。为了达到比较好的免杀效果，LOLBins的选取是有一定要求的。一般来说，需要包含如下特征：

1) 带有Microsoft签名或者第三方签名的程序。

2) 具有可被用于利用的功能（比如上传、下载和代码执行等）。

##  **三、免杀原理**

 **LOLBins为什么可以达到免杀效果？**

在解答这个问题之前，我们先了解下杀毒软件的查杀原理。一般来说，杀毒软件对一个文件会采用多种方法进行查杀。大约可以分为两大类：静态查杀和行为查杀。

 **静态查杀** 主要包含病毒特征码、文件属性（HASH、图标、开发者信息）等查杀，指未运行样本采用的文件扫描技术； **行为查杀**
主要包含沙箱模拟执行、主动防御和人工智能等查杀，是基于程序行为进行分析判断，多端联动的查杀技术。例如，样本刚“落地”就被杀毒软件查杀了，说明被静态查杀了；如果样本运行起来了，执行某些操作时被查杀了，说明此时样本的危险行为被杀毒软件检测到了。

 **为什么LOLBins文件可以实现免杀？**
这是因为LOLBins一般是正常的程序，对杀毒软件而言，是可信任的程序，所以基本上可以躲过杀毒软件的静态查杀。至于行为查杀，每种杀毒软件的实现、查杀策略多有不同。有的只要是可信任的程序，即使有高危行为也不予查杀；有的则相反，不管是不是可信任的程序，只要有高危行为，也会被查杀。

总的来说，从以下几个方面进行处理，可以实现较好的免杀效果：

1、文件特征

2、内存特征

3、程序行为

4、网络通信

选用LOLBins程序，基本不用考虑文件特征，直接静态免杀，这个是比较好的免杀思路。如果使用流行的黑客工具或者木马，需要对内存中的代码进行加花、混淆，避免内存特征被检测到。对于程序的行为，需要对选取的LOLBins程序进行测试，如果高危行为被查杀了，可以考虑使用其他的LOLBins程序执行高危操作。

网络通信数据避免使用明文，使用加密算法等进行加密，远程服务器尽量伪装为正常的服务器，必要时可以采用CDN，域前置，云函数等手法隐藏服务器IP。

试想，整个恶意活动全程使用LOLBins，形成LOLBins利用链，杀毒软件会报毒吗？

##  **四、逆向分析**

到目前为止，我们已经知道如何免杀的理论知识了。那么接下来逆向分析这个免杀样本，并借鉴它的方法，自己动手实现免杀。

样本名为LiveUpdate.exe，MD5:9050ac019b4c8dddbc5e250bb87cf9f2，这是NetSarang公司XSHELL、XFTP、XMANAGER、XLPD系列工具的更新程序，数字签名正常，如下图所示：

![](https://image.3001.net/images/20221129/1669685141_63855f9580eabc277d3f0.png!small)

该样本早在2020年被上传到某些在线威胁情报平台进行检测，可能很早就被作为LOLBins进行利用，如下图所示：

![](https://image.3001.net/images/20221129/1669685167_63855faf8cd48796c13a2.png!small)样本运行后，会加载同目录下后缀为dat的同名文件，也就是LiveUpdate.dat，然后解密该文件，解析其中的脚本代码并执行，完成软件更新。LiveUpdate.dat实际上是一个zip压缩文件，解压密码为99B2328D3FDF4E9E98559B4414F7ACB9，如下图所示：

![](https://image.3001.net/images/20221129/1669685197_63855fcdf23e643e7b03a.png!small)![](https://image.3001.net/images/20221129/1669685205_63855fd50dad049fabf29.png!small)解压成功后，得到5个文件：_TUProj.dat、_TUProjDT.dat、IRIMG1.JPG、IRIMG2.JPG、IRIMG3.JPG、和IRIMG4.JPG。执行的脚本在_TUProj.dat文件中，如下图所示：

![](https://image.3001.net/images/20221129/1669685224_63855fe8d2e5acb20f456.png!small)

可以看出，这是Lua脚本语言。这个更新程序实际上是一个Lua脚本解析执行引擎，可以自定义Lua代码，实现文件上传、下载，进程管理，注册表管理，服务管理，命令执行等功能，完全可以作为LOLBins，实现免杀。

样本中将CS远程控制木马的Shellcode转化为数字存放在数组中，如下图所示：

![](https://image.3001.net/images/20221129/1669685250_63856002686b0c689bf51.png!small)然后使用DLL.CallFunction函数调用Windows原生API函数VirtualAlloc，在内存中申请新的空间存放木马的Shellcode，如下图所示：

![](https://image.3001.net/images/20221129/1669685268_63856014b91925068364d.png!small)最后调用CreateThread函数创建新线程运行木马Shellcode，实现远程控制的功能。其中还加入了正常的网络请求，混淆网络通信，如下图所示：

![](https://image.3001.net/images/20221129/1669685284_638560247bd4652e28be6.png!small)

##  **五、免杀测试**

按照逆向分析结果和免杀原理，我们同样使用CS木马的Shellcode进行免杀测试。首先解压LiveUpdate.dat得到_TUProj.dat文件，然后修改其中的Lua代码，将混淆后的shellcode转换为数字存放在数组中，创建新线程运行。接着再将修改后的_TUProj.dat文件替换LiveUpdate.dat中的_TUProj.dat文件。最后再运行LiveUpdate.exe，实现加载LiveUpdate.dat，运行其中包含的Shellcode，如下图所示：

![](https://image.3001.net/images/20221129/1669685313_63856041c6b96e025ec11.png!small)

测试国内主流杀毒软件，静态全部免杀，运行后上线成功，执行注入等高危操作也全部免杀，免杀效果较好，如下图所示：

![](https://image.3001.net/images/20221129/1669685348_63856064c063e56ee4723.png!small)![](https://image.3001.net/images/20221129/1669685357_6385606d19fbc1bb99591.png!small)![](https://image.3001.net/images/20221129/1669685366_63856076a990218a8d59d.png!small)![](https://image.3001.net/images/20221129/1669685375_6385607f9b92235515967.png!small)

##  **六、总结**

基于LOLBins的攻击方法近年来在APT攻击中愈发常见，结合其他免杀技术，免杀效果极好，很难被检测和查杀。杀毒软件也应更新查杀手段，多角度对基于LOLBins的攻击行为进行定向、深入查杀。

##  **七、参考链接**

1) <https://www.anquanke.com/post/id/87299/>

2) <https://github.com/LOLBAS-Project/LOLBAS>

3) <https://www.cynet.com/attack-techniques-hands-on/what-are-lolbins-and-how-do-attackers-use-them-in-fileless-attacks/>

[原文链接﻿](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247485510&idx=1&sn=e2261501a4baaa98b780bc7897d2d906&chksm=c2a1dccff5d655d93d065350149453c708ca3920161026658da776b17db3d4795423486a838d&token=1833182322&lang=zh_CN#rd)

