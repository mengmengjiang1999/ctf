**作者：xxhzz@星阑科技PortalLab  
原文链接：<https://mp.weixin.qq.com/s/5B8MjKNB9UrsV6D-dKwTng>**

# **前言**

最近一直在对刚研发出来的自动化Web/API漏洞Fuzz的命令行扫描工具进行维护更新（工具地址：<https://github.com/StarCrossPortal/scalpel>），目前扫描工具已更新至第三个版本，新增了5条2022年CVE漏洞POC，修复了例如Content-Type和body类型不一致等问题。最新版本测试稳定，满足Web/API的漏洞Fuzz和多场景的漏洞检测，欢迎大家试用。

在维护更新扫描器POC库时，笔者看到了这个被称为“Textshell”的CVE漏洞，决定学习分析一波。

# **项目介绍**

Apache Commons Text 是一个低级库，用于执行各种文本操作，例如转义、计算字符串差异以及用通过插值器查找的值替换文本中的占位符。

# **漏洞描述**

2022年10月13号，官方发布了Apache Commons Text的漏洞通告，漏洞编号：CVE-2022-42889。Apache Commons
Text
执行变量插值，允许动态评估和扩展属性。插值的标准格式是“${prefix:name}”，其中“prefix”用于定位执行插值的。org.apache.commons.text.lookup.StringLookup
的实例。从 1.5 版到 1.9 版，攻击者可构造恶意文本，使得Apache Commons Text 在解析时执行任意恶意代码。

![图片](https://images.seebug.org/content/images/2022/11/23/1669189453000-1cxtys.png-w331s)

# **利用范围**

1.5 <= Apache Commons Text <= 1.9

# **漏洞分析**

## **环境搭建**

IDEA 通过Maven导入依赖

pom.xml如下：

    
    
    <dependencies>
        <dependency>
            <groupId>org.apache.commons</groupId>
            <artifactId>commons-configuration2</artifactId>
            <version>2.7</version>
        </dependency>
        <dependency>
            <groupId>org.apache.commons</groupId>
            <artifactId>commons-text</artifactId>
            <version>1.9</version>
        </dependency>
        <dependency>
            <groupId>org.apache.commons</groupId>
            <artifactId>commons-lang3</artifactId>
            <version>3.12.0</version>
        </dependency>
    </dependencies>

测试代码：

    
    
    package org.text;
    
    import org.apache.commons.text.StringSubstitutor;
    
    public class Main {
        public static void main(String[] args) {
    
            StringSubstitutor interpolator = StringSubstitutor.createInterpolator();
    //        String payload = interpolator.replace("${script:js:new java.lang.ProcessBuilder(\"calc\").start()}");
            String payload = "${script:js:new java.lang.ProcessBuilder(\"calc\").start()}";
            interpolator.replace(payload);
        }
    }

JDK版本1.8

## **动态分析**

在代码分析之前，我们先看看官方用户手册（<https://commons.apache.org/proper/commons-text/userguide.html>）中的内容。

![图片](https://images.seebug.org/content/images/2022/11/23/1669189453000-2ngomj.png-w331s)

这里演示了使用默认查找StringSubstitutor来构造复杂字符串的用法，而漏洞描述中的关键所在就是执行变量插值，其标准格式是${prefix:name}。

参考下 StringLookupFactory的文档（<http://commons.apache.org/proper/commons-text/apidocs/org/apache/commons/text/lookup/StringLookupFactory.html>）

![图片](https://images.seebug.org/content/images/2022/11/23/1669189454000-3nmoon.png-w331s)

自从1.5版本之后，可以满足script类型的字符串查找，但是并不是默认包括的。

将代码定位到

org.apache.commons.text.lookup.InterpolatorStringLookup#lookup

![图片](https://images.seebug.org/content/images/2022/11/23/1669189454000-4dhmel.png-w331s)

这里lookup方法会提取”:“后的部分作为 prefix 值，然后根据 stringLookupMap 提取其对应的 lookup 实例化对象。

到org.apache.commons.text.lookup.ScriptStringLookup#lookup中。

![图片](https://images.seebug.org/content/images/2022/11/23/1669189455000-5bhnos.png-w331s)

调用ScriptEngineManager执行代码。

了解了漏洞后半部分，打下断点，动态调试一下，看看如何调用lookup方法。

![图片](https://images.seebug.org/content/images/2022/11/23/1669189456000-6gskye.png-w331s)

org.apache.commons.text.StringSubstitutor#createInterpolator

![图片](https://images.seebug.org/content/images/2022/11/23/1669189456000-7uuwhr.png-w331s)

这里就是实例化了StringSubstitutor 并向其中传入
StringLookupFactory.INSTANCE.interpolatorStringLookup()

org.apache.commons.text.StringSubstitutor#replace

![图片](https://images.seebug.org/content/images/2022/11/23/1669189457000-8cixvp.png-w331s)

对参数转换类型，然后传入 substitute 处理，后续将经过一系列判断检查。

![图片](https://images.seebug.org/content/images/2022/11/23/1669189457000-9gpkxg.png-w331s)

最后传入resolveVariable

org.apache.commons.text.StringSubstitutor#resolveVariable

![图片](https://images.seebug.org/content/images/2022/11/23/1669189458000-10ipxls.png-w331s)

![图片](https://images.seebug.org/content/images/2022/11/23/1669189458000-11abfsi.png-w331s)

在getStringLookup的值之后，就会直接到org.apache.commons.text.lookup.InterpolatorStringLookup中调用lookup方法。

![图片](https://images.seebug.org/content/images/2022/11/23/1669189458000-12kxbtd.png-w331s)

到这里，正如开头所分析的那样lookup方法会提取”:“后的部分作为 prefix 值，然后根据 stringLookupMap 提取其对应的 lookup
实例化对象，最后通过调用ScriptEngineManager执行代码。

# **漏洞复现**

![图片](https://images.seebug.org/content/images/2022/11/23/1669189458000-13kqbtn.png-w331s)

当然，网上已经有很多大佬对这个进行了分析，此漏洞与Log4Shell (CVE-2021-44228)其实是不同的，因为在 Log4Shell
中，可以从日志消息正文中进行字符串插值，该正文通常包含不受信任的输入。在 Apache Common Text issue
中，相关方法明确用于执行字符串插值并明确记录在案，因此应用程序不太可能在没有适当验证的情况下无意中传递不受信任的输入。

# **漏洞检测工具**

**工具地址：**<https://github.com/StarCrossPortal/scalpel>

**已更新：**

目前扫描工具已更新至第三个版本，新增对CVE-2022-0885、CVE-2022-1054、CVE-2022-1392、CVE-2022-21500、CVE-2022-23854漏洞的检测，已内置100+漏洞POC，修复了例如Content-Type和body类型不一致等问题。最新版本测试稳定，满足Web/API的漏洞Fuzz和多场景的漏洞检测。

**持续更新：**

漏洞POC、扫描工具漏洞检测优化（检测逻辑，满足对需要连续数据包关联操作漏洞场景的检测）

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2025/>

