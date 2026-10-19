### 概述

威胁狩猎是在大数据中反复检索那些逃避传统安全设备的攻击手法，旨在发现未知威胁。大致流程如下：  
`收集数据 - 建立假设 - 工具分析 - 丰富威胁上下文 - 分析自动化`  
威胁狩猎是一个主动的行为。之前团队内打算做一个日志分析平台，初步选型以splunk为框架，使用一段时间后发现一个问题，splunk处理windows日志会存在日志解析失败情况。这就产生一个问题，编写的splunk检测规则无法生效。而站在乙方角度，分析安全事件要看细节，容不得日志解析失败，否则会影响分析效率。反之甲方角度来看处理有限范围内的告警即可。

### 收集数据

 **1、Windows日志**

数据类型

|

描述

|

路径

|

采集/分析工具  
  
---|---|---|---  
  
操作系统日志

|

Windows 操作系统日志是一些记录和存储系统事件和故障信息的文件，用于诊断计算机问题、监测资源使用情况、保护系统安全等

|

C:\Windows\System32\winevt\Logs

|

事件管理器  
  
主机行为日志

|

Windows行为日志是一种记录计算机系统活动的日志文件，包括系统启动和关闭、驱动程序加载、应用程序安装和卸载、用户登录和注销、文件和文件夹新增、删除等。行为日志可以帮助系统管理员诊断问题，查找安全漏洞，并进行系统性能和配置优化。

|

/

|

sysmon

商业EDR

  
  
  
关键位置的文件

|

windows上记录用户行为或者操作系统行为的其他文件

|

C:\Users\\{username}\AppData

C:\Users\<用户名>\AppData\Roaming

\Microsoft\Windows\PowerShell\PSReadLine

C:\Windows\Prefetch

  

C:\Windows\AppCompat\Programs\Amcache.hve

  

C:\Windows\System32\Tasks

  

注册表：

ShimCache

AppCompatCache

Userassist

MuiCache

|

AppCompatCacheParser

ShimCacheParser

AmcacheParser

JumpListExplorer  
  
 **2、Linux日志**

数据类型

|

描述

|

路径

|

采集工具  
  
---|---|---|---  
  
系统日志

|

系统日志是由系统服务和应用程序生成的记录。它包括系统启动过程中的信息、服务和应用程序启动和关闭的信息，还有一些错误和警告信息。

|

/var/log/messages

/var/log/syslog

/var/log/auth.log

/var/log/kern.log

/var/log/dmesg

/var/log/boot.log

/var/log/secure

/var/log/cron

|  
  
  
应用程序日志

|

应用程序日志是在应用程序中使用的记录和报告机制。它包括应用程序问题的错误消息、应用程序性能的统计信息、跟踪和调试日志，以及其他应用程序相关的信息。

|

/var/log/apache

|  
  
  
审计日志

|

审计日志是操作系统记录和监视系统活动的功能。审计日志包括系统事件、用户活动、系统配置、网络连接和网络流量等信息。管理员可以使用Linux审计日志来识别和跟踪安全事件和系统问题，以及了解系统运行的风险和问题。

|

/var/log/audit

|

audit  
  
关键位置的文件

|

linux上记录用户行为或者操作系统行为的其他文件

|

/tmp/

/home/{username}/.ssh/*

/home/{username}/.bash_history

/home/{username}/

/etc/ld.so.preload

/etc/crontab /var/spool/cron/*

/etc/init.*

|  
  
  
 **3、流量**

采集流量需要最大限度地覆盖当前网络中的所有通信流量，并将其标准化解析后存储系统中。这里要注意两点，一是部署探针设备要能采集到同网段及跨网段主机间的流量，二是针对ssl协议要进行字段解析。

###  **建立假设**

在威胁狩猎过程中，建立假设这一步骤是至关重要的。为此，我们可以依托痛苦金字塔模型和ATT&CK框架来帮助我们确定各项指标。痛苦金字塔模型提供了多项指标，包括Hash、IP、Domain、网络行为、攻击工具等，这些指标可以通过最新的公开Blogs获取。

![1686459463_648554478b552a277cf63.png!small?1686459464186](https://image.3001.net/images/20230611/1686459463_648554478b552a277cf63.png!small?1686459464186)

通过公开的渠道一般不易获取攻击者的完整行为。这时可以结合ATT&CK框架，针对不同的攻击阶段和攻击技术进行分类和分析，从而建立更加全面和准确的假设。通过这些措施可以更好地发现潜在的威胁。

![1686459483_6485545bba81def57fe59.png!small?1686459484607](https://image.3001.net/images/20230611/1686459483_6485545bba81def57fe59.png!small?1686459484607)

###  **工具分析**

企业如果购买了商业版的安全设备，可以基于设备本身的日志调查语法进行威胁狩猎。如果自建的话，日志分析多采用ELK、Splunk，流量分析一般用Suricata或者Snort。如下是一些开源的检测规则集

    
    
    https://github.com/Bert-JanP/Hunting-Queries-Detection-Ruleshttps://github.com/SigmaHQ/sigmahttps://github.com/mbabinski/Sigma-Ruleshttps://github.com/joesecurity/sigma-ruleshttps://github.com/12306Br0/Security-operation-book

然后根据搭建平台的搜索语法将威胁假设转换为检测规则。通过规则检出威胁后需要进一步验证威胁。

###  **丰富威胁上下文**

发现攻击痕迹后，下一步就是复现完整的攻击路径。这个环节主要是对目标进行取证。可以依托ATTCK框架来做，规则检测发现的只是一个点，而作为分析师需要将一个点还原成一条线。比如：在对日志进行威胁狩猎的时候，通过规则检测发现的是一条日志，那么这条日志是什么样的操作触发的呢。以及操作系统为什么会触发这样的操作。在这个环节多问几个"Why"，能让检测规则更严谨。

###  **分析自动化**

威胁狩猎首要是数据，其次是流程，最后是自动化，自动化的程度决定了狩猎思路的应用范围。在设置自动化的时候不仅要考虑检测规则本身，还要加一个规则可信度。通过规则的可信度提升规则优化空间，保证检出的准确率。但自动化这一块并不好做，多数攻击行为会产生多条日志，需要多条日志关联分析。

###  **案例**

ASMX是一种基于.NET平台的Web服务，使用.ASMX文件扩展名，网站使用XML来传递数据，并使用SOAP协议来进行通信。它提供了一种简单的方法来创建Web服务，并可用于提供网站的服务存储和操作数据。

某次hunt过程中发现流量中存在.asmx后缀的url。

![1686459541_64855495bd20dc58762ee.png!small?1686459542213](https://image.3001.net/images/20230611/1686459541_64855495bd20dc58762ee.png!small?1686459542213)

遂访问该URL发现该页面泄露了网站API。

![1686459561_648554a91da0460a55ef6.png!small?1686459561664](https://image.3001.net/images/20230611/1686459561_648554a91da0460a55ef6.png!small?1686459561664)

切到该目录的上级目录，又发现网站存在目录遍历漏洞。

![1686459585_648554c11cab7ed2c8c6a.png!small?1686459585665](https://image.3001.net/images/20230611/1686459585_648554c11cab7ed2c8c6a.png!small?1686459585665)

如上案例，我们可以总结出两个狩猎规则

    
    
    (1) url中包含".asmx"(2) url中包含".asmx"，访问url的上级目录判断是不是存在目录遍历漏洞

来源公众号:huasec

