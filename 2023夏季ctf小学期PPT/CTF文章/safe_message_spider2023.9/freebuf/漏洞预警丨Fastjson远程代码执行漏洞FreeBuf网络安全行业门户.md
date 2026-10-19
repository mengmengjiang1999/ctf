![image.png](https://image.3001.net/images/20190711/15628167914967.png!small)  

## 一、前言

 **Fastjson是阿里巴巴的开源JSON解析库，它可以解析JSON格式的字符串，支持将Java
Bean序列化为JSON字符串，也可以从JSON字符串反序列化到JavaBean。**

## 二、漏洞简介

Fastjson 1.2.48版本以下存在反序列化漏洞补丁绕过。

## 三、漏洞危害

经斗象安全应急响应团队分析Fastjson多处补丁修补出现纰漏，Fastjson在1.2.48版本以下，无需Autotype开启，攻击者即可通过精心构造的请求包在使用Fastjson的服务器上进行远程代码执行。

## 四、影响范围

### 产品

Fastjson

### 版本

1.2.48以下版本

### 组件

Fastjson

## 五、漏洞复现

使用POC进行漏洞复现。

## 六、修复方案

1.升级Fastjosn到1.2.58版本，并关闭Autotype；

2.WAF拦截Json请求中的多种编码形式的‘@type’，‘\u0040type’等字样；

3.建议尽可能使用Jackson或者Gson；

4.升级JDK版本到8u121，7u13，6u141以上。

## 七、参考

<https://github.com/alibaba/fastjson>

以上是本次高危漏洞预警的相关信息，如有任何疑问或需要更多支持，可通过以下方式与我们取得联系。

 **联系电话：400-156-9866**

 **Email：help@tophant.com**

