**2020年3月9日，Apache官方修复了一处由奇安信云影实验室maoge发现并提交的远程代码执行漏洞CVE-2020-1947。成功利用此漏洞，可以执行任意代码，完全控制目标主机。目前，该漏洞的利用POC已被公开。**  

Apache ShardingSphere是一套开源的分布式数据库中间件解决方案组成的生态圈，它由Sharding-JDBC、Sharding-Proxy和Sharding-Sidecar（计划中）这3款相互独立的产品组成。
它们均提供标准化的数据分片、分布式事务和数据库治理功能，可适用于如Java同构、异构语言、云原生等各种多样化的应用场景。ShardingSphere在解析snakeyaml的时候没有对其进行校验，当存在配置中心，用户提交恶意代码的时候，依然会对此进行解析并反序列化，从而导致恶意代码被执行。此漏洞影响sharding-jdbc,sharding-proxy,sharding-ui等。

##  **0** **x01** **漏洞验证**

###  一．环境搭建

1.官网下载4.0.0 版本sharding-ui。下载后进入bin目录启动sharding-ui。

使用localhost:8088 admin/admin (默认)进入配置页面。

###  二．复现

1、首先进入registry center添加一个注册中心。配置如下。

![](https://image.3001.net/images/20200311/1583905187_5e6879a3bab98.png!small)

2、进入rule config 新增一条规则，填入payload，点击commit即可执行命令。

![](https://image.3001.net/images/20200311/1583905220_5e6879c47f070.png!small)

通过实例化特意的snakeyaml，就可以触发漏洞。

##  **0** **x02** **漏洞** **分析**

### 1．snakeyaml 语法

!!+class 代表实例化一个类。我们可以dump出来看一下。

![](https://image.3001.net/images/20200311/1583905361_5e687a514f1fc.png!small)

刚好我们有ScriptEngineManager类可以接受一个classloader参数，URLClassLoader刚好满足要求来动态加载一个jar。可以通过snakeyaml的语法实例化出payload。

远程加载外置服务器的jar包，其中jar包代码包含如下方法：

    
    
    public class AwesomeScriptEngineFactory implements ScriptEngineFactory {
    
        public AwesomeScriptEngineFactory() {
    
        try {
    
        Runtime.getRuntime().exec("open /System/Applications/Calculator.app");
    
        } catch (IOException e) {
    
        e.printStackTrace();
    
        }
    
        }
    
        ……  
    }

编译为jar后放置在http服务器。

###  2\. AwesomeScriptEngineFactory 分析

对于上面的AwesomeScriptEngineFactory
类，为什么需要继承ScriptEngineFactory。通过调试可以知道：在此处需要为ScriptEngineFactory类型。命令执行放在构造函数里面，当初始化的时候既会调用。

![](https://image.3001.net/images/20200311/1583905422_5e687a8ed48db.png!small)

###  3\. 漏洞成因

其本质原因是开发者在加载yaml的时候直接unmarshal。没有考虑恶意加载的情况。

![](https://image.3001.net/images/20200311/1583905458_5e687ab2920e6.png!small)

直接通过new Yaml().load()从而导致反序列恶意类。

![](https://image.3001.net/images/20200311/1583905598_5e687b3e909db.png!small)4.0.1版本已经对此修复。对比新的补丁文件发现已经新增ClassFilterConstructor来对此进行过滤。

![](https://image.3001.net/images/20200311/1583905635_5e687b63dd5ab.png!small)

![](https://image.3001.net/images/20200311/1583905681_5e687b917ce4a.png!small)

搜索unmarshal的地方非常多。对于acceptClasses做了很强的限制。

![](https://image.3001.net/images/20200311/1583905743_5e687bcfa4568.png!small)

##  **0** **x03** **修复** **方案**

目前，Apache官方已发布新的版本4.0.1，请尽快升级到官方最新版本。

> <https://github.com/apache/incubator-shardingsphere/releases>

***本文作者： 云影实验室，转载请注明来自FreeBuf.COM**  

