# **源码链接**

(修改前的源码，因为feihong师傅的仓库已经不在了，这里使用的是Jeromeyoung师傅的源码进行改造)[
**https://github.com/Jeromeyoung/JNDIExploit-1**](https://sec-in.com/outLinkPage/?target=https://github.com/Jeromeyoung/JNDIExploit-1)

#  **0x00 JNDI注入工具代码结构分析**

 **controllers模块：负责LDAP请求的处理**

![](https://image.3001.net/images/20221117/1668662095_6375c34f197995f0a752b.png!small)

 **enum模块：负责存储各种模板类型名称，如：反序列化的Gadget、内存马的类型**

![](https://image.3001.net/images/20221117/1668662096_6375c3501ff503bb3ec6a.png!small)

 **异常模块：负责处理可能抛出的异常**

![](https://image.3001.net/images/20221117/1668662097_6375c3511015ea608aa97.png!small)

 **反序列化模块：各种反序列化链的处理**

![](https://image.3001.net/images/20221117/1668662097_6375c35183a8586477763.png!small)

 **模板模块：命令执行、回显、DNS、内存马模板**

![](https://image.3001.net/images/20221117/1668662098_6375c352723cdd71c2b09.png!small)

 **工具类模块：主要是为了方便而编写的一些工具类**

![](https://image.3001.net/images/20221117/1668662099_6375c353ad7f888645860.png!small)

 **协议服务及启动模块：负责LDAP、HTTP协议的具体实现**

![](https://image.3001.net/images/20221117/1668662100_6375c35430233d2216ef4.png!small)

 **下面先对启动及协议服务模块进行说明**

![](https://image.3001.net/images/20221117/1668662100_6375c3549ea03aefa0ec2.png!small)

**com.feihong.ldap.Starter类为整个工具的启动入口，从命令行接收参数传参到com.feihong.ldap.utils.Config类**

![](https://image.3001.net/images/20221117/1668662101_6375c355469f56d3a17b7.png!small)

**Config类中的@Parameter注解为参数的说明及代表的意思，类似于py中的argparse，命令接收到参数，分别赋值给Config类的几个私有变量。**

 **然后在之后的HTTPServer与LDAPServer中得到应用**

![](https://image.3001.net/images/20221117/1668662102_6375c35686c4b5153ceae.png!small)

 **关于LDAP服务端的编写和Demo可以参考以下链接：**[
**https://www.freebuf.com/vuls/253545.html**](https://sec-in.com/outLinkPage/?target=https://www.freebuf.com/vuls/253545.html)
**，HTTPServer则是正常的Java Demo编写即可**

![](https://image.3001.net/images/20221117/1668662103_6375c357065eddaaee5c1.png!small)

##  **第一部分注解的应用**

**在JNDIEXP中，作者为了可以反射一种类型的类，Controller类，这里的类起到了寻找特定类的作用，而且每个注解类都给定了uri属性**![](https://image.3001.net/images/20221117/1668662103_6375c35797c964dd6a720.png!small)

 **在LDAPServer.start()之前，会先通过new
Reflections(this.getClass().getPackage().getName())的方法获取到com.feihong.ldap包下面所有LdapMapping的类，之后将其以键值对（TreeMap
<String,
LdapController>）放入到Map中，以便于后续调用**![](https://image.3001.net/images/20221117/1668662104_6375c35812f66f378255d.png!small)

 **比如com.feihong.ldap.controllers.BasicController类，在Map中的存储格式就是(basic= >Object
BasicController)**![](https://image.3001.net/images/20221117/1668662104_6375c3587d04289527169.png!small)

**根据发送来的LDAP请求去决定调用哪个类，具体通过com.feihong.ldap.processSearchResult**![](https://image.3001.net/images/20221117/1668662105_6375c3590d6b144d2455d.png!small)

**根据工具运行的实际效果，如果我们的LDAP请求为ldap://192.168.85.1:1389/Basic/123**![](https://image.3001.net/images/20221117/1668662105_6375c3597d48aa24fa197.png!small)

 **那么DN为Basic/123，首先根据DN中的开头字符串决定是哪个Controller来处理当前的LDAP的请求**

##  **第二部分服务端动态调用类**

**在LDAP调用LdapController接口实现类之后（以BasicController为例），会先调用process方法，以/为标志分割，获取到相应的模块名称，比如ldap://0.0.0.0:1389/Basic/Command/whoami，那么第一部分Basic用来指定是BasicController，Command指定执行BasicController下的命令执行模块**![](https://image.3001.net/images/20221117/1668662106_6375c35a91e2abc38c9b2.png!small)

![](https://image.3001.net/images/20221117/1668662107_6375c35b9182bd94359e1.png!small)

**如果是命令执行模块**![](https://image.3001.net/images/20221117/1668662108_6375c35c1937cf8c70e57.png!small)

**通过com.feihong.ldap.utils.Util的getCmdFromBase方法获取到执行命令的内容，如果是base编码的，进行base64解码后返回内容**![](https://image.3001.net/images/20221117/1668662108_6375c35c9a906e7725b8b.png!small)

**将其赋值给params，之后再调用BasicController的sendResult方法，如果是command模块，初始化该模块，通过asm码的方法，这里为了避免出现类名重复的情况，使用随机字符命令类名**![](https://image.3001.net/images/20221117/1668662109_6375c35d143894f849842.png!small)

![](https://image.3001.net/images/20221117/1668662109_6375c35d7df6dee1261b9.png!small)![](https://image.3001.net/images/20221117/1668662110_6375c35e0912426bd5ef9.png!small)

![](https://image.3001.net/images/20221117/1668662110_6375c35ebf9bafe46126a.png!small)

![](https://image.3001.net/images/20221117/1668662111_6375c35fb557be33aba93.png!small)
**之后命令执行模块调用cache方法**![](https://image.3001.net/images/20221117/1668662112_6375c360336a15c900771.png!small)![](https://image.3001.net/images/20221117/1668662112_6375c36098fb2f29877e5.png!small)

![](https://image.3001.net/images/20221117/1668662113_6375c36117e32f6acc9d8.png!small)

**将其存储在map中，之后开始进行LDAP的步骤**![](https://image.3001.net/images/20221117/1668662113_6375c36185c60c19a7407.png!small)

 **首先LDAP设定好**

 **javaClassName：记录序列化对象的类名，这样应用程序就可以确定类信息，而不必首先反序列化**

 **javaClassNames：关于序列化对象的附加类信息。**

 **javaCodebase：实例化工厂所需的类定义的位置（HTTP地址）**

 **javaFactory：用于存储对象工厂的完全限定类的可选属性（即类名）**

 **一张图说明LDAP请求的过程**

![wKg0C2I4Qs6AAM4QAABoz1qOh2I020.png](https://image.3001.net/images/20221117/1668662114_6375c36202e42d594570d.png!small)

**接下来看HTTPServer如何接收HTTP请求并返回**![](https://image.3001.net/images/20221117/1668662114_6375c362c6822a8b25aba.png!small)

 **当HTTPServer接收到请求之后，将Cache类中map存储的类写入到响应中，这样避免了class文件落地的情况。**

#  **0x01 去除server console内容**

 **在这个JNDI的注入工具中，会在注入内存马的时候，使用系统输出语句，在控制台打印出东西，无关紧要的东西，直接去掉就好。**

![](https://image.3001.net/images/20221117/1668662115_6375c363e5416a1e6c05a.png!small)

#  **0x02 冰蝎3.11内存马注入**

 **改造前的filter类，获取session是通过ServletRequest的方式获取的**

![](https://image.3001.net/images/20221117/1668662116_6375c3647312a82cbfbf5.png!small)

**改造之后的filter类，不再使用自写的classLoader而是直接使用URLClassLoader，同理对其他的组件也进行类似的改造，如：spring的Interceptor，weblogic和jboss的filter**

![](https://image.3001.net/images/20221117/1668662116_6375c364e821ea5675294.png!small)

 **所有回显使用的是header头的WWW-Authenticate字段，而非cmd**

![](https://image.3001.net/images/20221117/1668662117_6375c365768ba014d0935.png!small)

#  **0x03 JDK版本匹配及tomcat版本兼容解决**

 **利用JDK向下兼容的特性，这里使用JDK6编译filter class。**

**tomcat版本兼容，根据先知不久之前提出的，tomcat6-9的通用StandardContext获取方法，获取到StandardContext，接下来的问题就是解决tomcat版本识别与不同版本间filter注入的问题。**

**tomcat8以下版本FilterDef、FilterMap都在org.apache.catalina.deploy包里，tomcat8以上包括8都在org.apache.tomcat.util.descriptor.web里。**

 **2.识别版本之后，进行不同版本间的filter注入**

 **实现逻辑大概如下：**

**对各个版本的filter内存马全部转为字节码Base64的编码格式，通过loadClass的办法，根据版本注入到内存中。（class一律使用JDK1.6编译）**

 **为了避免相关类加载不到的问题，这里统一使用反射写所有的filter注入步骤。**

 **tomcat6789的StandardContext先知上已经给出了解决方案：**

[ **https://xz.aliyun.com/t/9914**](https://sec-in.com/outLinkPage/?target=https://xz.aliyun.com/t/9914)

 **对tomcat特定类进行筛选，来决定FilterDef和FilterMap类加载的使用，最后形成的Demo如下：**

![](https://image.3001.net/images/20221117/1668662118_6375c36644ea94008292a.png!small)

![](https://image.3001.net/images/20221117/1668662119_6375c3670b4cf568265c0.png!small)

![](https://image.3001.net/images/20221117/1668662119_6375c367f1c8ef738976b.png!small)

![](https://image.3001.net/images/20221117/1668662120_6375c368723173d6c8bf1.png!small)

 **getStand的源码如下：**

![](https://image.3001.net/images/20221117/1668662120_6375c368e28330fff0f18.png!small)

![](https://image.3001.net/images/20221117/1668662122_6375c36a0db0ec739645e.png!small)

![](https://image.3001.net/images/20221117/1668662122_6375c36add00bd65c2f34.png!small)

 **经测试，可用于常规的tomcat6、7（某凌）、8、9版本。**

 **当所有的tomcat版本都测试完毕之后，发现这个通用方法对某远并不适用，原因是致远这里的ServerPort会永远等于-1。**

 **解决方案是使用原版的feihong-jndi将TomcatMemShell2中的filter类替换为自定义的filter类即可。**

#  **0x04 spring memShell的改进**

**在一些版本的测试中，发现原版的JNDIExploit的spring并不适用于所有的spring框架场景，对此做出补充（借鉴自lz2y与microworld师傅的成果）**

 **以ruoyi cms后台的snake yaml为例，lz2y师傅这里已经说了具体的原因（**[
**https://xz.aliyun.com/t/10651**](https://sec-in.com/outLinkPage/?target=https://xz.aliyun.com/t/10651)
**），直接使用师傅的Demo就好，我这里使用的是Windows的环境，使用比较在Linux和Windows都通用的Demo获取的WebApplicationContext**

![](https://image.3001.net/images/20221117/1668662123_6375c36b6cd6175e26127.png!small)

 **使用com.ruoyi.common.utils.spring.SpringUtils在windows
ruoyi4.6.0的环境中没有成功（POC使用的是com.sun.rowset.JdbcRowSetImpl）**

![](https://image.3001.net/images/20221117/1668662124_6375c36c074bd5dcc6961.png!small)

 **使用com.ruoyi.common.utils.spring.SpringUtils在windows
ruoyi4.6.0的环境中成功（POC使用的是javax.script.ScriptEngineManager）**

 **剩下的步骤直接注入内存马即可，实现Demo如下：**

![](https://image.3001.net/images/20221117/1668662125_6375c36d18a8f2b19ee23.png!small)

![](https://image.3001.net/images/20221117/1668662126_6375c36e295e11073dad6.png!small)

![](https://image.3001.net/images/20221117/1668662126_6375c36e907682c6b1dc1.png!small)

![](https://image.3001.net/images/20221117/1668662127_6375c36f0c2d8f2748355.png!small)

![](https://image.3001.net/images/20221117/1668662127_6375c36f7a5b4c925cc8a.png!small)

 **将其添加到类的引用处，对于spring的框架添加新增类的引用，需要修改的是四个类：**

 **com.feihong.ldap.enumtypes.PayloadType**

![](https://image.3001.net/images/20221117/1668662128_6375c37095ca9fd000bb1.png!small)

 **com.feihong.ldap.utils.Cache**

![](https://image.3001.net/images/20221117/1668662129_6375c37181f2ce3ff12d6.png!small)

 **com.feihong.ldap.controllers.BasicController**

![](https://image.3001.net/images/20221117/1668662130_6375c37205fa0b9ee269c.png!small)

 **com.feihong.ldap.controllers.TomcatBypassController**

![](https://image.3001.net/images/20221117/1668662131_6375c3734c185647dfd52.png!small)

**修改Cache类是为了能够让恶意类能够在内存中加载，具体的原因已经在0.1中分析完毕，修改BasicController和TomcatBypassController是为了能在LDAP在JDK的高低版本中找到引用。**

#  **0x05 jetty memShell的改进**

 **对于jetty内存马的改进，主要是log4j对solr的影响，针对于实战的场景，参考Qu3een师傅的文章（**[
**https://tttang.com/archive/1386/**](https://sec-in.com/outLinkPage/?target=https://tttang.com/archive/1386/) **）**

 **实现的Demo如下，直接集成到JNDI注入工具中**

![](https://image.3001.net/images/20221117/1668662132_6375c3744bda920f5c6e7.png!small)

![](https://image.3001.net/images/20221117/1668662133_6375c375a5f47915905d5.png!small)

 **修改com.feihong.ldap.enumtypes.PayloadType**

![](https://image.3001.net/images/20221117/1668662135_6375c3771322a22ae5b8b.png!small)

 **修改com.feihong.ldap.utils.Cache**

![](https://image.3001.net/images/20221117/1668662135_6375c377dc80364f781c7.png!small)

 **修改com.feihong.ldap.controllers.BasicController**

![](https://image.3001.net/images/20221117/1668662136_6375c37861f0c601575ab.png!small)

#  **0x06 webSphere memShell的改进**

 **暂缺**

#  **0x07 增加resin中间件下的内存马注入**

 **基于pen4uin师傅的通用研究成果直接集成到JNDI注入工具中，原理不再赘述，参考pen4uin师傅的公众号即可，直接给出Demo**

![](https://image.3001.net/images/20221117/1668662137_6375c379299c8c3c16ed1.png!small)

![](https://image.3001.net/images/20221117/1668662138_6375c37a1df5b2edf9e8b.png!small)

 **同样的，修改com.feihong.ldap.enumtypes.PayloadType**

![](https://image.3001.net/images/20221117/1668662138_6375c37acf701019e5f1d.png!small)

 **修改com.feihong.ldap.utils.Cache**

![](https://image.3001.net/images/20221117/1668662139_6375c37b476590015ae37.png!small)

 **修改com.feihong.ldap.controllers.BasicController**

![](https://image.3001.net/images/20221117/1668662140_6375c37c5bcba209058d6.png!small)

![](https://image.3001.net/images/20221117/1668662141_6375c37d5ef107b6317b8.png!small)

#  **0x08 增加tomcatValue内存马**

 **在tomcat容器中，有些场景filter内存马并不如valve内存马，所以为了增加兼容性，这里增加valve内存马，实现的Demo大致如下：**

![](https://image.3001.net/images/20221117/1668662141_6375c37dd5e611dfd84c7.png!small)

![](https://image.3001.net/images/20221117/1668662142_6375c37e51a98ac2676d9.png!small)

![](https://image.3001.net/images/20221117/1668662143_6375c37f2104263ce800f.png!small)

![](https://image.3001.net/images/20221117/1668662144_6375c3804b3e9277e4180.png!small)

![](https://image.3001.net/images/20221117/1668662144_6375c380f1c7ea38956b6.png!small)

 **同样的修改配置文件，增加到BasicController、TomcatBypassController、Cache、Config中。**

#  **参考链接**

[ **https://landgrey.me/blog/19/**](https://sec-in.com/outLinkPage/?target=https://landgrey.me/blog/19/)

[ **https://github.com/Mr-xn/JNDIExploit-1**](https://sec-in.com/outLinkPage/?target=https://github.com/Mr-xn/JNDIExploit-1)

[ **https://tttang.com/archive/1386/**](https://sec-in.com/outLinkPage/?target=https://tttang.com/archive/1386/)

[ **https://mp.weixin.qq.com/s/5s9eyRpaP7WhVd2estwtKg**](https://sec-in.com/outLinkPage/?target=https://mp.weixin.qq.com/s/5s9eyRpaP7WhVd2estwtKg)

[ **https://github.com/lz2y/yaml-payload-for-ruoyi**](https://sec-in.com/outLinkPage/?target=https://github.com/lz2y/yaml-payload-for-ruoyi)

[ **https://xz.aliyun.com/t/10651**](https://sec-in.com/outLinkPage/?target=https://xz.aliyun.com/t/10651)

