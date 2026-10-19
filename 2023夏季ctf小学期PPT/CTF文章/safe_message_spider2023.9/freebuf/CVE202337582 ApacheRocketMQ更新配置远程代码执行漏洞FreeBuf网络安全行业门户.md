## ****项目介绍****

Apache RocketMQ是由阿里捐赠给Apache的一款低延迟、高并发、高可用、高可靠的分布式消息中间件。 经历了淘宝双十一的洗礼。
RocketMQ既可为分布式应用系统提供异步解耦和削峰填谷的能力，同时也具备互联网应用所需的海量消息堆积、高吞吐、可靠重试等特性。

##  ** **项目地址****

https://github.com/apache/rocketmq

##  ** **漏洞概述****

在RocketMQ
5.1.1及以上版本中，当RocketMQ的NameServer暴露在外网且缺乏权限验证时，恶意攻击者可以通过未授权访问利用更新配置功能以RocketMQ运行的系统用户身份上传含有特定内容的文件到任意目录。此外，攻击者可以通过伪造
RocketMQ 协议内容来达到同样的效果。

##  ** **影响版本****

Apache RocketMQ <= 5.1.1

##  ** **环境搭建****

参考官方文档使用docker启动存在漏洞版本的RocketMQ

1）启动NameServer

docker run -it --net=host apache/rocketmq:5.1.1 ./mqnamesrv

2）启动Broker

$ docker run -it --net=host --mount
source=/tmp/store,target=/home/rocketmq/store apache/rocketmq:5.1.1 ./mqbroker
-n localhost:9876

##  ** **漏洞复现****

![](https://image.3001.net/images/20230720/1689824549_64b8ad25d99c6d61f79c5.png!small)

![](https://image.3001.net/images/20230720/1689824562_64b8ad3286aa951be2217.png!small)

##  ** **漏洞分析****

在修复CVE-2023-33246时，有两条补丁链接过滤了相关参数禁止实时修改配置文件

<https://github.com/apache/rocketmq/commit/c3ada731405c5990c36bf58d50b3e61965300703>

https://github.com/apache/rocketmq/commit/9d411cf04a695e7a3f41036e8377b0aa544d754d

对这两个补丁进行分析发现，两个补丁分别是对不同版本的rocketmq进行修复，这里仅介绍5.1.1版本的修复补丁，补丁代码逻辑一致分别涉及NameServer、Broker、Controller组件，都是禁止修改相关配置文件路径。

问题出在NameServer的补丁链接上如下

DefaultRequestProcessor.java![](https://image.3001.net/images/20230720/1689831673_64b8c8f9618adc57247ea.png!small)

这处补丁过滤了kvConfigPath和configStorePathName值。这个地方比较关键，后面会提到。

###  ** **文件上传漏洞****

文件上传漏洞的形成有两个核心条件，1、文件路径及后缀可控2、文件内容可控

5.1.1 版本的rocketmq中NameServer服务器可以同时满足，从而造成文件上传漏洞。下面进行核心代码逻辑分析

 ** **1、文件路径及后缀可控****

NameServer在更新配置内容时会进行写文件操作，文件路径由
getStorePath方法决定，因此可控![](https://image.3001.net/images/20230720/1689831691_64b8c90b0a957b8c6a9a1.png!small)

getStorePath方法如下，通过debug发现，最后返回值是由NamesrvConfig对象的configStorePath变量决定的（在上述补丁中过滤的是configStorePathName，因此被绕过）![](https://image.3001.net/images/20230720/1689831719_64b8c9279452a83a5ac51.png!small)

![](https://image.3001.net/images/20230720/1689831731_64b8c9331c70541bd9e13.png!small)

这个值能否修改呢？答案是可以。跟踪调试代码后可知下面这部分代码会通过反射将相关参数赋值给configObjectList中存储的配置对象。![](https://image.3001.net/images/20230720/1689831754_64b8c94abda4d1b904fda.png!small)

其中就有NamesrvConfig对象，因此我们可以实时修改配置文件的路径![](https://image.3001.net/images/20230720/1689831767_64b8c957282a3b89f9dc0.png!small)

  *  ** **文件内容可控****

下面代码将所有配置对象中的参数全部合并到allConfigs中并转换成字符串![](https://image.3001.net/images/20230720/1689831788_64b8c96c33f3617ac7dfb.png!small)

最终将全部配置信息写入了configStorePath指定的文件中。该文件权限是rocketmq启动时的用户权限。因此只要不出现kvConfigPath即可绕过校验。

###  ** **命令执行漏洞****

Linux crontab
是用来定期执行程序的命令。当安装完成操作系统之后，默认便会启动此任务调度命令。所有用户定义的crontab文件都被保存在/var/spool/cron目录中，其文件名与用户名一致，文件中的每一行都代表一项任务，每行的每个字段代表一项设置，它的格式共分为六个字段，前五段是时间设定段，第六段是要执行的命令段，格式如下：

minute hour day month week command

不满足上述格式的行会被crontab 自动忽略。

结合以上信息，可以通过写入crontab文件达到命令执行的目的。

###  ** **补丁分析****

CVE-2023-37582的补丁比较简单，过滤了configStorePath值，因此无法修改上传路径![](https://image.3001.net/images/20230720/1689831797_64b8c9756d57aa75ac56c.png!small)

##  ** **修复方式****

升级Apache RocketMQ到5.1.2或者4.9.7安全版本

###  ** **参考链接****

<https://github.com/apache/rocketmq/pull/6843>

https://lists.apache.org/thread/m614czxtpvlztd7mfgcs2xcsg36rdbnc

