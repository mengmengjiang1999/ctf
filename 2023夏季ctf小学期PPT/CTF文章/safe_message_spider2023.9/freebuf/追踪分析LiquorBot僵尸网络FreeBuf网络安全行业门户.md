![](https://image.3001.net/images/20200114/1579001795_5e1da7c348d6a.jpg!small)

## 前言

**自2016年起，Mirai僵尸网络就因发动大规模网络攻击并摧毁各种基础设施而闻名于众，它也已经成为了网络安全领域对中、大型物联网僵尸网络评估的一个参考因子。自从它开源之后，很多对僵尸网络感兴趣的人都会根据Mirai的源码来构建自己的僵尸网络，因此便出现了各式各样的Mirai变种，除了以破坏为目的的网络攻击之外，现在也开始有人在利用受损设备的算力来进行挖矿活动了。**

Bitdefender的研究人员近期正在追踪分析一款名为LiquorBot的僵尸网络，这款僵尸网络同样是基于Mirai源码开发的，而且它目前也正处于积极开发阶段，最近甚至还加入了挖门罗币的功能。

有趣的是，LiquorBot采用Go语言开发，与传统的C语言风格代码相比，Go提供了很多其他的编码优势，比如说内存安全、垃圾回收、结构类型等等。

### 关键发现

> 1、使用Go语言对Mirai进行了重新编译；
>
> 2、交叉编译，涉及多种架构（ARM、ARM64、x86、x64、MIPS）；
>
> 3、引入了加密货币挖矿功能；
>
> 4、利用SSH爆破以及路由器漏洞来实现传播感染；

## Dropper脚本

LiquorBot被交叉编译为多种体系架构，针对了各种CPU架构，其中包含ARM、ARM64、x86、x64、MIPS。在感染过程中，Dropper脚本会下载所有的Bot
Payload，这里不会根据目标设备的CPU架构来进行逻辑过滤。

Dropper脚本代码本身并不多，主要用于从攻击者控制的服务器获取源码文件。该脚本另一个比较有趣的特点是它使用了“#!/bin/sh”，这比使用“#!/bin/bash”更加稳定可靠。除此之外，由于脚本似乎没有加载“bash”支持的任何特定功能，因此恶意软件开发人员选择了“sh”变种来作为系统脚本应使用的默认Shell。

![](https://image.3001.net/images/20200114/1579001809_5e1da7d116839.png!small)

攻击者所使用的挖矿程序配置脚本似乎还针对CPU挖矿算法设置了不同的哈希率：

![](https://image.3001.net/images/20200114/1579001812_5e1da7d4f1567.png!small)

## LiquorBot功能

跟Mirai类似，LiquorBot会对其字符串进行混淆处理，并存储至一个映射表中。每次访问一个条目时，都需要向每个字符串添加值“0x51”来完成解密。下图列出的是LiquorBot解密字符串的情况：

![](https://image.3001.net/images/20200114/1579001821_5e1da7dde7cf6.png!small)

它还从Mirai借鉴了另一个功能，即通过尝试进行端口绑定来确保单个Bot能够在目标设备上正常运行。Bot所使用的主机地址和端口会以参数的形式发送至映射表中的“net.Listen”（条目9），其他版本的Bot会将监听端口设置为42007。

![](https://image.3001.net/images/20200114/1579001826_5e1da7e27fb81.png!small)

开始执行之后，Bot会进行重启，然后尝试伪装成sshd守护进程来运行。

Bot还会以下列形式并将数据写入/etc/resolv.conf来更新DNS解析器：

![](https://image.3001.net/images/20200114/1579001830_5e1da7e63ff68.png!small)

Bot的生命周期还包含一个清理阶段，此时它会删除所有植入的文件 (/tmp/.lmr,/tmp/.ldrop,
/tmp/config.json)并清除Bash历史记录。

Bot会跟下列多个服务器进行通信：

> 1、CnC：Bot向服务器报告目标设备的漏洞，并从服务器接收控制命令；
>
> 2、挖矿服务器；
>
> 3、托管恶意代码的服务器；

C&C服务器可以响应下列命令：

> download
>
> rget
>
> exec
>
> Shutdown

恶意软件传播

LiquorBot可以利用某些关键CVE漏洞以及其他各种命令注入和远程代码执行漏洞，其中包括但不限于:

> CVE-2015-2051, CVE-2016-1555, CVE-2016-6277,CVE-2018-17173, CVE-2017-6884,
> CVE-2018-10562, CVE-2017-6077, CVE-2017-6334, CVE-2016-5679, CVE-2018-9285,
> CVE-2013-3568, CVE-2019-12780

## 入侵威胁指标IoC

> 14592719e2a354633131bc238f07aa0cb9cce698
>
> 1611a8445085d1687c72b7e5a7c5602cbe580c8b
>
> 1f15195ddc1e4174674fbf5d1fc95ed0a7726f7b
>
> 2784a122089c20d5c02665da1241fe02f9ac90cc
>
> 2901d4ee7f289bf0b1a863bec716d751f66a4324
>
> 2d1d294aac29fab2041949d4cb5c58d3169a31d3
>
> 31176239ab5187af5d89666f37038340b95a5a4e
>
> 31d9ca734c5f4c1787131d3a1b6b91ca60e57794
>
> 331ec23c250b86d912fa34e0e700bfcac1a7c388
>
> 3453a96414e63a813b82c6d98fa3b76c1824abd8
>
> 36382165bb53a7ed9387a02e5b9baee36fe23f64
>
> 48c863e4ad23fb946386320f3a85391b54ba50ad
>
> 49602256c8d65d0620d5abe8011a78425c7ae177
>
> 54bdfa936c9eb4ea329ca35b95e471d51daef1d5
>
> 5821ff8eb9b23035a520e1fb836e43b1ec87ffaf
>
> 61abc90c20930c7615880ac9931778b48b9e6ebd
>
> 63b556a0afcf643337310254cc7f57c729188f36
>
> 65cd6a0371bdfffd7383907ba9a816e8e2e95da5
>
> 6c7a92d5d68b68ddba10af7ca6350cfb24b2595f
>
> 6d24c472b06e6f9ac3204ca768319d2b035a210a
>
> 8364c272e0c95ed214c71dbcb48f89c468544bc8
>
> 8df16857cb914f5eded0249cfde07f1c01697db1
>
> a69f9f5f2ac15aec393ab68277ec268c0624fe91
>
> b40f4f13b2b144946b165a2e4284c96fbc0d4682
>
> b9dd4d230d103b3db458d752d4917466ec1cb9b0
>
> ba55d92e3d7dba70205597433f1a98b35e4911b8
>
> bb07341ab6b203687845ae38cd8c17dfc947e79f
>
> c59dd90f7cefadaa80d9c0113f8af39e4ed0c1a1
>
> c5adabbdbf641f3e53e3268af60ac1b26088aa6b
>
> c6d850e264d7d8d6978cd85d69c22b29378e34e4
>
> c7ed7241e2d21fa471b6bfd6b97b24b514b3c5f2
>
> d216f33695421dfb17e69ed05aec46cf84b544b7
>
> d59175ffacd8895362253a3bcb18637ced765fcd
>
> d62cdd8f16a8f6b6cde5e8da633c224eab4765f2
>
> e91f2d5df4ef43cb4c69b15de9a68c7ff2d4951d
>
> fd65e6c5ae07c50c7d7639e2712c45324d4cf8de

### 相关域名：

> ardp.hldns.ru
>
> bpsuck.hldns.ru
>
> Wpceservice.hldns.ru
>
> systemservice.hldns.ru

 *** 参考来源：[ _bitdefender_](https://labs.bitdefender.com/2020/01/hold-my-beer-mirai-spinoff-named-liquorbot-incorporates-cryptomining/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

