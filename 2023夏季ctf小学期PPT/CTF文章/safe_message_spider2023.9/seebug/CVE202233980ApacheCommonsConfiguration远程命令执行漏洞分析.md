**作者：xxhzz@星阑科技PortalLab  
原文链接：<https://mp.weixin.qq.com/s/iAEDu3noxYvZ6xhxeN-reA>**

## **漏洞描述**

7月6日，Apache官方发布安全公告，修复了一个存在于Apache Commons Configuration
组件的远程代码执行漏洞，漏洞编号：CVE-2022-33980，漏洞威胁等级：高危。恶意攻击者通过该漏洞，可在目标服务器上实现任意代码执行。

## **相关介绍**

Apache Commons
Configuration是一个Java应用程序的配置管理工具，可以从properties或者xml文件中加载软件的配置信息，用来构建支撑软件运行的基础环境。在一些配置文件较多较复杂的情况下，使用该配置工具比较可以简化配置文件的解析和管理，提高开发效率和软件的可维护性。

## **利用范围**

2.4 <= Apache Commons Configuration <=2.7

## **漏洞分析**

### **前置知识**

什么是变量插值？

通常我们用apache的configuration2库来管理配置文件(org.apache.commons:commons-configuration2),在commons-configuration2管理的配置文件中，配置变量的值可以引用变量。举个例子：${env:xxhzz}就指代环境变量xxhzz，在commons-configuration2中这种引用动态变量的方式就叫变量插值。

变量插值解析：在commons-configuration2中，负责对字符串中的变量进行解析的是org.apache.commons.configuration2.interpol.ConfigurationInterpolator类中的interpolate(Object)方法。

### **漏洞原理**

![](https://images.seebug.org/content/images/2022/11/dacc7032-7fc1-4855-a019-91bf0395203c.png-w331s)

从漏洞通告中，可以得知Apache Commons
Configuration执行变量插值，允许动态评估和扩展属性。插值的标准格式是“${prefix:name}”，其中“prefix”用于定位执行插值的org.apache.commons.configuration2.interpol.Lookup
实例。

从2.4版到2.7版，默认的Lookup实例集包括可能导致任意代码执行或与远程服务器联系的插值器。如公告中提到“script”
可使用JVM脚本执行引擎(javax.script)执行表达式，若使用了不受信任的配置值，在受影响的版本中使用插值默认值的应用程序就很可能受到远程代码执行的影响。

### **环境搭建**

了解了漏洞原理后，为更好理解漏洞的形成，需构建一个调试的demo环境。

通过maven直接引入Apache Commons Configuration2.7。

![](https://images.seebug.org/content/images/2022/11/94fcbd74-7b16-4697-8ee3-fa148387720b.png-w331s)

    
    
    <dependency>
        <groupId>org.apache.commons</groupId>
        <artifactId>commons-configuration2</artifactId>
        <version>2.7</version>
    </dependency>

接着构建一个触发漏洞的主类即可

![](https://images.seebug.org/content/images/2022/11/abbba5ce-ed01-4741-aa95-eb03d808b929.png-w331s)

### **动态调式**

在对插值变量进行解析的地方打下断点。

org.apache.commons.configuration2.interpol.ConfigurationInterpolator#interpolate

![](https://images.seebug.org/content/images/2022/11/bb7429e6-ada3-49f6-a7f7-8f19ff12f36d.png-w331s)

开启debug模式，在经过了前两个if判断之后，随后会进入resolveSingleVariable函数。

![](https://images.seebug.org/content/images/2022/11/badbb377-b03a-496b-bf1b-79f10e42b24a.png-w331s)

在org.apache.commons.configuration2.interpol.ConfigurationInterpolator#resolveSingleVariable中首先跟一下extractVariableName函数。

![](https://images.seebug.org/content/images/2022/11/6b4382c5-c86e-4faf-9068-72083e58d57a.png-w331s)

org.apache.commons.configuration2.interpol.ConfigurationInterpolator#extractVariableName的作用是提取变量字符串strValue。

![](https://images.seebug.org/content/images/2022/11/50ca6fa1-60ac-4314-8c3b-2da7339191af.png-w331s)

随后进入org.apache.commons.configuration2.interpol.ConfigurationInterpolator#resolve函数中

通过index0f查找和判断条件，从变量字符串中分别获取到prefix和name。

![](https://images.seebug.org/content/images/2022/11/22ca8122-b569-4330-aa15-a68e0983cfec.png-w331s)

继续跟进会进入lookup函数。

![](https://images.seebug.org/content/images/2022/11/9558508a-e7a8-4539-b23f-0439873199d2.png-w331s)

在分析lookup函数前先跟进下fetchLookupForPrefix函数。

![](https://images.seebug.org/content/images/2022/11/55a5855e-48dc-4901-a799-fd16bc2abc4d.png-w331s)

fetchLookupForPrefix函数的作用是获取到stringLookup对象。

继续跟进，会进入commons-text-1.8.jar包中的org.apache.commons.text.lookup.ScriptStringLookup#lookup函数。

![](https://images.seebug.org/content/images/2022/11/4f609ac2-e1cd-43b0-8ad9-c13a25b7c139.png-w331s)

在org.apache.commons.text.lookup.ScriptStringLookup#lookup函数中会再次对字符串进行分割，分别提取engineName和script。

![](https://images.seebug.org/content/images/2022/11/ed55a300-87f3-4050-8eab-59beb92c0ffd.png-w331s)

接着会通过getEngineByName函数获取ScriptEngine（javax.script)。

![](https://images.seebug.org/content/images/2022/11/5324a654-c2fa-4f11-85e0-c0ea7aa099e2.png-w331s)

继续往下，出现eval函数。

而我们知道eval函数可计算某个字符串，并执行其中的的JavaScript 代码。

![](https://images.seebug.org/content/images/2022/11/4febfc5e-9bd5-4172-afc0-b75301b1fdbd.png-w331s)

继续往下将成功触发我们传入的payload，造成远程命令执行。

### **漏洞复现**

![](https://images.seebug.org/content/images/2022/11/2381cdae-0c54-47b8-98ab-24399eae868c.png-w331s)

成功命令执行。

![](https://images.seebug.org/content/images/2022/11/a5682335-bccb-414a-82ba-19605238c0af.png-w331s)

## **修复建议**

目前官方已发布修复版本修复了该漏洞，请受影响的用户升级到 Apache Commons Configuration 2.8.0 版本。

<https://commons.apache.org/proper/commons-configuration/download_configuration.cgi>

## **参考材料**

1.<https://lists.apache.org/thread/tdf5n7j80lfxdhs2764vn0xmpfodm87s>

2.<https://cloud.tencent.com/developer/article/1650833>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2001/>

