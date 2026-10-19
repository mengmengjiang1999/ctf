![](https://image.3001.net/images/20190725/15640423357136.png!small)

## 一、前言

 **XStream是常用的Java类库，用来将对象序列化成XML （JSON）或反序列化为对象。**

## 二、漏洞简介

Xstream 1.4.10版本存在反序列化漏洞CVE-2013-7285补丁绕过。

## 三、漏洞危害

经斗象安全应急响应团队分析, 当使用Xstream
1.4.10版本且未对安全框架进行初始化时，攻击者即可通过精心构造的请求包在使用Xstream的服务器上进行远程代码执行。

## 四、影响范围

产品

Xstream

版本

Xstream1.4.10版本

组件

Xstream

五、漏洞复现

暂无

## 六、修复方案

升级Xstream到1.4.11版本

## 七、参考

> <http://x-stream.github.io/changes.html#1.4.11>
>
> [https://cve.mitre.org/cgi-> bin/cvename.cgi?name=CVE-2019-10173](http://www.example.com)

以上是本次高危漏洞预警的相关信息，如有任何疑问或需要更多支持，可通过以下方式与我们取得联系。

联系电话：400-156-9866

Email：help@tophant.com

斗象安全应急响应团队

2019年7月25日

