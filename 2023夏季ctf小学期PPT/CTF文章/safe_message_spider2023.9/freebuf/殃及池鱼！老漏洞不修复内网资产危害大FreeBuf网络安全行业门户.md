## 背景

**近日，深信服安全团队接到安全感知报警提示内网某Linux核心Web服务器对内网其他服务器发起永恒之蓝和Struts2漏洞攻击等，报警主机被标记为已失陷。经过安全专家排查发现服务器存在较大的安全隐患，攻击者利用Web漏洞作为入口深入内网进行探测，试图窃取敏感数据。**

主要入侵路径如下图所示：

![图片1.png](https://image.3001.net/images/20190923/1569203682_5d8825e2d27c4.png!small)

## 总体情况

通过安全感知平台检测到有某linux主机对内网部分主机进行永恒之蓝攻击和Struts2漏洞利用等攻击行为，并且检测到针对部分其他主机存在Struts2漏洞的成功利用的场景。

![图片2.png](https://image.3001.net/images/20190923/1569203691_5d8825eb56602.png!small)

![安全感知平台.png](https://image.3001.net/images/20190923/1569203710_5d8825fedcda4.png!small)

## 排查溯源

通过对风险主机进行排查，查看进程时发现有一些明显的异常进程，/bin/sh -c 执行了很多异常的命令。

![图片3.png](https://image.3001.net/images/20190923/1569203722_5d88260a16db6.png!small)

查看进程树发现这些进程均是由Web进程发起的，并且还使用了frp代理工具进行代理转发穿透内网，同时针对内网发起ping包的扫描。

![图片4.png](https://image.3001.net/images/20190923/1569203776_5d882640430a9.png!small)

怀疑入口点在Web处，于是查看了访问日志。

查看进行可以发现，
该应用使用Nginx反向代理了内网多个Tomcat站点，从上面的Web父进程路径找到对应的Tomcat的访问日志，发现安全事件爆发前后的日志果然被删除了，并且/tmp目录下的代理工具frp和配置文件frp.ini也被清理了。既然对应站点的访问日志被清除，那Nginx中的总代理访问日志access.log应该会被入侵者遗漏掉。

查看目录，access.log果然没有被删除，从中找到了安全平台警报的内网攻击安全事件前后的Web访问日志。

![图片5.png](https://image.3001.net/images/20190923/1569203780_5d882644eace8.png!small)

通过日志可以看到早在8月30号入侵者就开始对Web站点进行摸索，然后在POST
/***/***.action之后出现了尝试访问Webshell，然后直至Webshell返回200的记录。由此怀疑是利用Struts2漏洞导致命令执行，写入的Webshell。

在下一步的渗透中，入侵者还上传了更多的Webshell和代理jsp，把受害主机当做跳板，对内网的80,8080，443端口进行扫描。

![图片6.png](https://image.3001.net/images/20190923/1569203786_5d88264a70f76.png!small)

入侵者利用扫描结果摸清内网，利用著名工具蚁剑2.1继续操控Webshell，继续对内网的站点进行Struts2漏洞攻击和永恒之蓝攻击。这些攻击均被深信服安全感知平台所发现并进行了记录与告警。

![图片7.png](https://image.3001.net/images/20190923/1569203787_5d88264bad0dc.png!small)

![图片8.png](https://image.3001.net/images/20190923/1569203791_5d88264f87af3.png!small)

入侵者还使用知名的frp代理工具将内网端口暴露到外网，用来进入更深的内网。其中，frp代理Server端均为国外服务器。

![图片9.png](https://image.3001.net/images/20190923/1569203795_5d8826530f6c2.png!small)

![图片10.png](https://image.3001.net/images/20190923/1569203797_5d88265578f1d.png!small)

通过利用poc对入口点漏洞进行验证，证实入口点的确存在Struts2漏洞。

##
![图片11.png](https://image.3001.net/images/20190923/1569203801_5d8826590f69f.png!small)
解决方案

1\.
建议广大用户及时下载并更新最新的Struts2包：<https://struts.apache.org/>，参考官方意见处置：<https://cwiki.apache.org/confluence/display/WW/Security>
Bulletins

2\. 删除主机Web目录下的Webshell文件，并停止Webshell起的子进程，关闭frp反向代理，停止暴露内网端口；

3\.
根据安全平台的分析中心的安全检测日志，筛选被攻击成功的主机日志，参照建议1、2再次进行Struts2版本升级、对应的Webshell和黑客工具删除以及关闭恶意进程。

4\. 平时多注意平台的安全警报，关注内网安全动态，及时升级安全平台和威胁感知探针。推荐使用深信服安全感知+防火墙+EDR，对内网进行感知、查杀和防护。

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

