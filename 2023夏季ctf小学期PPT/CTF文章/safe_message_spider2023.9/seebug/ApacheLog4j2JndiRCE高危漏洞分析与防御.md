**作者：启明星辰 ADLab  
原文链接：<https://mp.weixin.qq.com/s/19oIId_Ax2nxJ00k6vFhDg>**

漏洞编号：CVE-2021-44228  
CNVD编号：CNVD-2021-95919  
发布时间：2021年12月12日

# **_漏洞概述_**

Apache log4j2是一款Apache软件基金会的开源基础框架,用于 Java
日志记录的工具。日志记录主要用来监视代码中变量的变化情况，周期性地记录到文件中供其他应用进行统计分析工作；跟踪代码运行时轨迹，作为日后审计的依据；担当集成开发环境中的调试器的作用，向文件或控制台打印代码的调试信息。其在JAVA生态环境中应用极其广泛,影响巨大。

近日, Apache Log4j2
被曝存在JNDI远程代码执行漏洞，该漏洞一旦被攻击者利用会造成严重危害。该漏洞的触发点在于利用org.apache.logging.log4j.Logger进行log或error等记录操作时未对日志message信息进行有效检查,从而导致漏洞发生。

# **_漏洞时间轴_**

2014年7月13日：Apache Log4j2官方发布log4j-2.0此时该漏洞已经存在，距今7年之久；

2021年11月24日：阿里云安全团队向Apache官方报告了ApacheLog4j2远程代码执行漏洞（CVE-2021-44228）；

2021年12月8日：Apache Log4j2官方发布log4j2-2.15.0-rc1并第一次修复CVE-2021-44228漏洞；

2021年12月9日：启明星辰ADLab监测到Apache Log4j2官方公告并开展验证；

2021年12月10日：启明星辰ADLab确认漏洞存在，成功复现该漏洞并通报主管单位；

2021年12月10日：启明星辰ADLab研究确认log4j2-2.15.0-rc1存在Bypass的漏洞；

2021年12月10日：Apache Log4j2官方发布log4j2-2.15.0-rc2修复bypass漏洞。

# **_影响版本_**

Apache Log4j 2.x < =2.15.0-rc1

# **_漏洞详情_**

漏洞触发的调用链如下：

