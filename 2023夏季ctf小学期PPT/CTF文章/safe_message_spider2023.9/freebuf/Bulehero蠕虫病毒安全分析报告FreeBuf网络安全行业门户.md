# 一、概述

近日知道创宇404积极防御团队通过知道创宇云防御安全大数据平台（GAC）监测到大量利用Struts2、ThinkPHP等多个Web组件漏洞进行的组合攻击，并捕获到相关样本，经分析确认该样本为Bulehero蠕虫病毒。目前该Web攻击均被创宇盾拦截；知道创宇NDR流量监测系统也已经支持检测所有相关恶意IOC及流量。

# 二、追溯分析

### 1.发现攻击

2020年7月26日，通过日志分析发现IP：47.92.*.*（北京）、119.23.*.*（广东）、117.89.*.*（南京）等多个 IP
对客户网站发起 Web 漏洞攻击，通过远程下载并执行恶意文件 Download.exe，如下：

ThinkphpV5进行攻击：

![](https://image.3001.net/images/20200812/1597212404.png!small)

Tomcat PUT方式任意文件文件上传：

![](https://image.3001.net/images/20200812/1597212483.png!small)

Struts2远程命令执行：

![](https://image.3001.net/images/20200812/1597212512.png!small)

经过分析，发现Download.exe为下载器，执行流程如下：

![](https://image.3001.net/images/20200812/1597212563.png!small)

图1-执行流程

### 2.详细分析

2.1 Download.exe

Download.exe作为下载器，攻击成功之后会继续前往 http://UeR.ReiyKiQ.ir/AdPopBlocker.exe
下载AdPopBlocker.exe到系统TEMP目录并创建名为Uvwxya和fmrgsebls的计划任务来实现自启动，如下：

![](https://image.3001.net/images/20200812/1597212592.jpg!small)

图2-下载母体AdPopBlocker.exe

![](https://image.3001.net/images/20200812/1597212608.jpg!small)

图3-下载母体到TEMP目录

2.2 AdPopBlocker.exe

AdPopBlocker.exe作为母体会释放扫描模块、MSSQL爆破模块、挖矿模块等同时启动web攻击模块。

释放扫描模块到目录C:\Windows\iqvebecsc\ilebaiib下，并通过内置的几个IP查询网站获取自身的外网IP：

![img](https://image.3001.net/images/20200812/1597212683.jpg!small)

图4-获取自身外网IP

随后将生成的IP段地址保存为ip.txt，启动端口扫描工具对IP地址的80、8080等端口进行扫描，扫描完成后将扫描结果保存到result.txt。病毒会同时对内网以及外网IP地址攻击，使其传播更为广泛。

![img](https://image.3001.net/images/20200812/1597212705.jpg!small)

图5-扫描的IP段文件

![img](https://image.3001.net/images/20200812/1597212729.jpg!small)

图6-内置的部分IP段

释放永恒之蓝攻击模块到C:\Windows\iqvebecsc\UnattendGC目录,针对开放139/445端口的电脑利用永恒之蓝攻击模块进行攻击，攻击成功后植入Payload(AppCapture32.dll/AppCapture64.dll)，如下图：

![img](https://image.3001.net/images/20200812/1597212754.jpg!small)

图7-永恒之蓝攻击模块

![img](https://image.3001.net/images/20200812/1597212769.png!small)

图8-释放永恒之蓝攻击模块到UnattendGC目录下

![img](https://image.3001.net/images/20200812/1597212786.jpg!small)

图9-139/445端口扫描

利用MSSql sa用户弱口令进行爆破，使用的部分密码字典如图：

![img](https://image.3001.net/images/20200812/1597212801.jpg!small)

图10-sa用户弱口令爆破

![img](https://image.3001.net/images/20200812/1597212817.jpg!small)

图11-1 部分密码字典

使用Mimikatz搜集本机登录密码

![img](https://image.3001.net/images/20200812/1597212833.jpg!small)

图11-2 本机密码搜集

释放挖矿模块，并使用XMRig/6.6.2版本连接 185.147.34.10进行挖矿：

![img](https://image.3001.net/images/20200812/1597212849.jpg!small)

图12-挖矿

发起Web攻击：

Struts2远程命令执行漏洞（CVE-2017-5638）攻击

![img](https://image.3001.net/images/20200812/1597212863.jpg!small)

图13-Struts2漏洞攻击

PhpStudy后门漏洞攻击

![img](https://image.3001.net/images/20200812/1597212876.jpg!small)

图14-Phpstudy后门攻击

ThinkPHPV5远程代码执行漏洞（CNVD-2018-24942）攻击

![img](https://image.3001.net/images/20200812/1597212910.jpg!small)

图15-ThinkPHPV5漏洞攻击

Tomacat PUT方式任意文件上传漏洞（CVE-2017-12615）攻击

上传名为FxCodeShell.jsp的Webshell，如下：

![img](https://image.3001.net/images/20200812/1597212928.jpg!small)

图16-上传的Webshell

Apache Solr 远程命令执行漏洞（CVE-2019-0193）攻击

![img](https://image.3001.net/images/20200812/1597212945.jpg!small)

图17- Apache Solr漏洞攻击

Drupal远程代码执行漏洞（CVE-2018-7600）攻击

![img](https://image.3001.net/images/20200812/1597212961.jpg!small)

图18- Drupal漏洞攻击

Weblogic反序列化远程代码执行漏洞（CVE-2019-2725）攻击

![img](https://image.3001.net/images/20200812/1597212981.jpg!small)

图19- Weblogic漏洞攻击

# 三、防护建议

> 服务器暂时关闭不必要的端口（如135、139、445）；
>
> 下载并更新Windows系统补丁，及时修复永恒之蓝系列漏洞；
>
> 定期对服务器进行加固，尽早修复服务器相关组件安全漏洞，安装服务器端的安全软件；
>
> 服务器切勿使用弱口令，避免暴力破解。

# 四、附：IOCs

 **IP**|  **地理位置**  
---|---  
88.218.16.210| 荷兰  
172.105.239.24| 日本  
  
139.162.72.83

| 日本  
185.147.34.10| 荷兰  
URL  
---  
  
http://gie.ezrutou.ir:63145/conf.dat  
  
http://UeR.ReiyKiQ.ir/AdPopBlocker.exe  
http://172.105.239.24/sesnordateservice.exe  
Domain  
---  
UeR.ReiyKiQ.ir  
gie.ezrutou.ir  
  
ai.0x1725.site  
  
386be8418171626f63adb52d763ca1c0五、参考链接[https://www.freebuf.com/column/180544.html](column/180544.html
"https://www.freebuf.com/column/180544.html")

 **MD5**|  43f064685ed285cd8373759fb54ec238| 50ca2f5c614dd456a5fba497a33e587b|
6d2a5d8b341883a7403b48363144c054  
---|---|---|---
