## 概述

**近日发现新版本的WatchBog：自2018年底开始运行的加密货币挖掘僵尸网络。自6月初开始已有超过4,500台Linux机器遭到破坏。在新的Linux漏洞利用中，该版本WatchBog实现了BlueKeep
RDP协议漏洞扫描模块，这表明WatchBog正在记录所有有漏洞的系统ip，以便将来进行攻击或出售给第三方获取利润。**

 **目前，所有安全厂商都未检测到恶意软件。**

## 简介

Watchbog是一个加密货币挖掘僵尸网络，早在2018年11月就被发现。已知攻击组织正在利用已知的漏洞来攻击Linux服务器。阿里云安全部门过去曾对该组织进行过备案。

自上一次发表关于该组织分析报告以来，它已经通过一个新的扩展模块来增加其植入方式，以提高攻击服务器的覆盖率。我们检测到一个新版本watchbog，其中包含了最近发布的漏洞：JIRA的CVE-2019-11581（在漏洞发布后12天内增加）、exim的CVE-2019-10149和solr的CVE-2019-0192。

我们还发现新模块包含BlueKeep扫描器。CVE–2019-0708，是一个基于Windows的内核漏洞。该漏洞存在于Windows
2000到Windows Serv er 2008和Windows
7的未修补Windows版本中。现还没有PoC可用于实现此漏洞的RCE，在野外也还没有发现任何攻击行为。该扫描器模块的合并表明，Watchbog正在为以后针对含有Bluekeep漏洞的系统攻击做准备。

此外，Jira、Solr和Bluekeep扫描仪模块均在13天内添加，Watchbog正在加速新功能的整合。

安全厂商目前未检测到新模块的二进制文件：

