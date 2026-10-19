## 漏洞介绍：  

Apache Tomcat中的WebSocket存在安全漏洞，该漏洞源于程序没有正确验证payload的长度。攻击者可利用该漏洞造成拒绝服务（无限循环）。

## 漏洞影响范围：  

Apache Tomcat 10.0.0-M1-10.0.0-M6

Apache Tomcat 9.0.0.M1-9.0.36

Apache Tomcat 8.5.0-8.5.56

Apache Tomcat 7.0.27-7.0.104

## 漏洞修复方式：  

Apache Tomcat更新版本

其他方式：禁用或限制对WebSockets的访问

## 漏洞复现环境：  

CentOs7

tomcat9.30

jdk8

### 攻击方：

windows10

### 利用POC：  

tcdoc.exe  

## 漏洞复现步骤：  

centos以及tomcat环境搭建教程可以看我之前的文章 [点我查看](https://www.freebuf.com/vuls/255807.html)  

访问url地址发现tomcat默认存在的websocket地址：（tomcat部署完成后就存在）  

![1606445278_5fc068dee5813df3b4507.png!small?1606445276817](https://image.3001.net/images/20201127/1606445278_5fc068dee5813df3b4507.png!small?1606445276817)

下载测试poc：https://github.com/RedTeamPentesting/CVE-2020-13935  

安装说明步骤进行编译会报错，这里需要修改proxy地址，命令：go env -w GOPROXY=https://goproxy.cn  

编译成功：  

![1606445448_5fc06988526f795a1bd0f.png!small?1606445446183](https://image.3001.net/images/20201127/1606445448_5fc06988526f795a1bd0f.png!small?1606445446183)

![1606445390_5fc0694edb2510e1763c9.png!small?1606445388849](https://image.3001.net/images/20201127/1606445390_5fc0694edb2510e1763c9.png!small?1606445388849)

攻击服务器：  

![1606445495_5fc069b79fe45fabf70a3.png!small?1606445493517](https://image.3001.net/images/20201127/1606445495_5fc069b79fe45fabf70a3.png!small?1606445493517)

服务器cpu利用率瞬间达到100%：  

![1606445522_5fc069d2219bfb5b1b8a6.png!small?1606445519933](https://image.3001.net/images/20201127/1606445522_5fc069d2219bfb5b1b8a6.png!small?1606445519933)

## 漏洞浅析：  

根据redteam-pentesting分析的文章，这里说说我的理解。[点我查看](https://blog.redteam-pentesting.de/2020/websocket-vulnerability-tomcat/)  

我们看看WebSocket frame的结构:

参考RFC 6455 <https://tools.ietf.org/html/rfc6455#section-5.2>  

![1606445963_5fc06b8bb265ee90aff75.png!small?1606445961605](https://image.3001.net/images/20201127/1606445963_5fc06b8bb265ee90aff75.png!small?1606445961605)

图中说明，如果"负载长度"(payload length)设置为127，应该使用占64个bit的"扩展载荷长度"(extended payload
length)作为载荷长度，即8个bytes。  

 **看看WebSocket RFC要求：**

如果[7bit的载荷长度(payload length)]为127(二进制11111111``),
则接下来的8个bytes被解释为64-bit长的"无符号整数",作为载荷长度。 **无符号整数** **最高有效位需写为0。**  

 **这里应该是为了提高容错性，兼容错误的编程实现。因为无符号整数必然大于0，而有符号整数最高位才用1表示负数，0表示正数。**  

那么我们在构造"扩展载荷长度"(extended payload
length)时，将最高有效位设置为1，故意违反RFC规范，成为无效的载荷(payload)

以下是redteam-pentesting分析文章中关于无符号整数最高位的poc构造：  

> In order to construct a frame with an invalid payload length, triggering the
> misbehavior in the Apache Tomcat implementation, we set the following eight
> bytes to `0xFF`:
>  
>  
>     // set msb to 1, violating the spec and triggering the bug
>     buf.Write([]byte{0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF})

以上就是我的一写浅析，具体可查看redteam-pentesting分析 [点我查看﻿](https://blog.redteam-pentesting.de/2020/websocket-vulnerability-tomcat/)  

  

  

  

  

  

  

