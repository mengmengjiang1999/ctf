***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

 **近期，360企业安全集团代码卫士团队安全研究人员发现Oracle公司旗下产品Oracle WebLogic
Server的多个高危安全漏洞（CVE-2018-3245、CVE-2018-3248、CVE-2018-3249、CVE-2018-3252），并第一时间向Oracle公司报告，协助其修复漏洞。**

Oracle WebLogic Server 是目前全球 J2EE
使用最广泛的商业应用中间件之一。北京时间2018年10月17日，Oracle公司发布了关键补丁更新公告（Oracle Critical Patch
Update Advisory - October 2018），公开致谢360企业安全集团代码卫士团队，并且发布相应的补丁修复漏洞。

![](https://image.3001.net/images/20181018/1539841507_5bc81de393be3.png!small)

Oracle公司官方公告

![致谢360代码卫士](https://image.3001.net/images/20181018/1539841522_5bc81df260be6.jpg!small)

致谢360代码卫士

在Oracle公司本次修复的漏洞中，CVE-2018-3245 和 CVE-2018-3252均为高危反序列化漏洞，影响多个 WebLogic
大版本，CVSS评分为9.8分，一定条件下，可以造成远程代码执行。本文将对这两个漏洞进行简单描述。

## 漏洞概述

### CVE-2018-3245 (JRMP Deserialization via T3)

该漏洞是一个绕过补丁的漏洞，在Oracle 7月份修复JRMP反序列化漏洞的补丁功能中可以被绕过，导致补丁无效。该漏洞高危，可远程执行任意代码。

### CVE-2018-3252 (Deserialization via HTTP)

这个漏洞的触发并不是官方描述的T3协议，而是通过HTTP的方式即可触发（危害更大，HTTP一般防火墙均可通过）。由于补丁发布时间不久，互联网上还有大量未及时打补丁的
WebLogic Server。该漏洞的细节暂时不公开。

## 参考链接

> Oracle Critical Patch Update Advisory - October
> 2018：<https://www.oracle.com/technetwork/security-> advisory/cpuoct2018-4428296.html>。

 ***本文作者：360代码卫士，转载请注明来自FreeBuf.COM**

