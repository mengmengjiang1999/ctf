# Tomcat CVE-2018-1305 分析

阅读量 **498409**

|评论 **4**

发布时间 : 2018-02-28 12:00:20

 **x**

##### 译文声明

本文是翻译文章，文章原作者 n1nty

原文地址：<https://mp.weixin.qq.com/s/PZsOQy2lpR1lHqLWmAXlbg>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t0100a651715653abbb.png)

近日，Apache Tomcat爆出两个安全绕过漏洞 ，Apache Tomcat
7、8、9多个版本受到影响。攻击者可以利用这个问题，绕过某些安全限制来执行未经授权的操作。本篇文章只对CVE-2018-1305进行简要分析。

## 两个 CVE

  1. CVE-2018-1305
  2. CVE-2018-1304

从造成的影响方面来讲，都是鸡肋。从原理上讲有点像，基本可以认为是同一个。从分析角度来讲，这两个都比较简单。

这里只对 CVE-2018-1305 进行简要分析。

## 背景知识

Java EE 提供了类似 ACL 权限检查的注解，可以直接用于修饰 Java Servlet，用于对 Servlet 进行 ACL 保护。

## 简要分析

现假设有两个 Servlet：

  1. Servlet1，访问路径为 /servlet1/*
  2. Servlet2，访问路径为 /servlet1/servlet2/*

Servlet1 上有如下图的 Security Constraint（简单理解就是 ACL）：

![](https://p1.ssl.qhimg.com/t018973149d73a93ba7.png)

Servlet2 上并没有 ACL。

然而因为 Servlet2 的访问 url 位于 Servlet1 的下一级（/servlet1/servlet2 是 /servlet1/ 的
“子目录”），所以 Tomcat 中正常的代码逻辑应该是，虽然 Servlet2 上面没有 ACL，但是 Servlet2 应该继承 Servlet1 的
ACL。

正常情况应该是：

  1. 先访问 /servlet1，返回 403，因为请求被 ACL 拦截了
  2. 再访问 /servlet1/servlet2，返回 403，因为请求被 ACL 拦截

**那么实际的问题在哪里？**

Tomcat 在接收到 Servlet 访问请求后，在实例化 Servlet 对象之前，会先扫描被访问的 Servlet 上注册的 ACL。如果存在
ACL，则将 ACL 规则添加到一个 Context 唯一的列表中。随后再检查当前访问的 Servlet 是否被 ACL 保护。

ACL 扫描 org.apache.catalina.authenticator.AuthenticatorBase#invoke：

![](https://p4.ssl.qhimg.com/t017a5d9e6152153601.png)

ACL 检查 org.apache.catalina.authenticator.AuthenticatorBase#invoke：

![](https://p3.ssl.qhimg.com/t01e726a60d25b0affb.png)

问题出在，如果在 Servlet1 （/servlet1）被访问之前，有人先访问了 Servlet2（/servlet1/servlet2）。流程如下：

  1. Tomcat 接收到 Servlet2 的访问请求
  2. Tomcat 扫描 Servlet2 上注册的 ACL，发现 Servlet2 上没有注册 ACL
  3. Tomcat 检查 Servlet2 是否被 ACL 保护。这一步，因为 Servlet2 在 Servlet1 之前被访问，所以导致 Servlet1 上注册的 ACL 规则还没有被 Tomcat 发现。所以，原本应该被 Servlet1 的 ACL 规则保护的 Servlet2，就处在了未受保护的状态。

## 实例

![](https://p1.ssl.qhimg.com/t01f9a0cfdf5d6b8895.png)

  1. 访问 http://localhost:8080/CVE-2018-1305/servlet1/servlet2，此时 servlet1 的 ACL 没被 Tomcat 加载，所以访问成功
  2. 访问 http://localhost:8080/CVE-2018-1305/servlet1，被拒绝访问了，此时 Tomcat 加载了 servlet1 的 ACL
  3. 再访问 http://localhost:8080/CVE-2018-1305/servlet1/servlet2，被拒绝访问了，因为 Tomcat 已经加载了 servlet1 的 ACL

## Tomcat 的修复

Tomcat 的修复了 ACL 注册的方式。以前是采用，在 Servlet 真正被访问之前才去注册此 Servlet 上的 ACL。现在改成了，在
Context 启动的时候，就去扫描该 Context下所有的 Servlet 上注册的 ACL，并添加到 acl 列表中。

在任何一个 Context 启动时，Tomcat 都会自动调用：

org.apache.catalina.startup.WebAnnotationSet#loadApplicationServletAnnotations

而其中，添加了如下 ACL 相关代码：

![](https://p4.ssl.qhimg.com/t01ceb781fe4cd496a2.png)

## 影响范围

只有当你使用的 Tomcat 处于受影响的 Tomcat 版本，而且你的应用依赖于 Java EE Constraints 来进行 ACL
保护的时候，才受影响。

本文翻译自 [原文链接](https://mp.weixin.qq.com/s/PZsOQy2lpR1lHqLWmAXlbg)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **n1nty** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/99213](/post/id/99213)

安全客 - 有思想的安全新媒体

本文转载自: [](https://mp.weixin.qq.com/s/PZsOQy2lpR1lHqLWmAXlbg)

如若转载,请注明出处： <https://mp.weixin.qq.com/s/PZsOQy2lpR1lHqLWmAXlbg>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞](/tag/漏洞)
  * [漏洞分析](/tag/漏洞分析)
  * [CVE-2018-1305](/tag/CVE-2018-1305)
  * [Tomcat](/tag/Tomcat)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t0186e94c8e6c6cdf1c.jpg) n1nty

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

