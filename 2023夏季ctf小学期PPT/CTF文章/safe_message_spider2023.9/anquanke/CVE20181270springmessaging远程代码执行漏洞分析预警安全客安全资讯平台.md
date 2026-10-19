# CVE-2018-1270：spring-messaging远程代码执行漏洞分析预警

阅读量 **318953**

|评论 **1**

发布时间 : 2018-04-10 10:52:42

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t011730c673a60842e1.png)

报告编号： B6-2018-040901

报告来源： 360-CERT

报告作者： 360-CERT

更新日期： 2018-04-09

## 漏洞概述

2018年4月5日，Pivotal
Spring官方发布安全公告，Spring框架中存在三个漏洞,其中编号为CVE-2018-1270的漏洞可导致远程代码执行。

360-CERT通过对此漏洞进行了相关分析，认为漏洞影响严重；目前相关PoC已经被发布，建议相关用户尽快进行评估升级。

## 漏洞影响面

#### 影响版本

  1.     1. Spring Framework 5.0 to 5.0.4.
    2. Spring Framework 4.3 to 4.3.14
    3. 已不支持的旧版本仍然受影响  

#### 修复版本

    4. 5.0.x 用户升级到5.0.5版本
    5. 4.3.x 用户升级到4.3.15版本

## 漏洞详情

#### CVE-2018-1270

Spring框架中通过spring-messaging模块来实现STOMP（Simple Text-Orientated Messaging
Protocol），STOMP是一种封装WebSocket的简单消息协议。攻击者可以通过建立WebSocket连接并发送一条消息造成远程代码执行。如果使用了Spring
Security项目中的权限认证，可以在一定程度上增加漏洞利用难度。

#### CVE-2018-1271

当Spring MVC的静态资源存放在Windows系统上时，攻击可以通过构造特殊URL导致目录遍历漏洞。

此漏洞触发条件较高：

  1. Server运行于Windows系统上
  2. 从文件系统提供的文件服务（比如使用file协议，但不是file open）
  3. 没有使用CVE-2018-1199漏洞的补丁
  4. 不使用Tomcat或者是WildFly做Server

#### CVE-2018-1272

在Spring
MVC或者WebFlux应用把客户端请求再转向另一台服务器的场景下，攻击者通过构造和污染Multipart类型请求，可能对另一台服务器实现权限提升攻击。

## CVE-2018-1270漏洞分析

#### SpEL

Spring表达式语言全称Spring Expression
Language，支持查询和操作运行时对象导航图功能.。语法类似于传统EL，而且供额外的功能，能够进行函数调用和简单字符串的模板函数。

SpEL用法

    
    
    String expression = "T(java.lang.Runtime).getRuntime().exec(/"calc/")";
    String result = parser.parseExpression(expression).getValue().toString();
    

#### 漏洞触发流程

搭建spring-message 项目[demo](https://github.com/spring-guides/gs-messaging-stomp-websocket)

其中静态资源app.js运行在客户端与服务器做websocket交互，使用connect()函数建立Stomp链接

    
    
    function connect() {
            var socket = new SockJS('/gs-guide-websocket');
            stompClient = Stomp.over(socket);
            stompClient.connect({}, function (frame) {
                setConnected(true);
                console.log('Connected: ' + frame);
                stompClient.subscribe('/topic/greetings', function (greeting) {
                    showGreeting(JSON.parse(greeting.body).content);
                });
            });
        }
    

**Step1**

增加一个header头部，添加selector项，value为payload，Stomp协议规范中通过指定selector对订阅的信息进行过滤

![](https://p403.ssl.qhimgs4.com/t0114b79f18248b0efa.png)

Web应用在handleMessageInternal对消息进行处理，注册订阅者registerSubscription,最后调用DefaultSubscriptionRegistry函数对header参数进行处理，对selector值进行了解析，并将其保存至这次会话中。

![](https://p403.ssl.qhimgs4.com/t01265640c67dfa2b98.png)

**Step2**

点击send向服务器发送任意消息。Spring
在向订阅者分发消息时会调用filterSubscription对消息进行过滤，会执行`expression.getValue(context,
Boolean.class)`造成任意命令执行

![](https://p403.ssl.qhimgs4.com/t017a9a2894ba7f41d9.png)

#### 补丁分析

[补丁地址](https://github.com/spring-projects/spring-framework/commit/e0de9126ed8cf25cf141d3e66420da94e350708a#diff-ca84ec52e20ebb2a3732c6c15f37d37a)

    
    
    -import org.springframework.expression.spel.support.StandardEvaluationContext;
    +import org.springframework.expression.spel.support.SimpleEvaluationContext;
    

![](https://p403.ssl.qhimgs4.com/t01d18ae4bf5a4c9a93.png)

删除了`StandardEvaluationContext`引用，采用了`SimpleEvaluationContext`,`StandardEvaluationContext`可以执行任意SpEL表达式，Spring官方在5.0.5之后换用`SimpleEvaluationContext`，用于实现简单的数据绑定，保持灵活性减少安全隐患

[SimpleEvaluationContext地址](https://github.com/spring-projects/spring-framework/blob/v5.0.5.RELEASE/spring-expression/src/main/java/org/springframework/expression/spel/support/SimpleEvaluationContext.java)

[StandardEvaluationContext地址](https://github.com/spring-projects/spring-framework/blob/v5.0.5.RELEASE/spring-expression/src/main/java/org/springframework/expression/spel/support/StandardEvaluationContext.java)

## 时间线

**2018-04-05** Spring官方发布公告

**2018-04-09** 360-CERT发布分析预警通告

## 参考链接

  1. <https://xz.aliyun.com/t/2252>
  2. <https://pivotal.io/security/cve-2018-1270>
  3. <https://pivotal.io/security>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/104140](/post/id/104140)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞预警](/tag/漏洞预警)
  * [权限提升](/tag/权限提升)
  * [远程代码执行](/tag/远程代码执行)
  * [Spring框架漏洞](/tag/Spring框架漏洞)
  * [目录遍历](/tag/目录遍历)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

