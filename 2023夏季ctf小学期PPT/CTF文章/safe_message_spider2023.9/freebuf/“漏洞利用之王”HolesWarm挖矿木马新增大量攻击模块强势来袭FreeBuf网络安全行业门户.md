## **概述**

近期，威胁情报团队在活跃家族监控中捕获到了HolesWarm挖矿家族的最新变种。在本次更新中，该病毒家族
**新增了19种漏洞利用手法，横向攻击模块更是达到了31个** ，基本覆盖了大多数政企单位常用的服务组件，危害极大，应及时更新对应补丁做好防护。

HolesWarm也被称为AutoUpdate，首次披露于今年6月，是一个新型且十分活跃的挖矿家族，使用Golang编写，攻击目标同时覆盖Windows和linux双平台，除挖矿外还会窃取主机账户的登陆凭证等信息。
**本次更新，其新增漏洞利用模块之多，无愧于“漏洞利用王者”的称号。**

首次披露该家族分析文章：[支持双系统挖矿，警惕新型AutoUpdate挖矿病毒入侵](http://mp.weixin.qq.com/s?__biz=MzI4NjE2NjgxMQ==&mid=2650253736&idx=1&sn=87ef141c0aa1e66decde095e2684ca2c&chksm=f3e213dcc4959acac8fd2951f779e3b87a0c7b66c1e1601210096077552c3de23896523ea3c7&scene=21#wechat_redirect)

###  **漏洞利用模块更新**

本次更新漏洞利用模块新增19种，算上之前版本的漏洞利用模块一共31种，漏洞利用模块更新情况如下：

 **历史版本漏洞**

|

Docker未授权命令执行攻击  
  
---|---  
  
Jenkins 未授权命令执行攻击  
  
Shiro 反序列化 RCE  
  
Spring boot actuator RCE  
  
Struts2全系列（s008-s057）漏洞  
  
Tomcat 爆破攻击  
  
Weblogic RCE( CVE-2020-14882)  
  
XXL-JOB  
  
泛微OA E-cology Bsh 命令执行  
  
用友bsh.servlet.BshServlet 命令执行  
  
用友GRP-U8注入-命令执行  
  
致远OA htmlofficeservlet任意文件写入  
  
致远OA-ajax.do文件上传  
  
 **本次新增漏洞**

|

泛微OA代码执行漏洞  
  
---|---  
  
致远OA未授权漏洞  
  
weblogic （CVE-2017-10271）  
  
mongo-express RCE漏洞（CVE-2019-10758）  
  
Jupyter Notebook 未授权访问漏洞  
  
Apache Flink任意文件读写（CVE-2020-17518/19）  
  
Nexus Repository Manager 3远程命令执行(CVE-2019-7238)  
  
Apache ActiveMQ远程代码执行漏洞 (CVE-2016-3088)  
  
Apache Spark 未授权访问漏洞  
  
Hadoop Yarn REST API未授权漏洞  
  
万户网络-ezOFFICE 漏洞  
  
JBoss HttpInvoker反序列化漏洞（CVE-2017-12149）  
  
Confluence注入漏洞（CVE-2021-26084）  
  
YAPI接口管理平台RCE  
  
ShowDoc前台文件上传漏洞  
  
Fastjson 反序列化（CVE-2017-18349）  
  
ThinPHP代码执行漏洞  
  
###  **病毒攻击流程**

###
![](https://image.3001.net/images/20211130/1638255218_61a5ca729c17d1b4c847e.png!small)

###  **攻击活动趋势**

根据深信服安全云脑监控数据显示，该病毒持续处于活跃状态，近期攻击情况如下图所示：

![](https://image.3001.net/images/20211130/1638255261_61a5ca9d0f8e96e8a1fe8.jpg!small)

##  **样本详细分析**

###  **前置Loader**

 **Windows:**

当远程漏洞利用入侵成功后，植入名为loader.ps1/loader.bat脚本文件，脚本文件再下载主体控制模块services.exe到C:/Windows/Temp/.git/目录下，并对该目录进行隐藏。

 **Linux:**

当远程漏洞利用入侵成功后，植入名为loader.sh/loader.py脚本文件，脚本文件再下载主体控制模块kworkers到~/.git目录下，并对该目录进行隐藏。

###  **主体控制模块**

Service.exe和kwokers分别是windows和linux的主体控制模块，其功能是一致的都是根据配置文件windowsupdatev1.json下载、执行或更新其他功能模块，如挖矿模块dbus/update.exe、横向传播模块autoupdate等。

![](https://image.3001.net/images/20211130/1638255310_61a5caced0542da135fdd.png!small)

windowsupdatev1.json配置文件如下图:

filename字段为要下载的模块名称；

handle字段为要执行的动作（如下载、下载执行、更新等）；

url字段为下载的uri；

ver字段为对应的版本信息。

![](https://image.3001.net/images/20211130/1638255323_61a5cadb78076c2ed5507.png!small)

###  **横向传播模块**

 **Autoupdate**

横向传播模块autoupdate，先对内网网段进行端口扫描，并识别内网的http/https对应的服务是否存在漏洞，端口扫描如图：

![](https://image.3001.net/images/20211130/1638255339_61a5caeb199dec2b75c5f.jpg!small)

扫描识别对应的服务，如图：

![](https://image.3001.net/images/20211130/1638255632_61a5cc10f188e37d1cf71.png!small)

然后再用对应的漏洞利用模块进行攻击，如图：

![](https://image.3001.net/images/20211130/1638255654_61a5cc26bbff459ea4f7e.jpg!small)

 **sshkey.sh**

针对Linux平台，除了autoupdate外，还会下载sshkey.sh，通过该脚本遍历目录搜索失陷主机曾经登陆过的主机列表、曾使用的用户名以及ssh
key，并尝试使用这些用户名和密钥登陆其他主机，进一步进行横向传播，当登陆成功便下载执行前置loader。

![](https://image.3001.net/images/20211130/1638255703_61a5cc576793bf14016fa.png!small)

###  **进程隐藏模块**

###  **针对Windows平台**

Service.exe下载inj.exe和runtime.dll，来实现对挖矿模块updater.exe、横向传播模块autoupdate.exe以及主体控制模块service.exe进程进行隐藏。其中runtime.dll是开源的进程隐藏框架，通过inj.exe将runtime.dll注入到任务管理器进程，该dll再通过Hook
Native API NtQuerySystemInformation，来实现进程隐藏。

![](https://image.3001.net/images/20211130/1638255741_61a5cc7dbf79f6f7aacfb.png!small)

 **针对Linux平台**

Kworkers下载hideproc.sh进程隐藏脚本，该脚本下载processhide.c隐藏进程源文件，再将源文件编译成libc2.28.so，最后将libc2.28.so添加到系统的ld.so.preload文件，即实现启动进程时自动载入该链接库实现进程隐藏。

![](https://image.3001.net/images/20211130/1638255810_61a5ccc28082c9726aa76.jpg!small)

隐藏的进程为：主体控制模块kworkers，挖矿模块dbus以及横向传播模块autoupdate。如图：

![](https://image.3001.net/images/20211130/1638255481_61a5cb79689ae6570ae75.png!small)

###  **登陆凭证窃取**

 **针对windows平台**

主体控制模块service.exe会下载procdump文件，将系统进程lsass.exe进行内存dump，然后将dump下来的文件上传至C2服务器，服务器最终返回用户名密码信息，通信流量如图：

上传dump内存文件如图：

![](https://image.3001.net/images/20211130/1638255850_61a5ccead4a4008106300.png!small)

返回用户名密码如图：

![](https://image.3001.net/images/20211130/1638255862_61a5ccf616c497d38f71e.png!small)

 **针对Linux平台**

横向传播模块autoupdate通过遍历文件，查找云服务器的访问密钥Access key和Secret
key（当获取AK后便能够调用云账号下的所有资源和功能），当找到AK/Sk便会将数据上传至C2服务器，如图：

![](https://image.3001.net/images/20211130/1638255877_61a5cd051b390bfc87529.png!small)

###  **挖矿模块**

Windows端下载update.exe挖矿模块进行挖矿，Linux端下载dbus挖矿模块进行挖矿。两文件本质都是开源矿机XMRig，该病毒应该使用的是代理矿场，矿场地址便是其C2服务器：m.windowsupdatesupport[.]org:443，配置信息如图：

![](https://image.3001.net/images/20211130/1638255893_61a5cd15c8576aef18b32.png!small)

  

