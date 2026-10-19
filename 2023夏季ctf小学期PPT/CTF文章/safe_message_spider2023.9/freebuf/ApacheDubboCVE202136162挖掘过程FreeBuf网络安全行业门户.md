## **01 漏洞背景**

发现该漏洞的起因是在分析 CVE-2021-30181 的脚本注入补丁的时候，意外发现了几个已被修复的 yaml
反序列化漏洞，还以为是未公开的Nday，查询后发现其实对应的是 CVE-2021-30180 漏洞的修复代码。通过查看补丁可以知道，Router
模块中所有yaml.load的调用中都使用了SafeConstructor白名单过滤，无法正常利用。

“关于本文中出现的 SnakeYaml 反序列化相关知识，可以参考公众号之前发送的推文——[《Java
SnakeYaml反序列化分析》](http://mp.weixin.qq.com/s?__biz=MzkyMTI0NjA3OA==&mid=2247484516&idx=1&sn=937b5f5cb95b8b302a07289886348bf1&chksm=c187c475f6f04d633f73cce941faf610067854fcdadda381e3bf6ea5ce34788b1b43a17f929c&scene=21#wechat_redirect)”。

![1649992906_6258e4caa0ed5214712f1.png!small?1649992909028](https://image.3001.net/images/20220415/1649992906_6258e4caa0ed5214712f1.png!small?1649992909028)![1649992914_6258e4d2bf8a321eff10b.png!small?1649992918403](https://image.3001.net/images/20220415/1649992914_6258e4d2bf8a321eff10b.png!small?1649992918403)

在代码中搜索yaml.load的调用，发现还有另外一个模块存在调用，并且没有使用SafeConstructor等修复措施，漏洞代码位置如下所示：

    
    
    public class MigrationRule {private static final String DUBBO_SERVICEDISCOVERY_MIGRATION_KEY = "dubbo.application.service-discovery.migration";public static final String DUBBO_SERVICEDISCOVERY_MIGRATION_GROUP = "MIGRATION";public static final String RULE_KEY = ApplicationModel.getName() + ".migration";private static DynamicConfiguration configuration = null;private String key;private MigrationStep step;...public static MigrationRule parse(String rawRule) {if (null == configuration) {return getMigrationRule((String)null);} else if (!StringUtils.isBlank(rawRule) && !"INIT".equals(rawRule)) {Constructor constructor = new Constructor(MigrationRule.class);Yaml yaml = new Yaml(constructor);return (MigrationRule)yaml.load(rawRule);} else {String step = (String)configuration.getInternalProperty("dubbo.application.service-discovery.migration");return getMigrationRule(step);}}...}

因此CVE-2021-30180的 PoC 也是可以在这里进行利用的，具体的反序列化利用链 Github 安全实验室已公布，感兴趣的同学可以自行参照其改造
CVE-2021-36162 漏洞的利用链。

##  **02 漏洞触发**

有了 yaml 反序列化利用链，接下来就是看看如何触发这个漏洞。参照之前的漏洞触发方式，需要通过在 ZooKeeper（下文简写为 ZK）
上增加节点存入恶意数据来完成触发，因此有两个问题需要解决：

> 1\. 在 ZK 哪个节点中添加恶意 yaml 数据 ？
>
> 2\. 如何让消费者读取并解析这个 yaml 数据 ？

 **问题一**

通过搜索 Migation 功能可以找到下面的文档，Dubbo 利用该功能来控制消费者执行不同的选址策略，根据内容可以大致确定可以通过全局的配置中心 ZK
来控制恶意的数据。

![1649992949_6258e4f579c6822d051cf.png!small?1649992952920](https://image.3001.net/images/20220415/1649992949_6258e4f579c6822d051cf.png!small?1649992952920)

正常的运行消费者和服务端并进行抓包，可以发现其中包含与 migration 相关的 ZK Path，尝试在其中创建相关节点，并在下列路径中插入任意数据：

![1649992957_6258e4fd2fcc37f3725af.png!small?1649992958650](https://image.3001.net/images/20220415/1649992957_6258e4fd2fcc37f3725af.png!small?1649992958650)

 **问题二**

完成任意数据的插入以后，再次运行消费者可以发现有如下 **解析异常的报错信息** ，证明插入的数据已经生效，成功进入到了漏洞代码当中。

![1649992968_6258e5081b38047244c48.png!small?1649992969760](https://image.3001.net/images/20220415/1649992968_6258e5081b38047244c48.png!small?1649992969760)

尝试将构造好的 PoC 插入到上述的路径当中，这里会发现由于 PoC 中有很多的空格、特殊符号之类的字符存在，直接通过 ZKCli.sh 插入 PoC
会出现各种问题，导致漏洞无法正常触发，因此需要通过 Java 调用第三方包的方式来向 ZK 中添加数据，具体代码如下所示：

• 使用下列代码插入恶意 Yaml 数据

    
    
    // 在看到 github 官方插入代码前自行实现的插入逻辑public class RegisterYaml {public static void main(String[] args) throws Exception {String path = "/dubbo/config/MIGRATION/consumer-of-helloworld-app.migration";String poc = "...";RetryPolicy retryPolicy = new ExponentialBackoffRetry(1000,3);CuratorFramework client = CuratorFrameworkFactory.newClient("127.0.0.1:2181", retryPolicy);client.start();Stat stat = client.checkExists().forPath(path);if (stat != null) {client.delete().forPath(path);}client.create().forPath(path, poc.getBytes());}}

准备好漏洞触发所需的 SPI 配置文件，以及待执行的 Class 字节码文件即可，具体的文件目录结构如下所示：

    
    
    ├── META-INF│   └── services│       └── javax.script.ScriptEngineFactory└── cc└── m01n└── SnakeYaml└── AwesomeScriptEngineFactory.class

在 META-INF 同级目录下使用 Python 启动 HTTP Server。

• python3 -m http.server 8000

先启动服务端代码，再运行消费者代码，即可触发漏洞：

![1649993058_6258e562e93d68aeeff06.png!small?1649993060762](https://image.3001.net/images/20220415/1649993058_6258e562e93d68aeeff06.png!small?1649993060762)![1649993066_6258e56a40b553f9e1629.png!small?1649993068623](https://image.3001.net/images/20220415/1649993066_6258e56a40b553f9e1629.png!small?1649993068623)

##  **03 漏洞分析**

在MigrationRuleListener 类中打下断点，其中会调用 this.configuration.getConfig 从 ZK 中获取 yaml
数据到rawRule属性中，可以看到取出来的就是我们写入的恶意 yaml 数据。

![1649993081_6258e5797f7d4a9141ce3.png!small?1649993083568](https://image.3001.net/images/20220415/1649993081_6258e5797f7d4a9141ce3.png!small?1649993083568)

继续跟进发现MigrationRuleListener实例是通过自定义的 SPI ExtensionLoader#createExtension 创建完成。

![1649993089_6258e58188c3902dfb023.png!small?1649993091407](https://image.3001.net/images/20220415/1649993089_6258e58188c3902dfb023.png!small?1649993091407)

后面会对MigrationRuleListener实例调用onRefer方法，触发到后续的 yaml 数据解析操作。

进去断点跟进可以看到，rawRule中的 yaml 数据会被传入到 yaml.load 方法中，导致反序列化漏洞。

![1649993096_6258e588002972bef7bc9.png!small?1649993097679](https://image.3001.net/images/20220415/1649993096_6258e588002972bef7bc9.png!small?1649993097679)

##  **04 漏洞修复**

该漏洞在 2.7.13 版本完成了修复，修复思路 CVE-2021-30180
方式一致，采用了SafeConstructor进行修复，具体修复补丁如下所示：

https://github.com/apache/dubbo/commit/bfa4b3bb6660d404c0715f54f8743dda45b46909

![1649993106_6258e5925c86d831f932d.png!small?1649993109426](https://image.3001.net/images/20220415/1649993106_6258e5925c86d831f932d.png!small?1649993109426)

