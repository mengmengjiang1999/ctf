**作者：R17a  
本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！ 投稿邮箱：paper@seebug.org**

近期最火的漏洞莫过于log4j2 RCE漏洞，都说是史诗级的漏洞，那必然要分析下。

## 0x01 定位漏洞

既然是利用了jndi，那么断点就打在`javax.naming.InitialContext`构造方法肯定是没错的。

![](https://images.seebug.org/content/images/2021/12/dd2e2d02-f7be-4529-ab65-a03c7ecd0702.png-w331s)
通过回溯，最初调用lookup相关的地方在`org.apache.logging.log4j.core.lookup.StrSubstitutor.replace()`

![](https://images.seebug.org/content/images/2021/12/1f4a13d3-297f-4187-9555-b6fbb758c3d8.png-w331s)

进一步回溯分析调用lookup的原因，在`MessagePatternConverter.format()`中，遍历每个字符，当匹配到`${`就调用`StrSubstitutor.replace()`处理jndi相关信息。

![](https://images.seebug.org/content/images/2021/12/aa7b0bcb-b338-4ca7-a007-b164b42d60aa.jpg-w331s)

## 0x02 log4j日志记录及漏洞分析

在详细分析前先简单了解下log4j三大组件：

  1. Logger：日志记录器，负责收集处理日志记录
  2. Appender：日志存放的地方，负责日志的输出
  3. Layout：日志格式化，负责日志输出的形式

1、在log4j2中通过`LoggerConfig.processLogEvent()`处理日志事件，主要部分在调用`callAppenders()`即调用Appender：

![](https://images.seebug.org/content/images/2021/12/e1e0809e-c396-45d3-ba6f-59383ef1bb24.png-w331s)

2、Appender功能主要是负责将日志事件传递到其目标，常用的Appender有ConsoleAppender（输出到控制台）、FileAppender（输出到本地文件）等，通过AppenderControl获取具体的Appender，本次调试的是ConsoleAppender。

![](https://images.seebug.org/content/images/2021/12/109250ba-9107-4686-9eb6-a4d7d2f1b010.jpg-w331s)

调用`ConsoleAppender.tryAppend()`尝试输出日志

![](https://images.seebug.org/content/images/2021/12/4586f58d-3724-4792-9fb1-9cac596f8be9.png-w331s)

3、首先获取Layout日志格式，通过`Layout.encode()`进行日志的格式化

![](https://images.seebug.org/content/images/2021/12/a8dc2f7c-9f57-4f92-a85e-341199a7ae78.png-w331s)

Layout会获取formatters来完成具体的格式化的事情

![](https://images.seebug.org/content/images/2021/12/152629fc-397f-4577-be3d-6e992b5e83ed.png-w331s)

4、处理传入的message通过`MessagePatternConverter.format()`，也是本次漏洞的关键之处，我们具体来看下。首先创建一个workingBuilder，当config存在并且noLookups为false，匹配到`${'`则调用`workingBuilder.append()`获取StrSubstitutor内容来替换原来的信息（这里说明下，jndi执行命令后如果返回了结果就会将其append输出）

![](https://images.seebug.org/content/images/2021/12/d683ac3b-d344-4b36-a29f-4aaa42ba6a65.jpg-w331s)

noLookups来自设置来自配置文件，默认值为`false`，相当于默认支持jndi。

![](https://images.seebug.org/content/images/2021/12/2a917bcb-5917-4a28-a499-e93f9dcd82b2.png-w331s)

![](https://images.seebug.org/content/images/2021/12/2f24d349-3f7b-4b8a-9f60-def5464109f6.png-w331s)

5、`StrSubstitutor.resolveVariable()`解析变量，调用`Interpolator.lookup()`，Interpolator有date、
java、marker、ctx、jndi,、main、jvmrunargs、 sys、 env、 log4j共10种

![](https://images.seebug.org/content/images/2021/12/c5633adb-3ea7-4950-a3eb-d95ac2ab6e29.png-w331s)

根据前缀获取lookup为JndiLookup，后续就是jndi处理，这里不再继续。

![](https://images.seebug.org/content/images/2021/12/09524cf8-e926-451e-8f3e-23af0f1df8aa.png-w331s)

## 0x03 漏洞思考

那么究竟为什么要给log4j2开发jndi功能，特地去[官网](https://logging.apache.org/log4j/log4j-2.3/manual/configuration.html#PropertySubstitution)看了下，开发者最初考虑到使用log4j通过本地文件加载属性可能不够用，某些场景需要从更多的地方加载属性，因此设计了`Property
Substitution`.

![](https://images.seebug.org/content/images/2021/12/c01f7111-0536-466c-a40f-e52e326b250a.png-w331s)

jndi是，添加jndi服务主要是为了日志功能更加丰富，但是开发者没有考虑到jndi可能带来的危害。我想如果开发者在设计之初就考虑到了潜在的危害，考虑用白名单校验jndi的地址，便能够有效避免今天的局面。

<https://logging.apache.org/log4j/log4j-2.3/manual/lookups.html#ContextMapLookup>

![](https://images.seebug.org/content/images/2021/12/7e92b565-2063-4b29-bc09-08f73d6d6d38.jpg-w331s)

## 0x04 参考链接

<https://logging.apache.org/log4j/log4j-2.3/manual/lookups.html#ContextMapLookup>

<https://www.cnblogs.com/z-x-p/p/11534662.html>

<https://blog.csdn.net/henry115/article/details/78483457>

<https://blog.csdn.net/fygkchina/article/details/107183281>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1786/>

