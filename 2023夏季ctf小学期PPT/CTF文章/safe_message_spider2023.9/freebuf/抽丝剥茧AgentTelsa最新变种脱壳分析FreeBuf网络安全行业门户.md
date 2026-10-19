*** 本文作者：Voraka，本文属FreeBuf原创奖励计划，转载请注明来自FreeBuf.COM** ****

 **近日，我们检测到大量经过相同加壳混淆过的.NET 恶意木马文件，经过进一步深入分析发现，该木马是带隐私窃取功能的后门木马 Agent
Tesla。从2014年起至今，Agent Tesla已经由一个键盘记录器变身成为一款专业的商业间谍软件。本文主要介绍如何将Agent Tesla
间谍软件抽丝剥茧出来。**

## 样本分析

### 0x1 Stage1

这是一个.NET应用程序，我们从这个入口点来开始分析：

    
    
    static void XPathSingletonIterator(string[] args){    EventKeywords.WebBrowserDocumentCompletedEventArgs().EntryPoint.Invoke(null, null);}
    

可以看出函数WebBrowserDocumentCompletedEventArgs是一个Assembly方法，如图:

![1.PNG](https://image.3001.net/images/20180621/15295614678587.png!small)通过base64解码出一段代码，然后将动态编译成dll并通过反射的方式执行这段代码。解码的代码如图：

![2.PNG](https://image.3001.net/images/20180621/15295615414266.png!small)stage1.cs，主函数代码如图：![3.PNG](https://image.3001.net/images/20180621/15295616849679.png!small)FindResource函数的参数在MSDN的定义，如下：

    
    
    HRSRC FindResource(          HMODULE hModule,
        LPCTSTR lpName,    //124
        LPCTSTR lpType     //23， RT_HTML
    );
    

通过PE Explorer查看该样本的资源段，发现了被加密的payload即资源为124的PNG图片，如图：

![4.PNG](https://image.3001.net/images/20180621/1529561859208.png!small)在stage1.cs的代码中，找到了解密上面payload的代码，如图：

![5.PNG](https://image.3001.net/images/20180621/15295619523519.png!small)可以看出payload的解密方式为异或，密钥为Unicode字符串"QzEwIYNhXAJL"的字节码。由于是在内存中通过反射方式执行上面解密的payload，若要dump解密后的payload，需手动写代码进行解密。将stage1.cs稍作修改，部分代码如下：

![6.PNG](https://image.3001.net/images/20180621/15295628236003.png!small)将上面的代码编译并运行，解密生成stub.exe文件。

### 0x2 Stage2

将上面的stub.exe载入dnSpy继续分析，如下图：

![10.PNG](https://image.3001.net/images/20180621/15295708334858.png!small)首先发现该样本有三个资源，第一个资源是包含许多看似base64编码的字符串的文本，第二个和第三个是二进制文件。

资源一 (6ie58GzmUqGP5Y3w)

![12.PNG](https://image.3001.net/images/20180621/15295712312107.png!small)由上图可以看出，资源一中的字符串是用base64编码的，将资源一的内容复制出来，编写代码如下：

![13.PNG](https://image.3001.net/images/20180621/15295715207277.png!small)解码后的字符串，如图：

![14.PNG](https://image.3001.net/images/20180621/15295716061119.png!small)资源二
(YwdTXmElBrvD)

读取资源二的字节码并解密，如图：

![18.PNG](https://image.3001.net/images/20180622/15296324717132.png!small)

通过base64解码密钥key: Unicode字符串"oJUEUAnYNDgG"的字节码。如图：

![16.PNG](https://image.3001.net/images/20180621/15295744469961.png!small)将资源二与上面的key进行异或，得到payload2.exe，如图：

![15.PNG](https://image.3001.net/images/20180621/1529574219667.png!small)将资源二解密得到的payload保存为"payload2.exe"，进一步分析后发现是一个蠕虫病毒[Mofksys，](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?Name=Worm:Win32/Mofksys.A)主要通过网络共享，可移动驱动器和电子邮件传播。
并通过SMTP将收集到的敏感数据发送给攻击者。

资源三 (OhDKMgmICCQA)

将解密的恶意payload注入进程"C:\Windows\Microsoft.NET\Framework\v4.0.30319\vbc.exe"，如图：![17.PNG](https://image.3001.net/images/20180622/15296327911258.png!small)将资源三的字节码与Unicode字符串"oJUEUAnYNDgG"的字节码进行异或解密，如图：

![19.PNG](https://image.3001.net/images/20180622/15296474104628.png!small)将资源三解密得到的payload保存为"payload3.exe"，通过进一步分析发现是[Agent
Telsa](https://www.agenttesla.com/)的一个变种。Agent Tesla是一款强大的信息窃取木马。
它提供了通过键盘和屏幕截图监控他人的计算机。 键盘，屏幕截图和注册密码均以日志形式发送。 可以通过电子邮件，ftp或php（网页面板）接收日志。如下图：

### ![Agent-Tesla-keylogger.png](https://image.3001.net/images/20180622/15296489374658.png!small)0x3
Stage3

将上面的"payload3.exe"载入dnspy继续分析。恶意代码中敏感的字符串都被加密了，如图：

![20.PNG](https://image.3001.net/images/20180622/15296505744074.png!small)查看解密代码，如图：

![21.PNG](https://image.3001.net/images/20180622/15296506284167.png!small)发现加密算法为base64+AES，编写解密代码，将所有加密字符串解密，如图：

设置键盘钩子，获取键盘记录，如图：

![23.PNG](https://image.3001.net/images/20180622/15296535849765.png!small)![24.PNG](https://image.3001.net/images/20180622/15296535846759.png!small)

反模拟器，反调试，如图：

![25.PNG](https://image.3001.net/images/20180622/15296537079367.png!small)睡眠15秒后继续执行，通过延时机制躲避某些杀毒软件模拟器的检测，如图：![26.PNG](https://image.3001.net/images/20180622/1529653707555.png!small)检测模拟器的计算机名，如果是图中的名字则退出。如图：

![28.PNG](https://image.3001.net/images/20180622/15296544653817.png!small)获取屏幕截图，如图：

![29.PNG](https://image.3001.net/images/20180622/15296551239067.png!small)获取粘贴板内容，如图：

![31.PNG](https://image.3001.net/images/20180622/15296557129495.png!small)限于篇幅限制，不再一一列出，下面是该木马的主要功能，如图：

![27.PNG](https://image.3001.net/images/20180622/15296565456124.png!small)该木马使用的C&C配置信息，如下：

    
    
    private static string BO_46 = "smtp";         //通过邮件发送窃取的信息，而不是通过FTP，php等。
    

木马作者的使用的邮箱，如图：

![32.PNG](https://image.3001.net/images/20180622/15296575089235.png!small)出于”安全研究“的目的，我登陆了木马作者的邮箱，主要为了研究以下几点：

> 1\. 木马攻击的开始时间2. 木马感染者的数量
>
> 3\. 木马感染者的地域分布
>
> 4\. 木马感染/传播方式5. 木马作者溯源

截至今天，已经累计收到
6000+的邮件，如图：![33.PNG](https://image.3001.net/images/20180622/15296580614195.png!small)获取被感染用户密码信息，如图：

![34.PNG](https://image.3001.net/images/20180622/15296586155975.png!small)经过邮件统计，该木马感染的机器数量约为150台。从被感染的IP地址分析得出，大部分的受害者来源于土耳其。

除了一个邮箱地址，攻击者没有留下任何有价值可以溯源的线索，直到在海量邮件中发现了下面这封，如图：

![35.PNG](https://image.3001.net/images/20180625/15298943636058.png!small)可以看出这是攻击者早期在进行木马测试。测试时间为
2018.3.1，攻击者的机器名：KEMMETAL/DESKTOP-VEMHD4V

尝试在Google上搜索，看能否发现有价值的信息，最终在一个安全研究员的Twitter中发现了下面的信息，如图：

![36.PNG](https://image.3001.net/images/20180625/15298948627378.png!small)通过样本同源分析，最终发现该类型木马是通过钓鱼垃圾邮件进行传播。

##  **总结**

随着MaaS（Malware-as-a-Service）的日益增多，恶意程序攻击服务给攻击者提供越来越多的方便，也降低了攻击者的技术门槛，越来越多的人很容易加入到了网络犯罪当中。同时由于攻击套件的强大反调试，反杀毒软件的强大能力，使得各种这类木马横行，给杀毒软件带来更大的查杀难度和更大的挑战，也给整个网络安全环境带来更大的威胁。

 *** 本文作者：Voraka，本文属FreeBuf原创奖励计划，转载请注明来自FreeBuf.COM**

