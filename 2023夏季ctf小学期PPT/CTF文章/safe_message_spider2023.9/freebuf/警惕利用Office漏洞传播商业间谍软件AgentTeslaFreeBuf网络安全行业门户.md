# **背景概述**  

**AgentTesla原本是一款在2014年发布的简单的键盘记录器，近年来其开发团队为其不断增加了许多新功能，并进行出售。AgentTesla现已成为一个商业化的间谍软件，可通过控制端生成满足功能需求的木马程序。**

AgentTesla最常见的传播方式是钓鱼邮件，邮件附件中通常会携带恶意文档，通过宏或漏洞利用下载运行恶意程序。近日，深信服安全团队采集到利用CVE-2017-11882传播AgentTesla窃取信息的恶意样本，并对其攻击过程进行了详细分析。

##  **详细分析**

###  **CVE-2017-11882**

1.使用工具监控文件行为，查看到运行文档后系统拉起了eqnedt32.exe进程，并且通过抓包捕获到下载EXE文件的流量，由此判断是利用CVE-2017-11882执行恶意代码：

![01.png](https://image.3001.net/images/20190527/1558922464_5ceb44e0bb9fb.png!small)

2.通过附加调试器，在Kernel32!WinExec下断点，查看寄存器值，找到运行了"C:\Users\root\AppData\Roaming\Adobe.exe"的命令，与捕获到的流量信息相结合判断，恶意代码应是下载文件保存到本地然后运行，推断使用了URLDownloadToFile相关API：

![02.png](https://image.3001.net/images/20190527/1558922468_5ceb44e42b2d3.png!small)

3.附加调试器对网络相关API下断调试，但程序并没有断下，于是在eqnedt32.exe造成溢出的函数处下断，单步调试到ret覆盖的返回地址，执行恶意代码：

![03.png](https://image.3001.net/images/20190527/1558922470_5ceb44e69484c.png!small)

4.恶意代码先对内存进行解密操作，图中是解密前后对比，可以直观的看到所使用的字符串信息，通过动态获取API地址，调用URLDownloadToFileW下载文件，再通过WinExec运行：

![04.png](https://image.3001.net/images/20190527/1558922473_5ceb44e9595a1.png!small)

**![05.png](https://image.3001.net/images/20190527/1558922506_5ceb450ab582e.png!small)**

###  **AgentTesla**

1.AgentTesla是用.Net框架编写的键盘记录器，使用反编译工具查看代码，自定义函数名都进行了混淆，但使用的API和关键字符串仍然是明文的，可以看到进行键击记录的代码：

![06.png](https://image.3001.net/images/20190527/1558922517_5ceb4515d5101.png!small)

2.除了键盘记录以外，还会通过读取注册表键值来获取主机信息：

![07.png](https://image.3001.net/images/20190527/1558922545_5ceb4531a27fd.png!small)

3.使用DES算法加密所要发送的数据：

![08.png](https://image.3001.net/images/20190527/1558922549_5ceb4535eafcc.png!small)

4.有三种可选的方式将窃取到的数据上传至远程C&C端：

通过FTP上传：

![](https://image.3001.net/images/20190527/1558922559_5ceb453f893d0.png!small)

通过SMTP上传：

![10.png](https://image.3001.net/images/20190527/1558922562_5ceb4542c5bbd.png!small)

通过HTTP上传：

![11.png](https://image.3001.net/images/20190527/1558922565_5ceb45458514f.png!small)

5.AgentTesla的资源中内嵌了一个DLL文件，名为IELibrary.dll，是一个用于实现浏览器操作的DLL文件，在AgentTesla中定义了需要窃取信息的浏览器及网络套件名称，这是在使用控制端生成恶意程序时的可选项：

![12.png](https://image.3001.net/images/20190527/1558922569_5ceb454958360.png!small)

6\. IELibrary.dll主要针对浏览器进行信息收集和操作，包括历史记录的增删查：

![13.png](https://image.3001.net/images/20190527/1558922571_5ceb454bf1db9.png!small)

窃取密码及cookie：

![14.png](https://image.3001.net/images/20190527/1558922574_5ceb454eb3ddf.png!small)

##  **解决方案**

###  **病毒检测查杀**

1、深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

64位系统下载链接：

<http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>

32位系统下载链接：

<http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

###  **病毒防御**

1、不从不明网站下载软件，不要点击来源不明的邮件附件，不随意启用宏；

2、下载补丁修补CVE-2017-11882：

<https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-11882>

3、开启Windows Update功能，定期对系统进行自动更新

最后，建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。推荐使用深信服安全感知+防火墙+EDR，对内网进行感知、查杀和防护。

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM。**

