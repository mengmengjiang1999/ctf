**近日，亚信安全截获新型的EMOTET银行木马新变种，其主要通过垃圾邮件的方式进行传播，是一款比较著名且复杂的银行木马。EMOTET银行木马最早可以追溯到2014年，其主要使用网络嗅探技术窃取数据。在之后的几年里，EMOTET表现得并不活跃且慢慢开始淡出人们的视线。然而，2017年8月份EMOTET又“卷土重来”，亚信安全截获了多个变种，这些变种主要攻击美国、英国和加拿大等国家，此后，EMOTET一直处于活跃阶段。**

本次截获的Emotet银行木马同样是通过带有附件的垃圾邮件进行传播，诱导用户点击带有宏病毒的附件文档，一旦宏启动，恶意的宏代码将会运行，通过PowerShell命令下载恶意程序，窃取用户敏感信息。亚信安全将其命名为Trojan.W97M.POWLOAD.TIOIBEFV。

##  **详细分析**

Emotet银行木马主要通过垃圾邮件进行传播，下图是我们截获的垃圾邮件样本，主题为“付款汇款通知”。

![](https://image.3001.net/images/20190920/1568964786_5d8480b2db9ce.png!small)

打开文档后，会提示开启宏，一旦运行后，将会执行恶意的宏代码。

![](https://image.3001.net/images/20190920/1568964798_5d8480be63692.png!small)

通过olevbs工具查看，该样本含有宏代码模块，并且都是混淆的代码，可以通过动态调试，获取其最终运行的PowerShell命令行。

![](https://image.3001.net/images/20190920/1568964869_5d84810518592.png!small)

![](https://image.3001.net/images/20190920/1568964878_5d84810e6fbce.png!small)

由于命令行是通过base64加密的，我们可以将其解密，解密后的代码如下所示，其主要功能是从C&C服务器上下载恶意的可执行程序523.exe到系统用户目录，并执行该程序。

![](https://image.3001.net/images/20190920/1568964902_5d84812634295.png!small)![](https://image.3001.net/images/20190920/1568964911_5d84812fa92a9.png!small)

##  **523.exe** **文件分析**

该程序的核心代码是通过高度加密的，其将资源区的内容和静态变量中的加密字符串进行整合，然后动态分配内存，进行解密。

首先通过修改注册表关闭进程的DEP策略（数据执行保护策略），通过资源操作API获取资源节区内容。

![](https://image.3001.net/images/20190920/1568964929_5d848141a9e88.png!small)![](https://image.3001.net/images/20190920/1568964936_5d848148bb7ca.png!small)

多次分配内存，解密这些加密的字符串。

![](https://image.3001.net/images/20190920/1568964954_5d84815a149ac.png!small)![](https://image.3001.net/images/20190920/1568964964_5d848164b5b3a.png!small)

整合PE数据。

![](https://image.3001.net/images/20190920/1568964981_5d848175bf06a.png!small)

![](https://image.3001.net/images/20190920/1568964990_5d84817e29ed9.png!small)![](https://image.3001.net/images/20190920/1568964995_5d84818389f57.png!small)

获取操作系统的位数，名称和版本信息。

![](https://image.3001.net/images/20190920/1568965012_5d8481949ee21.png!small)

动态获取要使用的API函数地址。

![](https://image.3001.net/images/20190920/1568965022_5d84819ede9e3.png!small)

通过GetModuleFileNameW函数获取当前进程路径。

![](https://image.3001.net/images/20190920/1568965037_5d8481add5a74.png!small)

然后再次创建一个挂起的子进程。  

![](https://image.3001.net/images/20190920/1568965057_5d8481c192e5f.png!small)![](https://image.3001.net/images/20190920/1568965071_5d8481cf7bab8.png!small)

然后通过修改其子进程的主线程上下文内容，将其重新指向该程序入口地址0x00400000。

![](https://image.3001.net/images/20190920/1568965089_5d8481e172c4d.png!small)

![](https://image.3001.net/images/20190920/1568965134_5d84820ed0196.png!small)![](https://image.3001.net/images/20190920/1568965106_5d8481f277960.png!small)

修改线程上下文内容后，然后恢复，运行子进程。

![](https://image.3001.net/images/20190920/1568965172_5d8482345ca76.png!small)

通过调用ExitPorcess函数，结束其父进程。

![](https://image.3001.net/images/20190920/1568965183_5d84823f2a894.png!small)

其子进程的主要功能是与C&C服务器进行通信，窃取系统敏感信息和远程控制用户电脑等恶意行为。它会不断尝试可以进行连接的网址，有些网址目前已经无法连接。

![](https://image.3001.net/images/20190920/1568965219_5d8482634247e.png!small)![](https://image.3001.net/images/20190920/1568965196_5d84824c72a40.png!small)

![](https://image.3001.net/images/20190920/1568965243_5d84827b7edba.png!small)

最后会通过修改注册表，添加启动项。

![](https://image.3001.net/images/20190920/1568965254_5d8482861da82.png!small)

##  **总结：**

亚信安全通过持续的追踪调查发现，从9月16日首次发现本次变种后，截止今日该病毒仍然在不断的更新，比较显著的变化是C&C服务器地址以及落地到系统中的可执行文件名称，从523.exe到572.exe、208.exe和
972.exe等，同样地，下载这些文件的URL地址也发生了改变。

![](https://image.3001.net/images/20190920/1568965269_5d848295b0b93.png!small)![](https://image.3001.net/images/20190920/1568965274_5d84829aa009a.png!small)![](https://image.3001.net/images/20190920/1568965279_5d84829fc6ee3.png!small)

最新的Emotet相关C2信息。

![](https://image.3001.net/images/20190920/1568965293_5d8482ad4d47b.png!small)![](https://image.3001.net/images/20190920/1568965300_5d8482b4d8022.png!small)

![](https://image.3001.net/images/20190920/1568965308_5d8482bc7732c.png!small)

从9月中旬开始，利用垃圾邮件传播EMOTET银行木马的活动持续增加，如下是其垃圾邮件样例。目前垃圾邮件的使用的语言以德语，波兰语和意大利语居多，不排除将来会有中文版本的钓鱼邮件。

![](https://image.3001.net/images/20190920/1568965320_5d8482c879623.png!small)

##  **解决方案**

> 不要点击来源不明的邮件以及附件；
>
> 不要点击来源不明的邮件中包含的链接；
>
> 打全系统及应用程序补丁；
>
> 采用高强度的密码，避免使用弱口令密码，并定期更换密码；
>
> 尽量关闭不必要的文件共享；

**IOC**

> SHA-1
>
> 6b6f838eab12486f80fae8c83e116620ef188053

 ***本文作者：亚信安全，转载请注明来自FreeBuf.COM**

