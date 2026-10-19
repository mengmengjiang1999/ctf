##  **fastjson组件** **介绍**

**fastjson是一个Java语言编写的高性能功能完善的JSON库。它采用一种“假定有序快速匹配”的算法，把JSON
Parse的性能提升到极致，是目前Java语言中最快的JSON库。fastjson接口简单易用，已经被广泛使用在缓存序列化、协议交互、Web输出、Android客户端等多种应用场景。**

##  **漏洞描述**

fastjson远程代码执行漏洞是由于使用com.ibatis.sqlmap.engine.transaction.jta.JtaTransactionConfig类，绕过了fastjson的黑名单而导致
。当服务端加载了存在受漏洞影响的 ibatis-sqlmap依赖，并且开启了fastjson的 autotype
时，远程攻击者可以通过构造的攻击代码触发远程代码执行漏洞 ，最终可以获取到服务器的控制权限。

##  **漏洞分析**

以fastjson1.2.62 + ibatis-sqlmap-2.3.4.726作为漏洞环境分析。传入构造好的payload，经过JSON类中的parse方法的解析入口，如下图：

![](https://image.3001.net/images/20200304/1583294058_5e5f266ae3484.png!small)

在JSONObject类中进行格式解析和特殊字符检测。继续跟进处理的过程，当获取到@type传入的类名后，会通过checkAutoType方法检查@type传入的类是否在黑名单中，如果黑名单中存在此类名，直接抛出异常退出程序。如下图：

![](https://image.3001.net/images/20200304/1583294066_5e5f267273f56.png!small)

继续跟进，payload中的json格式数据会在JSONScanner类中进行字段名匹配，如果字段名匹配成功，则将对应的参数值传入，为对应属性赋值，代码如下图：

![](https://image.3001.net/images/20200304/1583294074_5e5f267a19308.png!small)

进入@type指定的com.ibatis.sqlmap.engine.transaction.jta.JtaTransactionConfig类中，通过setProperties类，为utxName变量赋值。此时utxName的值是从json数据中传入的UserTransaction参数值。

![](https://image.3001.net/images/20200304/1583294082_5e5f2682a2f26.png!small)

当我们在UserTransaction参数中传入恶意地址，经过lookup方法进行访问，服务器就可以远程加载恶意文件。

![](https://image.3001.net/images/20200304/1583294089_5e5f268924253.png!small)

至此漏洞利用过程基本完成。

##  **漏洞复现**

搭建fastjson1.2.66 + ibatis-sqlmap-2.3.4.726漏洞环境，传入精心构造的json数据，让目标服务器加载远程主机上的恶意文件，从而在目标主机上执行任意代码。效果如图：

##
![](https://image.3001.net/images/20200304/1583294095_5e5f268f57cfc.png!small)

##  **影响范围**

目前受影响的fastjson版本：

> **fastjson <=1.2.66**

##  **修复建议**

1\. fastjson默认关闭autotype，如果项目中不需要该功能，可以删除以下代码 ：

    
    
    ParserConfig.getGlobalInstance().setAutoTypeSupport(true);

##  **时间轴**

> 2020/3/3 深信服千里目安全实验室发现并成功利用漏洞，发布漏洞分析文章。

***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

  

