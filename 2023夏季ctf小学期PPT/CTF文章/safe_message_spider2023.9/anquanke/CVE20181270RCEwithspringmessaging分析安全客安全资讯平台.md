# CVE-2018-1270 RCE with spring-messaging分析

阅读量 **1438486**

发布时间 : 2019-12-23 16:30:40

 **x**

##### 译文声明

本文是翻译文章，文章原作者 adm1n，文章来源：adm1n.design

原文地址：<http://adm1n.design/2019/12/20/CVE-2018-1270%20Remote%20Code%20Execution%20with%20spring-messaging%20%E5%88%86%E6%9E%90/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t019bf60acaeddb33ee.jpg)

作者：Hu3sky@360CERT

## 漏洞详情

Spring Messaging 属于Spring Framework项目，其定义了Enterprise Integration
Patterns典型实现的接口及相关的支持（注解，接口的简单默认实现等）

<https://pivotal.io/security/cve-2018-1270>

## 影响范围

    
    
    Spring
    versions 5.0.x - 5.0.5
    versions 4.3.x - 4.3.16
    
    SpringBoot
    2.0.0及以下

Spring Framework允许应用程序通过spring-messaging模块通过简单的内存STOMP代理通过WebSocket端点公开STOMP。恶意用户（或攻击者）可以向代理发送消息，这可能导致远程执行代码攻击。

复现环境

<https://repo.spring.io/release/org/springframework/spring/5.0.0.RELEASE/>

## SPEL

spel是Spring Expression Language
即，spring表达式语言，是一个支持查询和操作运行时对象导航图功能的强大的表达式语言.支持以下功能

    
    
    文字表达式
    布尔和关系运算符
    正则表达式
    类表达式
    访问 properties, arrays, lists, maps
    方法调用
    关系运算符
    参数
    调用构造函数
    Bean引用
    构造Array
    内嵌lists
    内嵌maps
    三元运算符
    变量
    用户定义的函数
    集合投影
    集合筛选
    模板表达式

一个hello world

    
    
    import org.springframework.expression.ExpressionParser;
    import org.springframework.expression.spel.standard.SpelExpressionParser;
    
    public class Spel {
        public static void main(String[] args) {
            ExpressionParser parser = new SpelExpressionParser();
            String var1 = (String)parser.parseExpression("'Hello World'").getValue();
            int maxValue = (Integer) parser.parseExpression("0x7FFFFFFF").getValue();
            System.out.println(maxValue);
            System.out.println(var1);
        }
    }

