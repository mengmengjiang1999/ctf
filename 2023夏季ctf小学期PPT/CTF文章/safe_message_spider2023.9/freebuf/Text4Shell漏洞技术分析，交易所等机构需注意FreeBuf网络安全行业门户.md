![](https://image.3001.net/images/20221019/1666179935_634fe35fea365319ca948.png!small)

### CVE编号

CVE-2022-42889

### 描述

Apache Commons
Text支持执行变量插值，标准格式是“${prefix:name}”，其中“prefix”用于定位org.apache.commons.text.lookup.StringLookup的实例。从1.5版到1.9版，默认lookup实例集如：script使用JVM
脚本执行引擎javax.script执行表达式、 dns用于解析dns记录、url用于发起任意http请求。

如果使用了不受信任的配置值，则受影响的应用程序容易受到远程代码执行，该漏洞NVD评分为9.8。

Apache Commons
Text作为Java语言的基础组件，其安全性需要各Web3项目方提高重视，及时关注各种Web3基础架构的安全漏洞并及时打好补丁，以避免潜在的安全风险和数字资产损失。我们将及时挖掘，追踪各种web3上的安全风险，以及提供领先的安全解决方案，确保web3世界链上，链下安全无虞。

受影响版本

`>=1.5 <=1.9`

### 分析

阅读官方1.9文档时，看到以下内容

![](https://image.3001.net/images/20221019/1666180006_634fe3a624ac3459df8b9.png!small)

通过script插值执行javascript运算，得到结果:

![](https://image.3001.net/images/20221019/1666180039_634fe3c75fd8135e47938.png!small)

根据漏洞描述script使用 JVM
脚本执行引擎（javax.script），猜测StringSubstitutor.replace方法处理script插值时可能执行任意java代码。

构造payload：

    
    
    ${Script:javascript:java.lang.Runtime.getRuntime().exec(\"open -a calculator\");}"

![](https://image.3001.net/images/20221019/1666180065_634fe3e1d9a97f8fc985b.png!small)

分析入口StringSubstitutor.replace，调用了substitute方法处理传入的字符串

![](https://image.3001.net/images/20221019/1666180097_634fe40190bc50c97455a.png!small)

进行处理${}字符，取出再进行解析，跟入resolveVariable方法

![](https://image.3001.net/images/20221019/1666180167_634fe447dd8caa614d6c5.png!small)

继续跟进StringLookup对象的lookup方法

![](https://image.3001.net/images/20221019/1666180223_634fe47fb469ecc61bca5.png!small)

在stringLookupMap初始化了其他插值，插值对应不同lookup实例

![](https://image.3001.net/images/20221019/1666180246_634fe4968118420d8234f.png!small)

当前传入是script，lookup实例对应ScriptStringLookup类的lookup方法

![](https://image.3001.net/images/20221019/1666180276_634fe4b4617fc5bb90686.png!small)

在该方法中，最终调用scriptEngine.eval触发漏洞。

![](https://image.3001.net/images/20221019/1666180322_634fe4e2770e16827716d.png!small)

调用栈

![图片](https://image.3001.net/images/20200701/1593550745.png!small)

### 修复

在1.10.0版本中stringLookupMap集合初始化时不再有script，lookup为null时，既没有找到对应实例。

![](https://image.3001.net/images/20221019/1666180383_634fe51f0cab433ded9d8.png!small)

## 其他插值的利用

### 1.任意文件读取

    
    
    ${file:UTF-8:/etc/passwd}

此时为lookup实例为FileStringLookup类

![](https://image.3001.net/images/20221019/1666180426_634fe54aca31cb910edf0.png!small)

lookup方法读取文件返回

![](https://image.3001.net/images/20221019/1666180456_634fe56828368579391b6.png!small)

结果

![](https://image.3001.net/images/20221019/1666180482_634fe582562b22a4bcdc1.png!small)

### 2\. DNS探测

    
    
    ${dns:127.0.0.1|test.xxx.xxx}

用于无损检测

![](https://image.3001.net/images/20221019/1666180503_634fe59769208dae096e5.png!small)

### 3\. HTTP 请求

可用于ssrf探测端口

    
    
    ${url:UTF-8:http://127.0.0.1:2121}﻿

![1666184085_634ff39506565ff322c29.png!small?1666184086554](https://image.3001.net/images/20221019/1666184085_634ff39506565ff322c29.png!small?1666184086554)

### 总结

该漏洞payload看起来类似于log4shell，很容易被攻击者利用，有些人已经开始将其称为“Text4Shell”或“Act4Shell”。

建议各Web3项目方提高重视，及时升级到 Apache Commons Text
1.10.0，默认情况下禁用有问题的插值器，以避免潜在的安全风险和数字资产损失。如有任何疑问或技术交流，欢迎联系我们
operation@numencyber.com。

![](https://image.3001.net/images/20221019/1666180558_634fe5ce0425d6a823a7b.png!small)

  

[ **Numen 导航**](https://numencyber.com/)

 **Numen 官网**  
https://numencyber.com/  
**GitHub**  
https://github.com/NumenCyber  
 **Twitter**  
https://twitter.com/@numencyber  
 **Medium**  
https://medium.com/@numencyberlabs  
 **LinkedIn**

https://www.linkedin.com/company/numencyber/

