## 一、前言

 **FasterXMLjackson-databind是一个简单基于Java应用库，Jackson可以轻松的将Java对象转换成json对象和xml文档，同样也可以将json、xml转换成Java对象。**

## 二、漏洞简介

FasterXMLjackson-databind2.9.9.2以下版本存在反序列化漏洞补丁绕过。

## 三、漏洞危害

经斗象安全应急响应团队分析，攻击者可以通过精心构造的请求包可以在受影响的Jackson服务器上进行远程代码执行。

![640.png](https://image.3001.net/images/20190731/15645410331818.png!small)

## 四、影响范围

### 产品

FastXML

### 版本

FasterXMLjackson-databind<2.9.9.2

FasterXMLjackson-databind<2.10.0

FasterXMLjackson-databind<2.7.9.6

FasterXMLjackson-databind<2.8.11.4

### 组件

FasterXMLjackson-databind

FasterXMLback-ported

## 五、修复方案

1、升级FasterXMLjackson-databind版本到2.9.9.2,2.10.0,2.7.9.6,2.8.11.4

2、不开启Jackson的defaultTyping选项

## 六、参考

> <https://github.com/FasterXML/jackson-databind/issues/2389>
>
> <https://github.com/FasterXML/jackson-databind/issues/2387>
>
> <https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-14379>
>
> <https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-14361>
>
> <https://github.com/Heartway>
>
> <https://github.com/yeahx>

以上是本次高危漏洞预警的相关信息，如有任何疑问或需要更多支持，可通过以下方式与我们取得联系。

联系电话：400-156-9866

Email：help@tophant.com

