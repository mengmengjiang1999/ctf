*****本文原创作者：F_F，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  
**

##  **一、前言**

 **说起来也比较久了，故事起源于去年11月份，我在公司办公环境搭建了一个dvwa的靶场环境，用于web漏洞的测试，不经意的发现access
log日志增长迅速，查看之后吓出一身冷汗。**

日志部分截图如下：

![1.png](https://image.3001.net/images/20190415/1555293894_5cb3e6c6cc9b4.png!small)一看就知道这是struts的攻击payload，但是我搭建的是php站点啊，拿java的payload来打我，有意义么！气愤之余，顺着payload里面的下载地址，找到了一个压缩包，分析后才发现是黑客进行攻击的主程序源代码。

该病毒与腾讯之前在FreeBuf上分析的Satan特征一致，腾讯捕获并分析的是可执行程序，我溯源获取到的是源代码。参考链接：<https://www.freebuf.com/column/197205.html>。看了腾讯的分析后，也对这次黑客攻击有了快速、清晰的认识。

##  **二、正文**

本文主要从源代码来看看一款精致的病毒软件，它应该具备什么样的功能，模块化设计该如何规划。

源代码解压：

![2.png](https://image.3001.net/images/20190415/1555295171_5cb3ebc39d393.png!small)

程序用c++编写，总共14个文件，简要介绍如下：

 **main.cpp：**
程序的主要执行入口，创建多线程执行扫描，同时调用struts2攻击模块、tomcat攻击模块、weblogic攻击模块，jboss攻击模块，ssh攻击模块。攻击成功后，调用public.cpp的上传模块，将攻击成功的目标站点地址通过自定义base64编码上传到黑客站点。

 **struts2.cpp：**
包括045、046、057的攻击payload，满足条件时，调用public的上传模块，将攻击成功的目标站点通过自定义base64编码上传到黑客站点。

 **tomcat.cpp：** 设置16进制编码的java
webshell，在破解tomcat管理后台用户名/密码后，尝试上传并执行webshell，webshell主要用户识别操作系统类型，智能下载fast.exe/ft32/ft64挖款程序。

 **weblogic.cpp：** 包括CVE-2017-10271(WLS
组件的反序列化漏洞)，CVE-2018-2894（任意文件上传）的攻击payload。

 **jboss.cpp：** 包括CVE-2013-4810（反序列化漏洞），CVE-2017-12149（反序列化命令执行漏洞），后台文件上传漏洞

 **ssh2.cpp：** 通过配置的ssh用户名/密码组合，尝试登陆目标主机，登陆成功则执行下载挖矿程序。

核心代码截图：主程序main.cpp

###
![3.png](https://image.3001.net/images/20190415/1555299471_5cb3fc8fc9e8f.png!small)2.1
程序不传入参数，执行GetLocalIP：

获取本地所有网卡，在非回环地址调用TaskAll。

![1.png](https://image.3001.net/images/20190415/1555300135_5cb3ff27c2e54.png!small)TaskAll调用多线程进行端口扫描：

![2.png](https://image.3001.net/images/20190415/1555300302_5cb3ffce7b94d.png!small)

pScan逻辑判断：

![Clipboard
Image.png](https://image.3001.net/images/20190415/1555318097_5cb445512f05c.png!small)

如果端口为22，则进行ssh爆破，爆破成功后，基于主机信息进行远程挖矿程序下载：

![Clipboard
Image.png](https://image.3001.net/images/20190415/1555315882_5cb43caa71312.png!small)

如果端口不是22，则调用HttpCheck函数，根据端口设置http协议类型，然后再调用AllScan进行攻击。

![Clipboard
Image.png](https://image.3001.net/images/20190415/1555316123_5cb43d9b6d6ea.png!small)以上诸如struts2.cpp、tomcat.cpp、weblogic.cpp、jboss.cpp中的攻击代码，均在AllScan中调用：

![Clipboard
Image.png](https://image.3001.net/images/20190415/1555316610_5cb43f8254faf.png!small)![Clipboard
Image.png](https://image.3001.net/images/20190415/1555316826_5cb4405aafc7c.png!small)![Clipboard
Image.png](https://image.3001.net/images/20190415/1555316904_5cb440a8a2915.png!small)![Clipboard
Image.png](https://image.3001.net/images/20190415/1555317100_5cb4416c3be30.png!small)Tomcat攻击模块，程序中内置用户名/密码清单，进行破解。

![Clipboard
Image.png](https://image.3001.net/images/20190415/1555317172_5cb441b4dffb1.png!small)
**综合：**
在程序未传参时，程序自动获取本地所有网卡的ip地址，开启多线程在B段上进行端口扫描，如发现主机22开放，则尝试破解，其他协议则尝试web访问，设置HTTP/HTTPS协议，然后将所有payload依次打过去，控制主机下载挖矿程序，如成功利用，则将站点信息base64编码回传到黑客站点。

### 2.2 传入ips，从本地ips文件中依次读取ip清单，在ip地址的C段上调用pScan进行扫描。

部分逻辑代码如下：

### ![Clipboard
Image.png](https://image.3001.net/images/20190415/1555318298_5cb4461a9c420.png!small)![Clipboard
Image.png](https://image.3001.net/images/20190415/1555318374_5cb4466636bb0.png!small)2.3
其他模式说明

若命令为att，则命令行后是具体的站点地址，此时调用AllScan，用所有web payload进行攻击；

若命令为file，则命令行后是文件汇总的站点清单，判断http/https协议后，调用AllScan进行攻击；

若命令为ssh，则命令后是文件汇总的ip清单，则根据内置的ssh用户名/密码进行破解，成功后控制主机下载挖矿程序。

##  **三、其余核心代码截图**

struts2.cpp：Struts2-045，区分windows/linux32/linux64位，设置不同的挖矿程序地址：

![Clipboard
Image.png](https://image.3001.net/images/20190415/1555319023_5cb448ef5fef5.png!small)Struts2-046
payload：

![Clipboard
Image.png](https://image.3001.net/images/20190415/1555319060_5cb4491434715.png!small)Struts2-057
payload：

![Clipboard
Image.png](https://image.3001.net/images/20190415/1555319085_5cb4492d63407.png!small)

jboss.cpp：

![Clipboard
Image.png](https://image.3001.net/images/20190415/1555319154_5cb44972f4074.png!small)

##  **四、分析回顾与反思**

111.90.158.225是黑客回传数据的站点，当前已无法打开，之前看到很多txt文件，还不知道是什么意思，应该有很多终端已经沦陷。程序的模块化设计对于企业安全人员红蓝对抗、批量验证站点组件漏洞都具有一定的参考意义。

反思：做好安全感知和攻击溯源对于企业而言确实很重要，比如部署一些蜜罐，可以在攻击早起就能察觉，另外终端的批量文件和进程检索，很基础也很重要！

 ***本文原创作者：F_F，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