![](https://p3.ssl.qhimg.com/t01e7cf2521e036bec4.png)

弹calc

代码

    
    
    String calc = (String)parser.parseExpression("T(Runtime).getRuntime().exec('open /Applications/Calculator.app/')").getValue();

![](https://p1.ssl.qhimg.com/dm/1024_436_/t0137ef574345a94494.png)

这里的T是类型操作符，可以从类路径加载指定类名称（全限定名）所对应的 Class 的实例，格式为：T(全限定类名)，效果等同于
ClassLoader#loadClass()

## Websocket

由于HTTP具有单向通信的特点，于是造成了Server向Client推送消息变得很难，需要使用轮询的方式，于是有了WebSocket，他支持双向通信，类似于聊天室模式，在这个会话里，Server和Clinet都能发送数据，相互通信，所以WebSocket是一种在一个TCP连接上能够全双工，双向通信的协议

## Stomp

STOMP即Simple (or Streaming) Text Orientated Messaging
Protocol，简单(流)文本定向消息协议，一个非常简单和容易实现的协议，提供了可互操作的连接格式，易于开发并应用广泛。这个协议可以有多种载体，可以通过HTTP，也可以通过WebSocket。在Spring-Message中使用的是STOMP Over WebSocket。

STOMP是一种基于帧的协议， STOMP是基于Text的，但也允许传输二进制数据。
它的默认编码是UTF-8，但它的消息体也支持其他编码方式，比如压缩编码。

一个STOMP帧由三部分组成:命令，Header(头信息)，Body（消息体）

    
    
    COMMAND
    header1:value1
    header2:value2
    
    Body^@

一个实际帧结构

    
    
    SEND
    destination:/broker/roomId/1
    content-length:57
    
    {“type":"ENTER","content":"o7jD64gNifq-wq-C13Q5CRisJx5E"}

spring 的消息功能是基于消息代理构建的

### demo

stomp的架构图

![](https://p3.ssl.qhimg.com/dm/1024_406_/t01c8653580fba520af.png)

图中各个组件介绍：

  * 生产者型客户端（左上组件）: 发送SEND命令到某个目的地址(destination)的客户端。
  * 消费者型客户端（左下组件）: 订阅某个目的地址(destination), 并接收此目的地址所推送过来的消息的客户端。
  * request channel: 一组用来接收生产者型客户端所推送过来的消息的线程池。
  * response channel: 一组用来推送消息给消费者型客户端的线程池。
  * broker: 消息队列管理者，也可以成为消息代理。它有自己的地址（例如“/topic”），客户端可以向其发送订阅指令，它会记录哪些订阅了这个目的地址(destination)。
  * 应用目的地址(图中的”/app”): 发送到这类目的地址的消息在到达broker之前，会先路由到由应用写的某个方法。相当于对进入broker的消息进行一次拦截，目的是针对消息做一些业务处理。
  * 非应用目的地址(图中的”/topic”，也是消息代理地址): 发送到这类目的地址的消息会直接转到broker。不会被应用拦截。
  * SimpAnnotatonMethod: 发送到应用目的地址的消息在到达broker之前, 先路由到的方法. 这部分代码是由应用控制的。

    
    
    git clone https://github.com/spring-guides/gs-messaging-stomp-websocket
    cd gs-messaging-stomp-websocket
    //回到spring-boot 2.0.1之前
    git checkout 6958af0b02bf05282673826b73cd7a85e84c12d3

几个重要的文件

GreetingController.java(相当于图中的SimpAnnotatonMethod)

    
    
    package hello;
    
    import org.springframework.messaging.handler.annotation.MessageMapping;
    import org.springframework.messaging.handler.annotation.SendTo;
    import org.springframework.stereotype.Controller;
    
    @Controller
    public class GreetingController {
    
    
        //使用MessageMapping注解来标识所有发送到“/hello”这个destination的消息，都会被路由到这个方法进行处理
        @MessageMapping("/hello")
        //使用SendTo注解来标识这个方法返回的结果，都会被发送到它指定的destination，“/topic/greetings”.
        @SendTo("/topic/greetings")
        public Greeting greeting(HelloMessage message) throws Exception {
            Thread.sleep(1000); // simulated delay
            return new Greeting("Hello, " + message.getName() + "!");
        }
    
    }

尤其注意，这个处理器方法有一个返回值，这个返回值并不是返回给客户端的，而是转发给消息代理的，如果客户端想要这个返回值的话，只能从消息代理订阅

WebSocketConfig.java

    
    
    package hello;
    
    import org.springframework.context.annotation.Configuration;
    import org.springframework.messaging.simp.config.MessageBrokerRegistry;
    import org.springframework.web.socket.config.annotation.EnableWebSocketMessageBroker;
    import org.springframework.web.socket.config.annotation.StompEndpointRegistry;
    import org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurer;
    
    //使用Configuration注解标识这是一个Springboot的配置类.
    @Configuration
    //使用此注解来标识使能WebSocket的broker.即使用broker来处理消息
    @EnableWebSocketMessageBroker
    public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {
    
        @Override
        public void configureMessageBroker(MessageBrokerRegistry config) {
            //应用程序以 /app 为前缀，而 代理目的地以 /topic 为前缀
            config.enableSimpleBroker("/topic");
            config.setApplicationDestinationPrefixes("/app");
        }
    
        @Override
        public void registerStompEndpoints(StompEndpointRegistry registry) {
            registry.addEndpoint("/gs-guide-websocket").withSockJS();
        }
    
    }

运行后

![](https://p1.ssl.qhimg.com/dm/1024_296_/t01e7993d443d59af60.png)

## 漏洞复现

在static/app.js

添加header，需要指定为selector，在文档里有说明，是一个选择器

<https://stomp.github.io/stomp-specification-1.0.html>

![](https://p1.ssl.qhimg.com/t01fc63c89317eda31e.png)

随便发送一条消息即可触发

![](https://p0.ssl.qhimg.com/dm/1024_469_/t016f0ec2fc74937806.png)

可以抓个包看到websocket发送的STOMP帧

点击connect时

![](https://p0.ssl.qhimg.com/dm/1024_105_/t01486e561dd839fb00.png)

![](https://p0.ssl.qhimg.com/dm/1024_49_/t01b16ab0ed48dd1afb.png)

点击send时

![](https://p4.ssl.qhimg.com/dm/1024_121_/t01270ec919013ef189.png)

## 漏洞分析

### SUBSCRIBE

先在ExecutorSubscribableChannel.class的run函数下断，可以发现先来的第一条命令是CONNECT

![](https://p4.ssl.qhimg.com/dm/1024_333_/t01f9f52543f150915f.png)

然后是SUBSCRIBE命令，此时的message如下

![](https://p1.ssl.qhimg.com/dm/1024_580_/t013ddc60bb858c57ae.png)

然后从header取出selector并判断是否为null

![](https://p1.ssl.qhimg.com/dm/1024_360_/t01e2a425d7cec6a051.png)

不为null后，调用expressionParser.parseExpression处理selector，返回给expression变量，

![](https://p4.ssl.qhimg.com/dm/1024_252_/t01eed4bb370e7e1c2f.png)

然后调用subscriptionRegistry.addSubscription方法添加订阅

传入sessionId，subsId,destination和expression，首先从sessionid中获得info，如果没有就注册订阅，存储着session里的东西，返回DefaultSubscriptionRegistry的实例info

![](https://p2.ssl.qhimg.com/dm/1024_177_/t011a194c0cb2c07d9e.png)

然后获取value，这里为null

    
    
    DefaultSubscriptionRegistry.SessionSubscriptionInfo value = (DefaultSubscriptionRegistry.SessionSubscriptionInfo)this.sessions.putIfAbsent(sessionId, info);

往下走，添加订阅

![](https://p0.ssl.qhimg.com/dm/1024_92_/t011eb20516683d85ce.png)

把destination put 进destinationLookup

![](https://p0.ssl.qhimg.com/dm/1024_260_/t01ffbd703865743a72.png)

然后调用Subscription初始化id和selector值，最后add进subs变量

![](https://p1.ssl.qhimg.com/dm/1024_73_/t014887e67b3284afef.png)

![](https://p2.ssl.qhimg.com/dm/1024_116_/t012d62b0e94ecdae3d.png)

然后在缓存中更新订阅

![](https://p1.ssl.qhimg.com/dm/1024_61_/t01bdae6b63dd6a0b39.png)

### Send

发送的message为

![](https://p2.ssl.qhimg.com/dm/1024_172_/t014b712f3e2aefb4e9.png)

前面的调用很多，我们之间从处理的地方开始跟进

![](https://p2.ssl.qhimg.com/dm/1024_262_/t01b9e841453dcf151b.png)

在这之前的调用栈，通过反射来调到我们请求的方法

![](https://p5.ssl.qhimg.com/dm/1024_533_/t015c8609c9fcfbec0c.png)

inovke处理完后，会返回我们的控制器里的值

![](https://p2.ssl.qhimg.com/dm/1024_190_/t010d320e1394785002.png)

往下执行，跟入handleReturnValue

![](https://p4.ssl.qhimg.com/dm/1024_98_/t01fed9bce88fbc8781.png)

调用getReturnValueHandler来获得handler变量，用于处理return数据，有默认的defaultDestinationPrefix

![](https://p1.ssl.qhimg.com/dm/1024_60_/t010a4bf1139a68b4e5.png)

继续跟进

![](https://p0.ssl.qhimg.com/dm/1024_142_/t01a50d1db7f2a4f271.png)

提取headers等信息

![](https://p4.ssl.qhimg.com/dm/1024_125_/t0151d83e91da98c7c7.png)

![](https://p0.ssl.qhimg.com/dm/1024_387_/t012151d52aa13738f1.png)

然后get Sessionid 为c01pvxeq

获取destination

![](https://p2.ssl.qhimg.com/dm/1024_249_/t010769a35f5c5f13e8.png)

进入for循环后，首先调用createHeaders，把sessionid传入，主要是设置session和header

![](https://p3.ssl.qhimg.com/dm/1024_287_/t01d1b3e5eeb703b719.png)

然后跟到convertAndSend

![](https://p4.ssl.qhimg.com/dm/1024_81_/t015b90783b6c67de76.png)

调用doConvert函数得到message，然后调用send，开始发送message

![](https://p2.ssl.qhimg.com/dm/1024_87_/t01f7e6049c48c1ff0c.png)

![](https://p0.ssl.qhimg.com/dm/1024_65_/t018d16e629099a7ff4.png)

调用sendInternal

![](https://p4.ssl.qhimg.com/dm/1024_65_/t0132f5bf442141187c.png)

message

![](https://p0.ssl.qhimg.com/dm/1024_115_/t01d328e235405d84a5.png)

由于timeout为-1，所以调用send传入message参数

![](https://p4.ssl.qhimg.com/dm/1024_97_/t0138d36ae9e938781d.png)

![](https://p4.ssl.qhimg.com/t010c665bb736e85805.png)

跟入sendInternal

![](https://p0.ssl.qhimg.com/dm/1024_80_/t01665fb2eb65a249c0.png)

![](https://p4.ssl.qhimg.com/dm/1024_192_/t01295b07c19cd855f6.png)

![](https://p3.ssl.qhimg.com/dm/1024_171_/t011d45cb1239b955f9.png)

![](https://p1.ssl.qhimg.com/dm/1024_185_/t012778cd865fedea30.png)

调用SimpleBrokerMessageHandler的handleMessageInternal

获取到信息后调用updateSessionReadTime更新时间

检测是否是perfix开头，这里发往的订阅目的地是/topic/greetings，所以checkDestinationPrefix为true

调用sendMessageToSubscribers发送message到订阅地址

![](https://p0.ssl.qhimg.com/dm/1024_153_/t017c95c8f75ca3d3ce.png)

跟入findSubscriptions查找订阅，检测destination，没有error则进入findSubscriptionsInternal函数

![](https://p1.ssl.qhimg.com/dm/1024_61_/t01faaaf3beb8103f7f.png)

![](https://p4.ssl.qhimg.com/dm/1024_241_/t01b995490541d71c7f.png)

这里的destinationCache变量是

![](https://p1.ssl.qhimg.com/t019f108d01b9f03a31.png)

还记得一开始处理订阅的时候么，我们有一些put操作，相当于存入缓存了，这里就是一个提取的操作

调用DefaultSubscriptionRegistry的getSubscriptions获取订阅信息，

![](https://p4.ssl.qhimg.com/dm/1024_103_/t010ee592cab876d7e3.png)

从整个订阅里获取全部的信息然后保存到一个迭代器里，并且赋值给info

![](https://p2.ssl.qhimg.com/dm/1024_269_/t013fe33445cf79ecda.png)

![](https://p1.ssl.qhimg.com/dm/1024_322_/t01f0cace53c5448951.png)

最后根据sessionID add result里

![](https://p3.ssl.qhimg.com/dm/1024_54_/t01881b65f1a45bfa67.png)

最后更新缓存

然后跟进filterSubscriptions

首先判断selector是否存在，存在则进入判断

result变量传入后形参是allMatches

提取出expression，判断不为空

![](https://p0.ssl.qhimg.com/dm/1024_51_/t01558e826d80d4e98f.png)

然后在getValue执行spel表达式

![](https://p1.ssl.qhimg.com/dm/1024_124_/t01696b828a2f9806f0.png)

调用链很长

![](https://p4.ssl.qhimg.com/dm/1024_984_/t01bcb96cef97abd13a.png)

## 修复

<https://github.com/spring-projects/spring-framework/commit/e0de9126ed8cf25cf141d3e66420da94e350708a#diff-ca84ec52e20ebb2a3732c6c15f37d37aL217>

![](https://p3.ssl.qhimg.com/dm/1024_77_/t01fb3b439e261a3206.png)

![](https://p5.ssl.qhimg.com/dm/1024_162_/t01c8217e04063685f4.png)

![](https://p3.ssl.qhimg.com/dm/1024_437_/t01e8ba22e08b50432c.png)

更改为要重用的静态计算上下文,SimpleEvaluationContext 对于权限的限制更为严格，能够进行的操作更少。只支持一些简单的Map结构。

来看看修改为SimpleEvaluationContext如下代码的执行情况

    
    
    import org.springframework.expression.EvaluationContext;
    import org.springframework.expression.Expression;
    import org.springframework.expression.ExpressionParser;
    import org.springframework.expression.spel.standard.SpelExpressionParser;
    import org.springframework.expression.spel.support.SimpleEvaluationContext;
    
    public class Spel {
        public static void main(String[] args) {
            ExpressionParser parser = new SpelExpressionParser();
            EvaluationContext context = SimpleEvaluationContext.forReadOnlyDataBinding().build();
            Expression calc = parser.parseExpression("T(Runtime).getRuntime().exec('open /Applications/Calculator.app/')");
            calc.getValue(context);
    
        }
    }

![](https://p1.ssl.qhimg.com/dm/1024_572_/t017a03f08289d0848a.png)

不再弹出calc。

## Reference

  * <https://my.oschina.net/genghz/blog/1796965>
  * <https://www.toptal.com/java/stomp-spring-boot-websocket>
  * <https://pivotal.io/security/cve-2018-1270>
  * <https://juejin.im/post/5b7071ade51d45665816f8c0>
  * <https://juejin.im/post/5b9cb6825188255c5546e5f4>
  * <https://spring.io/guides/gs/messaging-jms/>
  * <https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/messaging/simp/broker/DefaultSubscriptionRegistry.html>
  * <https://blog.csdn.net/pacosonswjtu/article/details/51914567>
  * <https://www.cnblogs.com/jmcui/p/8999998.html>

本文翻译自adm1n.design
[原文链接](http://adm1n.design/2019/12/20/CVE-2018-1270%20Remote%20Code%20Execution%20with%20spring-messaging%20%E5%88%86%E6%9E%90/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/195537](/post/id/195537)

安全客 - 有思想的安全新媒体

本文转载自:
[adm1n.design](http://adm1n.design/2019/12/20/CVE-2018-1270%20Remote%20Code%20Execution%20with%20spring-messaging%20%E5%88%86%E6%9E%90/)

如若转载,请注明出处：
<http://adm1n.design/2019/12/20/CVE-2018-1270%20Remote%20Code%20Execution%20with%20spring-messaging%20%E5%88%86%E6%9E%90/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __2赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

