## **漏洞描述**

7月6日，Apache官方发布安全公告，修复了一个存在于Apache Commons Configuration
组件的远程代码执行漏洞，漏洞编号：CVE-2022-33980，漏洞威胁等级：高危。恶意攻击者通过该漏洞，可在目标服务器上实现任意代码执行。

##  **相关介绍**

Apache Commons
Configuration是一个Java应用程序的配置管理工具，可以从properties或者xml文件中加载软件的配置信息，用来构建支撑软件运行的基础环境。在一些配置文件较多较复杂的情况下，使用该配置工具比较可以简化配置文件的解析和管理，提高开发效率和软件的可维护性。

##  **利用范围**

2.4 <= Apache Commons Configuration <=2.7

##  **漏洞分析**

###  **前置知识**

什么是变量插值？

通常我们用apach的configuration2库来管理配置文件(org.apache.commons:commons-configuration2),在commons-configuration2管理的配置文件中，配置变量的值可以引用变量。举个例子：${env:xxhzz}就指代环境变量xxhzz，在commons-configuration2中这种引用动态变量的方式就叫变量插值。

变量插值解析：在commons-configuration2中，负责对字符串中的变量进行解析的是org.apache.commons.configuration2.interpol.ConfigurationInterpolator类中的interpolate(Object)方法。

###  **漏洞原理**

![](https://image.3001.net/images/20220720/1658298499_62d7a083d5ef40e43c132.png!small)

从漏洞通告中，可以得知Apache Commons
Configuration执行变量插值，允许动态评估和扩展属性。插值的标准格式是“${prefix:name}”，其中“prefix”用于定位执行插值的org.apache.commons.configuration2.interpol.Lookup
实例。

从2.4版到2.7版，默认的Lookup实例集包括可能导致任意代码执行或与远程服务器联系的插值器。如公告中提到“script”
可使用JVM脚本执行引擎(javax.script)执行表达式，若使用了不受信任的配置值，在受影响的版本中使用插值默认值的应用程序就很可能受到远程代码执行的影响。

###  **环境搭建**

了解了漏洞原理后，为更好理解漏洞的形成，需构建一个调试的demo环境。

通过maven直接引入Apache Commons Configuration2.7。

![](https://image.3001.net/images/20220720/1658298542_62d7a0ae6dd5b5fe7dee2.png!small)

    
    
    <dependency>
        <groupId>org.apache.commons</groupId>
        <artifactId>commons-configuration2</artifactId>
        <version>2.7</version>
    </dependency>

接着构建一个触发漏洞的主类即可

![](https://image.3001.net/images/20220720/1658298573_62d7a0cd1c979cc19aff8.png!small)

###  **动态调式**

在对插值变量进行解析的地方打下断点。

org.apache.commons.configuration2.interpol.ConfigurationInterpolator#interpolate

![](https://image.3001.net/images/20220720/1658298608_62d7a0f0ed00d82c0c4f3.png!small)开启debug模式，在经过了前两个if判断之后，随后会进入resolveSingleVariable函数。

![](https://image.3001.net/images/20220720/1658298623_62d7a0ff151de830e30f7.png!small)在org.apache.commons.configuration2.interpol.ConfigurationInterpolator#resolveSingleVariable中首先跟一下extractVariableName函数。

![](https://image.3001.net/images/20220720/1658298643_62d7a1132a45958bdddb5.png!small)org.apache.commons.configuration2.interpol.ConfigurationInterpolator#extractVariableName的作用是提取变量字符串strValue。

![](https://image.3001.net/images/20220720/1658298662_62d7a1264f71da3a11bed.png!small)

随后进入org.apache.commons.configuration2.interpol.ConfigurationInterpolator#resolve函数中

通过index0f查找和判断条件，从变量字符串中分别获取到prefix和name。

![](https://image.3001.net/images/20220720/1658298678_62d7a136310ddfed0b79d.png!small)继续跟进会进入lookup函数。

![](https://image.3001.net/images/20220720/1658298696_62d7a1482fdf19944e60a.png!small)在分析lookup函数前先跟进下fetchLookupForPrefix函数。

![](https://image.3001.net/images/20220720/1658298710_62d7a1566bfb3005cc9b6.png!small)

fetchLookupForPrefix函数的作用是获取到stringLookup对象。

继续跟进，会进入commons-text-1.8.jar包中的org.apache.commons.text.lookup.ScriptStringLookup#lookup函数。

![](https://image.3001.net/images/20220720/1658298740_62d7a174bb04b31b76cba.png!small)在org.apache.commons.text.lookup.ScriptStringLookup#lookup函数中会再次对字符串进行分割，分别提取engineName和script。

![](https://image.3001.net/images/20220720/1658298754_62d7a182374e8626d78c4.png!small)接着会通过getEngineByName函数获取ScriptEngine（javax.script)。

![](https://image.3001.net/images/20220720/1658298769_62d7a19160b30dc2afa5d.png!small)

继续往下，出现eval函数。

而我们知道eval函数可计算某个字符串，并执行其中的的JavaScript 代码。

![](https://image.3001.net/images/20220720/1658298783_62d7a19fe7fa9e2b06c2c.png!small)  
继续往下将成功触发我们传入的payload，造成远程命令执行。

###  **漏洞复现**

![](https://image.3001.net/images/20220720/1658298810_62d7a1bab5ba75f813a84.png!small)
成功命令执行。

![](https://image.3001.net/images/20220720/1658298829_62d7a1cd57dc1df419421.png!small)

##  **修复建议**

目前官方已发布修复版本修复了该漏洞，请受影响的用户升级到 Apache Commons Configuration 2.8.0 版本。

https://commons.apache.org/proper/commons-configuration/download_configuration.cgi

##  **参考材料**

1.https://lists.apache.org/thread/tdf5n7j80lfxdhs2764vn0xmpfodm87s

2.https://cloud.tencent.com/developer/article/1650833