![](https://images.seebug.org/content/images/2021/12/d1c88af8-4824-4d64-86ce-24cb343732a4.png-w331s)

在进行Logger.log()日志记录时会采用logIfEnabled()方法进行判断，返回为true才可以继续进行日志操作。这里也是漏洞能否成功触发的关键。

![](https://images.seebug.org/content/images/2021/12/0597b350-11ca-49d7-881e-773e5e5e74de.png-w331s)

在本次漏洞分析过程中日志等级为Level.FATAL，它的intLevel()为100，而本环境中默认的日志级别为ERROR（200），如下图所示：

![](https://images.seebug.org/content/images/2021/12/8f9ad907-aa87-4996-9883-2ddb5000473c.png-w331s)

此时filter方法返回true，成功进入到logMessage的方法中。这里当Level等级优先级高于或等于ERROR（200）时（等级越高数值越低）才能触发漏洞；如WARN、INFO、DEBUG、ALL优先级低于ERROR（200），则无法触发该漏洞。也就是说，漏洞能否成功触发与设置的日志Level有关。

![](https://images.seebug.org/content/images/2021/12/c744bbd8-60a7-42cb-b2f3-bbfc2f6becc5.png-w331s)

然后，来到org.apache.logging.log4j.core.pattern.MessagePatternConverter的format()这个关键方法中，首先要判断noLookups这个变量的值，noLookups默认为false，意思为开启JNDI格式化功能。如下图所示：

![](https://images.seebug.org/content/images/2021/12/d316be2d-b445-4b7d-9b10-21c4ba6d332f.png-w331s)

我们根据之前的分析已经知道了noLookups这个变量的值为false的，!false的值为真，那么就进入到for循环里继续对log的message
event进行处理，取出${}中的数据进行后续lookup()操作。

![](https://images.seebug.org/content/images/2021/12/ab690ffd-d3f1-4864-9b40-c25f5ccc0ad8.png-w331s)

org.apache.logging.log4j.core.lookup.Interpolator的lookup()方法包含多种处理event的途径，根据event的prefix选择相应的StrLookup进行处理。包括jndi、date、Java、main等。

![](https://images.seebug.org/content/images/2021/12/894b8454-06eb-4a8a-b349-1acf24b1fa46.png-w331s)

当构造的event的prefix为jndi时，则通过org.apache.logging.log4j.core.lookup.JndiLookup的lookup()方法处理，从而触发JNDI漏洞利用。

![](https://images.seebug.org/content/images/2021/12/3ddc28d8-a6eb-4c32-89f5-69f8b704bdcc.png-w331s)

# **_几点疑问的解答_**

**1.Log4j 1.x版本是否存在该漏洞**

Log4j 1.x的最高版本为1.2.17，以下将1.x表示为小于等于1.2.17的所有版本。由于Log4j
1.x的代码和Log4j2相差比较大，没有Log4j2相对应的功能，所以Log4j 1.x版本不存在CVE-2021-44228漏洞。

通过深入分析源码后发现，如果我们能够控制配置文件log4j.properties中的内容，也可以达到JNDI注入的效果。示例如下：

![](https://images.seebug.org/content/images/2021/12/a98e9f4c-0ef9-4ca4-944e-91d1c2834edf.png-w331s)

成功利用如下图所示:

![](https://images.seebug.org/content/images/2021/12/ea73a272-d40d-46fd-bf0f-90fd7ef4c95e.png-w331s)

**2.只要用了Log4j2就会有漏洞吗**

有两个限制条件，第一个限制条件是：默认情况下，代码中日志等级的优先级高于或等于默认级别（ERROR（200），数值越低优先级越高）才可以成功，所以OFF、FATAL、ERROR均可被利用。如下图所示：

![](https://images.seebug.org/content/images/2021/12/3b90a2e5-b59c-4bbd-ab12-d33867018122.png-w331s)

但若是项目中采用配置文件的形式自定义日志级别，以Apache Struts2 为例，

Apache Struts2 默认日志级别为：info。如下图所示：

![](https://images.seebug.org/content/images/2021/12/17a005ae-553f-41aa-b2b6-50f362f402d6.png-w331s)

通过调试Struts2 Showcase，部署后获取到的初始日志级别为：info(400)。

![](https://images.seebug.org/content/images/2021/12/3f42578d-aace-489b-969f-0246598cd0f7.png-w331s)

当我们日志等级优先级高于或等于info(400)时，WARN、ERROR、FATAL、OFF、INFO这几个级别的日志都可能被利用，Apache
Struts2存在漏洞的位置如下图所示。

![](https://images.seebug.org/content/images/2021/12/16889134-0dd1-488c-9849-b3c809af08b3.png-w331s)

第二个限制条件是：必须能够控制日志内容。测试代码如下：logger.log(Level.ERROR,"xxx")；只有当log方法的第二个参数xxx的内容被污染的情况下才能被成功利用。

**3.用了高版本JDK，漏洞就免疫了吗**

看了一些大家对这个漏洞的讨论,很多人以为JDK版本高了就免疫了,某个网友评论如下图所示:

![](https://images.seebug.org/content/images/2021/12/a66cfeaa-b9e9-4789-a08f-72f0afaec18e.png-w331s)

在某些特定情况下，比如中间件用的Tomcat、Websphere,又比如存在反序列化漏洞的依赖包,攻击者同样可以绕过高版本JDK的限制达到RCE的目的。虽然高版本JDK对这个漏洞的防御不是那么完美，但仍强烈建议选用高版本的JDK，至少能提高黑客入侵的门槛。

**4.Log4j2 2.15.0-rc1补丁安全吗**

默认配置是安全的,因为默认已经不会通过lookup来处理日志内容，但如果配置文件由于配置不当，仍然有被利用的可能。比如以下配置即存在风险：

![](https://images.seebug.org/content/images/2021/12/32331303-61d4-461e-8306-130991a6fa22.png-w331s)

**5.Log4j2 2.15.0-rc2补丁安全吗**

rc1被绕过了，rc2是不是也能被绕过？结论是目前是安全的，因为rc2有诸多限制，如协议、白名单HOST、LDAP
Attributes限制等多个限制，其中白名单HOST限制如下所示：

![](https://images.seebug.org/content/images/2021/12/9ab7662c-5a4e-4651-9e32-0e94d0b295d2.png-w331s)

**6.单一WAF防御策略可行吗**

有些人觉得补漏洞太麻烦了，而且升级最新版本不兼容，更换版本后错误百出，不如用WAF来防御，阻断ldap、jndi这些关键字。目前针对绕过WAF的方法已经有很多种了，仅使用WAF拦截肯定会出现问题。

**7.加固了,为何仍存在漏洞**

我们看到早期文章加固方案基本按照下面这样写的：

（1）jvm参数 -Dlog4j2.formatMsgNoLookups=true

（2）在应用程序的classpath下添加log4j2.component.properties配置文件文件，文件内容：log4j2.formatMsgNoLookups=True

（3）设置系统环境变量FORMAT_MESSAGES_PATTERN_DISABLE_LOOKUPS 设置为true

很多人按照这个方案去加固，最后看到的结果是漏洞依然存在。这里有两点需要注意：

（1）这三个修复方案在2.10以下均处于失效状态。如果你用的2.10以下的版本，这样来加固肯定是不可以的。

（2）2.10版本以上，为什么也不成功。原因是设置环境变量FORMAT_MESSAGES_PATTERN_DISABLE_LOOKUPS为true并不会关闭lookup，而正确的修复方案是将LOG4J_FORMAT_MSG_NO_LOOKUPS设置为true。下面从代码层面详细分析为什么会这样。

通过跟踪代码发现，在初始化LogManager的Context环境时，会将系统环境变量加入到Log4j自己的属性环境中。当系统环境变量的key值前缀为“LOG4J_”时，自动截取“LOG4J_”之后的部分进行Util.tokenize(key)处理后加入到Environment的tokenized中。

![](https://images.seebug.org/content/images/2021/12/084d952b-a282-4a10-bcfa-881ac2297526.png-w331s)

Util.tokenize()方法对参数key进行正则匹配处理，然后返回处理后的List结果。正则匹配的规则为：

private static final Pattern PROPERTY_TOKENIZER =
Pattern.compile("(?i:^log4j2?[-.
_/]?|^org\\.apache\\.logging\\.log4j\\.)?([A-Z]*[a-z0-9]+|[A-Z0-9]+)[-._
/]?");

那么，如何设置key值才能成功让PropertiesUtil.getProperties().getBooleanProperty("log4j2.formatMsgNoLookups",
false);返回值为true呢？

跟踪代码发现，getBooleanProperty()获取属性也是通过查找PropertiesUtil.Environment中的normalized、literal和tokenized是否存在该属性判断的。而通过tokenized查找时，Util.tokenize(key)处理后的值作为key值然后在tokenized中进行匹配。

![](https://images.seebug.org/content/images/2021/12/65226e8a-55b0-413c-b1bf-3042ccac8c11.png-w331s)

我们再来看系统环境变量LOG4J_FORMAT_MSG_NO_LOOKUPS，去掉前缀LOG4J_后经Util.tokenize()处理后的结果如下图所示：

![](https://images.seebug.org/content/images/2021/12/70e4fe93-3d67-4686-8120-d07758d5def4.png-w331s)

因此成功将Constants.FORMAT_MESSAGES_PATTERN_DISABLE_LOOKUPS =
PropertiesUtil.getProperties().getBooleanProperty("log4j2.formatMsgNoLookups",
false);的结果设置为true，进而达到防御效果。

这里的系统环境变量设置为LOG4J_FORMAT_MSG_NO_LOOKUPS=true

其实只要满足正则匹配规则就可以，例如：

LOG4J_FORMAT_MSG_NO_LOOKUPS=true

LOG4J_log4j2_formatMsgNoLookups=true

LOG4J_formatMsgNoLookups=true

总结一下这三种方案只适用于
>=2.10版本，2.10以下的版本无效。FORMAT_MESSAGES_PATTERN_DISABLE_LOOKUPS不符合正则规则所以无效，而环境变量LOG4J_FORMAT_MSG_NO_LOOKUPS匹配成功，可以成功关闭lookup。

# **_总结：_**

总的来说这个漏洞影响面极广，同时利用难度很低，目前启明星辰ADLab确认受该漏洞影响的产品应用有：Ghidra、Apache
James、VMware多应用、Apache Solr、Apache Druid、Apache Flink、Apache
Struts2、Dubbo。其它存在该漏洞的系统或应用也会逐渐浮出水面。

注意：其中很多应用的利用代码已经被公布出来，希望引起大家足够重视。

# **_最终方案：_**

1.升级最新版本，目前最新版本为log4j-2.16.0，相比log4j-2.15.0修复了其它安全问题，在业务许可的情况下建议升级log4j-2.16.0-rc1。
2\. 弃用log4j 1.x版本，因为漏洞太多，并且无法更新升级。

**_临时方案：_**

1.对于Log4j 1.x版本

移除JMSAppender.class文件，命令为：

zip -q -d log4j-1.x.jar
org/apache/log4j/net/JMSAppender.class（使用该方案时需经过测试，避免对实际业务产生影响）

2.对于log4j2 >=2.10的版本(以下三种方案任选其一)：

1)添加log4j2.component.properties配置文件，增加如下内容为：

log4j2.formatMsgNoLookups=true

2)设置 jvm 参数: -Dlog4j2.formatMsgNoLookups=true

3)设置系统环境变量：LOG4J_FORMAT_MSG_NO_LOOKUPS=true

3.对于log4j2 <2.10的版本：

可以通过移除JndiLookup类的方式，命令为：

zip -q -d log4j-core-2.x.jar
org/apache/logging/log4j/core/lookup/JndiLookup.class

# **_参考链接_**

https://www.cnvd.org.cn/webinfo/show/7116

https://github.com/apache/logging-log4j2/releases/tag/log4j-2.16.0-rc1

https://gist.github.com/SwitHak/b66db3a06c2955a9cb71a8718970c592

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1787/>