![1.PNG](https://image.3001.net/images/20190731/1564540315_5d40fd9b51fc8.png!small)

将此文件上载到intezer分析后，我们可以看到它与watchbog共享代码：

![2.PNG](https://image.3001.net/images/20190731/1564540325_5d40fda50be5c.png!small)

这一新的传播模块存在一个缺陷，它允许我们发起“中间人”攻击，以帮助我们分析二进制文件。

## 技术分析

watchbog在感染目标时运行初始部署脚本。该脚本通过crontab持久控制，并从Pastebin下载更多的Monero Miner模块。

该脚本末尾的部分如下：

![3.PNG](https://image.3001.net/images/20190731/1564540563_5d40fe93a4d79.png!small)

根据watchbog脚本传统操作方式，脚本会从pastebin下载另一个base64编码的有效payload，然后执行：

![4.PNG](https://image.3001.net/images/20190731/1564540571_5d40fe9b4038b.png!small)

然而，下载的不是另一个挖矿模块，它是新的传播模块。从快速视图中可以看到这是一个动态链接ELF可执行文件。分析后发现这实际上是一个Cython-compiled的可执行文件，需要进一步进行分析。

![5.PNG](https://image.3001.net/images/20190731/1564540580_5d40fea46ffaf.png!small)

如关于Cython的文章所述：

“Cython是一个优化的静态编译器，它将您的.py模块转换为高性能的C文件。生成的C文件可以毫不费力地编译到二进制库中。编译完成后就无法将已编译的库反向转换为可读的Python源代码“。不过，编译后的二进制文件包含了一些对原始python模块的信息：

![6.PNG](https://image.3001.net/images/20190731/1564540590_5d40feae5603a.png!small)

## 初始化

二进制文件会在/tmp/.gooobb处创建文件，在该文件中，它将其pid作为恶意软件执行的日志写入。当此文件存在时，后续启动传播模块都会失败。

然后二进制文件从Pastebin中检索其C2服务器：

![7.PNG](https://image.3001.net/images/20190731/1564541173_5d4100f592190.png!small)

.onion C2服务器地址以硬编码存储在二进制文件中，并用作后备。

我们可以根据对Pastebin链接的访问次数来估计受感染的受害者数量：

![8.PNG](https://image.3001.net/images/20190731/1564541182_5d4100fec06cb.png!small)

如上所示，大约有4,500个端点访问了Pastebin链接。
由于已知WatchBog在6月5日之前一直处于活动状态，其中一些机器可能点击了较旧的Pastebin链接受到感染。

二进制文件首先尝试连接到其中一个可用的静态C2服务器。我们观察到C2服务器的证书已过期。通常，HTTPS客户端会检查他们正在与之交互的SSL证书的验证。
然而，WatchBog的植入方式并非如此。 这导致WatchBog客户端在使用HTTPS时没有验证证书，否则它将拒绝与C2通信。

这个漏洞允许我们使用自己的证书设置HTTPS代理，并进行“中间人”攻击以分析WatchBog SSL / TLS流量：

![9.PNG](https://image.3001.net/images/20190731/1564541190_5d410106c078d.png!small)

然后，二进制文件为受感染的受害者生成唯一密钥，并在此密钥下向C2发送初始消息。 以下图片包含来自SSL /
TLS解密流量的样本请求和响应有效payload：

![25.PNG](https://image.3001.net/images/20190731/1564541910_5d4103d69454d.png!small)

对这些数据包通过编码混淆其内容。 在分析过程中，我们已经确定使用的编码算法。 以下脚本可以解码payload：

    
    
    final = ""
    arr = input()
    
    for a in arr:
          stri = "begin 666 \n{0}\n \nend\n".format(a) \
                .decode("uu").strip('\x00') \
                .decode("hex") \
                .decode("base64")
        final += chr(int(stri))
    print(final[::-1])
    

初始消息包含受攻击系统信息：

![11.PNG](https://image.3001.net/images/20190731/1564541198_5d41010e53bc1.png!small)

这些信息将被合并和取hash值，以构建其CNC中WatchBog API的路径。 服务器回复一个“任务”，让机器自动在目标列表上执行：

![12.PNG](https://image.3001.net/images/20190731/1564541210_5d41011a427c7.png!small)

## BlueKeep扫描  

在较新版本的WatchBog中，已经集成了一个RDP扫描程序，以便找到易受攻击的Windows机器。
此扫描程序是来自github上zithosum0x0的python扫描程序。 我们可以根据函数名称的相似性进行评估：

![21.PNG](https://image.3001.net/images/20190731/1564541389_5d4101cd1d2d3.png!small)

扫描器将尝试从CNC提供的IP列表中查找易受攻击的RDP服务器：

![22.PNG](https://image.3001.net/images/20190731/1564541397_5d4101d5aa1ea.png!small)

RDP的默认Windows服务端口是TCP 3389，可以利用“Cookie：mstshash =”字段识别。

![23.PNG](https://image.3001.net/images/20190731/1564541407_5d4101df0505a.png!small)

![24.PNG](https://image.3001.net/images/20190731/1564541418_5d4101eaf243c.png!small)

我们可以观察到使用字符串'watchbog'作为RDP mstshash字段的用户名。

我们发现RDP扫描的IP列表中，一些IP地址属于 Vodafone Australia和Tencent Computer Systems。

在扫描结束之后，WatchBog客户端返回一个RC4加密的结果IP地址列表，编码为十六进制字符串：

![25.PNG](https://image.3001.net/images/20190731/1564541425_5d4101f146b4b.png!small)

可以看出WatchBog正在收集易受攻击的BlueKeep Windows列表以供将来使用，或者出售给第三方获取利润。

## 传播方式

WatchBog利用如下几个漏洞进行传播：

CVE-2019-11581 (Jira)

CVE-2019-10149 (Exim)

CVE-2019-0192 (Solr)

CVE-2018-1000861 (Jenkins)

CVE-2019-7238 (Nexus Repository Manager 3)

![31.PNG](https://image.3001.net/images/20190731/1564541703_5d410307b8216.png!small)

此外还有CouchDB和Redis实例模块与代码一起实现RCE。所有被利用的“pwn”模块都允许攻击者实现远程代码执行。一旦发现易受攻击的服务存在漏洞利用模块，二进制文件就会调用对应漏洞并安装Pastebin上托管的恶意bash脚本来进行传播。

我们能够找到上传到HybridAnalysis的spreader模块的早期测试版本，包括对Solr CVE-2019-0192的攻击，对ActiveMQ
CVE-2016-3088的攻击，以及Redis实例：

![32.PNG](https://image.3001.net/images/20190731/1564541712_5d410310144a2.png!small)

## 总结

WatchBog通过整合最近发布的漏洞并使用新攻击技术更新其植入方式。如果使用Cython等引擎本地部署Python恶意软件，它就会变得更难分析。这与其他Python本机框架（如pyinstaller）形成对比，Cython无法恢复Python代码。

Linux僵尸网络整合BlueKeep扫描器表明WatchBog开始在不同的平台上探索获利机会。目前，没有已知的RCE BlueKeep PoC。

## 防范措施

1、将相关软件更新到最新版本：

2、Windows用户参考Microsoft的客户指南，安装BlueKeep漏洞补丁。

3、使用Exim，Jira，Solr，Jenkins或Nexus Repository Manager 3的Linux用户更新到最新版本。

4、使用Redis或CouchDB的Linux用户确保没有在受信任网络之外开放端口。

5、怀疑自己感染了WatchBog的Linux用户检查是否存在“/tmp/.tmplassstgggzzzqpppppp12233333”文件或“/tmp/.gooobb”文件。

## 线上代码分析

WatchBog已经在Intezer的基因数据库中编入索引。 如果怀疑是WatchBog的可疑文件，可以将其上传到Intezer
Analyze，以检测此恶意软件的代码重用情况。

![33.PNG](https://image.3001.net/images/20190731/1564541721_5d4103195bc30.png!small)

## IOCs

> b17829d758e8689143456240ebd79b420f963722707246f5dc9b085a411f7b5e
>
> 26ebeac4492616baf977903bb8deb7803bd5a22d8a005f02398c188b0375dfa4
>
> cdf11a1fa7e551fe6be1f170ba9dedee80401396adf7e39ccde5df635c1117a9
>
> <https://9d842cb6.ngrok>[.]io
>
> <https://7dc5fb4e.ngrok>[.]io
>
> <https://z5r6anrjbcasuikp.onion>[.]to
>
> <https://pastebin>[.]com/raw/Dj3JTtnj
>
> <https://pastebin>[.]com/raw/p3mGdbpq
>
> <https://pastebin>[.]com/raw/UeynzXEr
>
> <https://pastebin>[.]com/raw/MMCFQMH9
>
> 3.14.212[.]173
>
> 3.14.202[.]129
>
> 3.17.202[.]129
>
> 3.19.3[.]150
>
> 18.188.14[.]65

 ***本文作者：Kriston，转载请注明来自FreeBuf.COM**

