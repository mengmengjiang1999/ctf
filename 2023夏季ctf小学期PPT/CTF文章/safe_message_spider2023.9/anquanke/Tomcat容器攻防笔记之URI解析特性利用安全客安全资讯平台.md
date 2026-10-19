# Tomcat容器攻防笔记之URI解析特性利用

阅读量 **210835**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-02-08 10:00:46

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t0116251f7a76c95d7b.png)

* * *

## 一、提要

Hello，好久不见，最近琐事缠身，也是抽空对Tomcat这个基础特性，做了点微小的工作。

回归正题，在日常代码审计的过程中发现，Tomcat原生javax.servlet.http.HttpServletRequest类提供的getRequestURI()方法，在解析请求时若使用不当，可以绕过访问控制，导致未授权访问。

事实上，Tomcat在解析请求路径时，会自行修正路径，并使用修正后的路径来匹配对应的Servlet，然而，在路径需要修正的情况下，Tomcat自行修正后得到的URI路径跟使用getRequestURI方法得到的URI路径不一致，因而在我们去对请求路径做权限访问控制时，容易导致绕过。

ok，前情提要浅尝即止，接下来，上号！

![](https://p5.ssl.qhimg.com/t01b5eb780cb8c364ff.png)

## 二、URI解析特性

这次换个思路，逆流而上，先来看看，Tomcat是根据什么来匹配对应的Servlet。

回顾先前文章，涉及流的解析与对象封装，那就是Tomcat架构中Connector连接器与Container容器的桥梁org.apache.catalina.connector.CoyoteAdapter#prepare，在那里新建和封装Request和Response对象，并最终在postParseRequest方法的this.connector.getService().getMapper().map()中完成对Servlet的绑定。走，看看去。

![](https://p0.ssl.qhimg.com/t01c34d14491764e967.png)

阿~是decodedURI，后面是根据decodeURI来匹配Servlet的，可以，现在我们去追溯一下decodedURI。适配器CoyoteAdapter作为桥梁，首先被调用Prepare方法，在其中新建Request及Response对象，并调用postParseRequest方法对Request对象完成数据封装。

![](https://p5.ssl.qhimg.com/t01a5618105eafce743.png)

看方法名识方法作用，进入postParseRequest方法，该方法会对请求所使用的协议、方式等进行判断，并一一封装入Request对象中，略过，直捣黄龙。

![](https://p2.ssl.qhimg.com/t01f34eed7c3bfec12f.png)

decodeURI从req,decodedURI()中取出，刚取出时为null，(由于undecodedURI的Type为2时指代bytes类型，满足if条件)，随后进入if逻辑，通过duplicate(复制)，复制得到了undecodedURI的值。这里调试时，访问的地址为“/txxx/;abc/index.jsp”。随后进入parsePathParameters方法，进一步解析URI。

![](https://p5.ssl.qhimg.com/t01d77a0bbe6711b141.png)

举一个例子说明处理流程，比方说访问的URI为“/t/;a=1;b=2/./../index.jsp”  
首先根据分号来进行分割出A部分和B部分.  
A部分:”/t/“  
B部分:”a=1;b=2/./../index.jsp”  
然后查找B部分中，第一个分号的下标，分割出pathVariables简称pv(路径参数)以及C部分。  
pv部分:”a=1”  
C部分:”;b=2/./../index.jsp”  
将A部分与C部分进行拼接得到D部分  
D部分:”/t/;b=2/./../index.jsp”

![](https://p2.ssl.qhimg.com/t019c4583c4e8ee47e6.png)

而每次分割得到的pv，会判断是否含有等于号，含有则会被保存为pathParameters，因此上述最后得到pathParameters={“a”:”1”,
”b”:”2”}，没有等于号，则直接忽略pv。

重复以上流程，直到分割后的第二部分不存在分号，最后得到“/t//./../index.jsp”

![](https://p1.ssl.qhimg.com/t01b8cbeabc14ea8f87.png)

到这里，parsePathParameters(req,
request)就完成了，然后进入602行req.getURLDecoder().convert(decodedURI,
false)，完成URL编码解析，再之后进入607行normalize(req.decodedURI())方法，该方法顾名思义用于规范化URI，会对URI进行进一步的修正。

normalize方法主要有四个修正行为，一一列举。

![](https://p1.ssl.qhimg.com/t01a3fa03af31596992.png)

反斜杠的Ascii码为“92”，将URI中所有的“\”修正为“/”

![](https://p1.ssl.qhimg.com/t017c940e31cc9d68ad.png)

斜杠的Ascii码为“47”，将URI中紧邻的两个斜杠修正为一个斜杠，形如“/t//./../index.jsp”修正为“/t/./../index.jsp”

![](https://p1.ssl.qhimg.com/t012ac0eb8080d97a1a.png)

第三第四合在一起说，首先修正URI中的“/./”，例如将“/t/./../index.jsp”修正为”/t/../index.jsp”,随后，解析“/../”进行URI路径跳跃，例如将“/t/../index.jsp”最终解析为“/index.jsp”

![](https://p0.ssl.qhimg.com/t0183ee1f5706598c22.png)

综上，normalize()方法结束后，Tomcat对于当前请求的URI已经解析完毕，并保存在变量decodedURI中，并最终交由this.connector.getService().getMapper().map(serverName,
decodedURI, version, request.getMappingData());根据decodedURI来匹配对应的Servlet。

而我们原本访问的URI“/t/;a=1;b=2/./../index.jsp”则保存在Coyote.Request实例的uriMB当中。

## 三、利用场景

对于各种业务系统而言，理所应当会存在多用户多角色的访问控制，具体表现在是否有足够的权限去调用后端的接口，而实现访问控制很重要的前提就是通过用户当前请求的路径来进行判断匹配。

打个比方说，用户test，不可以访问“/admin”接口，从业务代码实现起来，就是判断用户test当前访问的URI是否等价于”/admin”,如果等价，则响应401权限不足。

这里边的问题是什么呢？仍有部分开发者，习惯地通过HttpServletRequest.getRequestURI()的方式，来获取当前请求的URI。承接前面我们的分析，补充一下，该方法事实上是返回了Coyote.Request中的uriMB，也就是没有经过Tomcat修正的URI。

因此可能会产生这么一种情况：用户test访问的URI经过修正后，实际访问的是“/admin”,但后端使用getRequestURI()方法得到的URI跟“/admin”不等价，结合上面分析举个例子，很容易明白：“/;/admin”、“/;a/admin”、“/;a=1/admin”

以上三个路径跟”/admin”无法等价，但经Tomcat修正后，访问的却恰恰是“/admin”。

## 四、修复方案及延伸

    
    
    String uri = request.getContextPath() + request.getServletPath();
    

不同的框架可能在资源解析中各有差异，就像先前Spring与Shiro之间的解析差异产生的未授权访问，因此日常审计也可以多留心这条思路。

从修复漏洞，抵御风险，提高系统安全性的角度来说，需尽保证关键数据、关键对象，传递和使用的一致性，以免岔路

![](https://p3.ssl.qhimg.com/t01738b3588885c9be7.jpg)

欢迎各位师傅留言交流，一起玩耍

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **鲸落** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/230238](/post/id/230238)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)
  * [Tomcat](/tag/Tomcat)

 **+1** __5赞

 __收藏

![](https://p5.ssl.qhimg.com/t0180afe1d6131dd030.png) 鲸落

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

