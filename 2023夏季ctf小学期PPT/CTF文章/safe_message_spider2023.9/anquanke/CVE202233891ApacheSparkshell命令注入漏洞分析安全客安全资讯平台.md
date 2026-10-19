# CVE-2022-33891 Apache Spark shell命令注入漏洞分析

阅读量 **240212**

发布时间 : 2022-07-28 10:30:44

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t010de74eeb36b4d1cd.jpg)

## 漏洞描述

7月18号，Apache发布安全公告，修复了一个Apache
Spark中存在的命令注入漏洞。漏洞编号：CVE-2022-33891，漏洞威胁等级：高危。Apache Spark UI提供了通过配置选项Spark
.acl .enable启用acl的可能性。使用身份验证过滤器，这将检查用户是否具有查看或修改应用程序的访问权限。如果启用了acl,
HttpSecurityFilter中的代码路径可以允许某人通过提供任意用户名来执行模拟。
恶意用户可能能够访问权限检查功能，该功能最终将根据他们的输入构建一个 Unix shell 命令并执行它。这将导致任意 shell 命令执行。

## 相关介绍

Apache
Spark是美国阿帕奇（Apache）软件基金会的一款支持非循环数据流和内存计算的大规模数据处理引擎。Spark优点在于能更好地适用于数据挖掘与机器学习等需要迭代的MapReduce的算法。

## 利用范围

Spark Core – Apache <=3.0.3

3.1.1 <= Spark Core – Apache <=3.1.2

3.2.0 <= Spark Core – Apache <=3.2.1

## 漏洞分析

**环境搭建**

在官网（https://archive.apache.org/dist/spark）下载Apache Spark 3.2.1版本进行漏洞复现分析。

![](https://p0.ssl.qhimg.com/t019fc2a7c22f8b949b.png)

漏洞触发的关键在于是否启用ACL，使用身份验证过滤器。

启用ACL的两种方式：

1、通过设置选项 spark.acls.enable 启用 。

2、运行spark-shell时，通过-c参数启动。

为更好分析漏洞，在运行spark-shell前，需在其中进行远程调试配置

export
SPARK_SUBMIT_OPTS=”-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005″

![](https://p5.ssl.qhimg.com/t01b924e8787f529e77.png)

配置完成后运行spark-shell，并开启ACL

./spark-shell –conf spark.acls.enable=true

![](https://p5.ssl.qhimg.com/t01d210d99ff29532e0.png)

### **漏洞原理**

根据diff（https://github.com/apache/spark/pull/36315/files）分析。

![](https://p0.ssl.qhimg.com/t01ada98b8e60042cf6.png)

如上所示，使用命令拼接且没有做任何处理，而在修复的版本中直接删除了ShellBasedGroupsMappingProvider函数中对bash的调用。

### **动态分析**

了解漏洞原理之后，就该考虑如何触发漏洞。

在Apache spark启用ACL后，会通过HttpSecurityFilter这个filter进行权限的校验。

首先将断点打在org.apache.spark.ui.HttpSecurityFilter#doFilter函数处。

![](https://p3.ssl.qhimg.com/t01f9beec93b91502df.png)

在进入doFilter函数之后，首先会提取参数“doAs”的值，然后赋值给effectiveUser，进入org.apache.spark.SecurityManager#checkUIViewPermissions函数。

![](https://p2.ssl.qhimg.com/t0164ce11cc2388f8e9.png)

后续跟进一系列函数进行处理。

![](https://p1.ssl.qhimg.com/t01aec909dbcace5df2.png)

进入org.apache.spark.security.ShellBasedGroupsMappingProvider#getGroups函数时，username为传入参数。

![](https://p2.ssl.qhimg.com/t013588288958ef0a33.png)

随后进入org.apache.spark.security.ShellBasedGroupsMappingProvider#getUnixGroups函数。

![](https://p0.ssl.qhimg.com/t0137ed0ad077393d6a.png)

在这里username进行了拼接处理，因为我们传入的username参数可控，便形成了命令注入。

后续将通过executeAndGetOutput函数直接触发传入的命令，造成命令执行。

![](https://p2.ssl.qhimg.com/t0198fd727473e32520.png)

### **漏洞复现**

通过反单引号和参数“doAs”成功命令注入。

![](https://p5.ssl.qhimg.com/t01a3e74196f073d73b.png)

## 修复建议

建议受影响的用户升级到安全版本：Apache Spark 3.1.3、3.2.2 或 3.3.0 或更高版本。

## 参考材料

1.https://lists.apache.org/thread/p847l3kopoo5bjtmxrcwk21xp6tjxqlc

2.https://archive.apache.org/dist/spark/

3.https://github.com/apache/spark/pull/36315/files

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **星阑科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/277003](/post/id/277003)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [安全漏洞](/tag/安全漏洞)
  * [Apache Spark shell命令注入](/tag/Apache Spark shell命令注入)

 **+1** __2赞

 __收藏

![](https://p0.ssl.qhimg.com/t01ae1a72a720da3a7b.png) 星阑科技

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

