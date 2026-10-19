***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  **0x1 概述**  

**腾讯御见威胁情报中心监控发现，近期有大批企业网站的Web服务器遭到入侵并被植入挖矿木马。**

安全人员分析发现被攻击网站服务器多存在Apache Struts 2 Jakarta Multipart
Parser远程代码执行（RCE）漏洞(S2-045,CVE-2017-5638)，该漏洞在2017年3月被报出，影响范围为Struts 2.3.5 -Struts 2.3.31，以及Struts 2.5 – Struts 2.5.10版本。黑客组织利用该漏洞批量攻击网站并植入了木马。

##  **0x2 Shell代码分析**

黑客组织在攻击时向目标网站同时注入了Linux和Windows版本shell代码。如果目标网站是Windows服务器，则Windows版shell代码最终执行成功；如果目标网站是Linux服务器，则Linux版shell代码最终执行成功。

###  **1．Linux版本的shell代码**

在请求中通过iptables stop命令关闭防火墙，以及chmod 777命令提高权限。

![1.png](https://image.3001.net/images/20180427/15248152523542.png!small)

图1

然后通过wget、curl程序获取Linux挖矿程序，并通过命令crontab将其设定为持续执行。

![2.png](https://image.3001.net/images/20180427/15248152659347.png!small)

图2

###  **2\. Windows版本的shell代码**

首先创建用于下载挖矿木马的文件xxoo.vbe，并写入脚本代码。

![3.png](https://image.3001.net/images/20180427/15248152762181.png!small)

图3

在目标服务器生成脚本xxoo.vbe

![4.png](https://image.3001.net/images/20180427/15248152987014.png!small)

图4

然后利用cscript xxoo.vbe下载挖矿木马EXE

![5.png](https://image.3001.net/images/20180427/15248153093578.png!small)

图5

##  **0x3 木马分析**

###  **1\. Linux挖矿木马**

Linux木马脚本存放地址为hxxp://181.214.87.241/java/oracle.jpg，脚本会关闭已有挖矿进程，然后获取矿池配置文件，下载启动Linux挖矿程序。

![6.png](https://image.3001.net/images/20180427/15248153207150.png!small)

图6

从脚本使用的矿池配置文件hxxp://181.214.87.241/java/vlqd.cf

![7.png](https://image.3001.net/images/20180427/1524815333628.png!small)

图7

其中矿池地址为：78.46.91.134:80

挖矿帐号为：487ityZsfqR3vq5RUaHVCVY7G7nNEdvvkDgSy12aJgkG9fJooA1W8ZGLMMqJYiCm35iTFTm6vwfAt7rupBSKmb3YGdGiR4C

访问矿池IP可以看到门罗币矿池pool.minexmr.com

![8.png](https://image.3001.net/images/20180427/15248153461028.png!small)

图8

在该矿池的界面，查询到挖矿账户的信息：

![9.png](https://image.3001.net/images/20180427/15248153585812.png!small)

图9

下载的Linux挖矿程序(ELF文件)hxxp://181.214.87.241/java/vlqd

![10.png](https://image.3001.net/images/20180427/15248153718542.png!small)

图10

挖矿代码特征

![11.png](https://image.3001.net/images/20180427/1524815383841.png!small)

图11

###  **2\. Windows挖矿木马**

挖矿程序9875.exe运行后释放进程守护脚本AutoRunApp.VBS，每隔一段时间检测挖矿进程，如果进程不存在则重新启动；同时9875.exe释放并加载驱动xxxx.sys在驱动层保护挖矿行为。

![12.png](https://image.3001.net/images/20180427/15248153953241.png!small)

图12

木马判断系统版本

![13.png](https://image.3001.net/images/20180427/15248154095882.png!small)

图13

将自身添加到注册表启动项

![14.png](https://image.3001.net/images/20180427/15248154238681.png!small)

图14

创建挖矿进程守护脚本

![15.png](https://image.3001.net/images/20180427/15248154355833.png!small)

图15

![16.png](https://image.3001.net/images/20180427/15248154481662.png!small)

图16

释放随机名驱动到Temp目录，对挖矿进程、文件进行保护

![17.png](https://image.3001.net/images/20180427/15248154624380.png!small)

图17

获取机器信息

![18.png](https://image.3001.net/images/20180427/15248154847985.png!small)

图18

连接C2地址：61.147.120.245

![19.png](https://image.3001.net/images/20180427/15248154955913.png!small)

图19

门罗币挖矿代码

![20.jpg](https://image.3001.net/images/20180427/15248155095970.jpg!small)

图20

 **0x4 溯源分析**

查询木马连接C2的域名[www.sgzca.win](http://www.sgzca.win)，从注册邮箱可以看到作者曾经使用过的QQ：284****811

![21.png](https://image.3001.net/images/20180427/1524815523719.png!small)

图21

通过QQ可以查到域名注册者在某黑客论坛的记录

![22.jpg](https://image.3001.net/images/20180427/15248155378801.jpg!small)

图22

![23.png](https://image.3001.net/images/20180427/15248155512307.png!small)

图23

作者的论坛记录显示曾经发布过的矿马生成器、弱口令以及各类黑客工具

![24.png](https://image.3001.net/images/20180427/15248155648780.png!small)

图24

其他人下载工具时作者也能获得收入

![25.jpg](https://image.3001.net/images/20180427/15248155766519.jpg!small)

图25

作者发布的一款矿马生成器，支持任务管理器状态检测和K进程

![26.jpg](https://image.3001.net/images/20180427/15248155894330.jpg!small)

图26

![27.png](https://image.3001.net/images/20180427/15248156015479.png!small)

图27

作者累计发布11万多个IP的3306口令

![28.png](https://image.3001.net/images/20180427/15248156158185.png!small)

图28

##  **0x5 安全建议**

1．可查看web目录下/WEB-INF/lib/目录下的struts-core.x.x.jar 文件，如果这个版本在Struts2.3.5 到
Struts2.3.31 ，以及Struts2.5 到 Struts2.5.10之间则存在漏洞。受影响用户可升级版本至Apache Struts
2.3.32 或 Apache Struts 2.5.10.1以消除漏洞影响。

2．使用腾讯御知网络空间风险雷达（网址：<https://s.tencent.com/product/yuzhi/index.html>）进行风险扫描和站点监控，及时修复Web服务器安全漏洞。

3．网站管理员可使用腾讯云网站管家智能防护平台（网址：<https://s.tencent.com/product/wzgj/index.html>），其具备Web入侵防护，0Day漏洞补丁修复等多纬度防御策略，可全面保护网站系统。

##  **0x6 IOCs**

###  **C2：**

[www.bk1433.top](http://www.bk1433.top)

> 61.147.120.245
>
> kk321.f3322.net
>
> 216.118.225.250
>
> 10.0.2.15

[www.sgzca.win](http://www.sgzca.win)

> xs516.f3322.net
>
> 123.207.162.18

###  **md5 **：****

> 35b4395ae17f5b4125de6ee07d6bdde6
>
> 96725ba1ca94113f5b4e082f8b37ce6f
>
> ae96e22912145a7d4c5ada7911e4061f
>
> 46cfbf8b219a0c8845a212510576d2f8
>
> 1ed6c5dfa3dbb26fc758b16dc5aac9d7
>
> 5aa908705f019df2b70029c76150314b
>
> 49c1980e48ad9a425126abd11400d4c4
>
> f0744ef4ffbb474e1d438bd0cfd73eec
>
> 9bc3a69211711a5e417c2b3029f3bac5
>
> 49d2f2344ad8fc17427d44bf4693884d
>
> 97ff66fd9a73137db18bde42ef1fc85a
>
> a53babe49f07d8826c7eda7675c5a73f
>
> 748d3d940525836eed70cbfc032facb3

 ***本文作者：腾讯电脑管家，转载请注明来自FreeBuf.COM**

